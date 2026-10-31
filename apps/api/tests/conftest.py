"""Shared pytest configuration: the provider socket guard (specification §13.1) and settings.

Tests never reach a provider. Unless a test is marked ``live``, any attempt to resolve or connect
to a host in ``PROVIDER_HOSTS`` raises ``ProviderNetworkBlockedError``. Mocked HTTP (respx) and
recorded responses never open a socket, so they are not affected.

The cached settings are cleared around every test, and ``clean_settings_env`` removes every
backend variable from the environment, so a test sees only the values it sets.
"""

import socket
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any

import pytest
from fixtures.auth import api_app, api_client, auth_user  # noqa: F401  # registers the auth fixtures
from fixtures.db import db_session, migrated_database_url  # noqa: F401  # registers the DB fixtures

from app.core.config import Settings, get_settings

# Provider API hosts the guard refuses. A pattern "*.example.org" matches example.org and every
# subdomain. Extension cards add their hosts here (§13.1: api.open-meteo.com, *.wikipedia.org,
# *.wikivoyage.org).
PROVIDER_HOSTS: tuple[str, ...] = (
    "generativelanguage.googleapis.com",  # Gemini API (google-genai)
    "api.openrouteservice.org",  # OpenRouteService
)


class ProviderNetworkBlockedError(RuntimeError):
    """Raised when a test that is not marked ``live`` tries to reach a provider host.

    Not an ``OSError``: client code that falls back on network errors must not swallow it.
    """


def match_provider_host(host: object, patterns: Iterable[str] = PROVIDER_HOSTS) -> str | None:
    """Return the pattern in ``patterns`` that ``host`` matches, or None."""
    if isinstance(host, bytes):
        host = host.decode("ascii", "replace")
    if not isinstance(host, str):
        return None
    name = host.strip().rstrip(".").lower()
    for pattern in patterns:
        if pattern.startswith("*."):
            domain = pattern[2:]
            if name == domain or name.endswith("." + domain):
                return pattern
        elif name == pattern:
            return pattern
    return None


@dataclass(frozen=True)
class ProviderSocketGuard:
    """What the guard fixture yields, so tests can inspect it without importing this module."""

    active: bool
    hosts: tuple[str, ...]
    error: type[ProviderNetworkBlockedError]
    match: Callable[..., str | None]


def _refuse_provider_host(host: object, nodeid: str) -> None:
    pattern = match_provider_host(host)
    if pattern is not None:
        raise ProviderNetworkBlockedError(
            f"socket guard: {nodeid} tried to reach provider host {host!r} (matches {pattern!r}). "
            "Use the MOCK provider, recorded responses or respx, or mark the test 'live' "
            "(run only by make live-smoke)."
        )


@pytest.fixture(autouse=True)
def provider_socket_guard(request: pytest.FixtureRequest) -> Iterator[ProviderSocketGuard]:
    """Block provider hosts for every test that is not marked ``live``."""
    live = request.node.get_closest_marker("live") is not None
    guard = ProviderSocketGuard(
        active=not live,
        hosts=PROVIDER_HOSTS,
        error=ProviderNetworkBlockedError,
        match=match_provider_host,
    )
    if live:
        yield guard
        return

    nodeid = request.node.nodeid
    real_getaddrinfo = socket.getaddrinfo
    real_connect = socket.socket.connect
    real_connect_ex = socket.socket.connect_ex

    # Name resolution: covers socket.create_connection, httpx/httpcore and asyncio, which all
    # resolve the host name through socket.getaddrinfo before connecting.
    def guarded_getaddrinfo(host: Any, *args: Any, **kwargs: Any) -> Any:
        _refuse_provider_host(host, nodeid)
        return real_getaddrinfo(host, *args, **kwargs)

    # A host name passed straight to connect() is resolved inside the C socket module.
    def guarded_connect(self: socket.socket, address: Any) -> None:
        if isinstance(address, tuple) and address:
            _refuse_provider_host(address[0], nodeid)
        real_connect(self, address)

    def guarded_connect_ex(self: socket.socket, address: Any) -> int:
        if isinstance(address, tuple) and address:
            _refuse_provider_host(address[0], nodeid)
        return real_connect_ex(self, address)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
        patch.setattr(socket.socket, "connect", guarded_connect)
        patch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
        yield guard


@pytest.fixture(autouse=True)
def reset_settings_cache() -> Iterator[None]:
    """Let each test read the settings afresh."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def clean_settings_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """Remove every backend variable (and GOOGLE_API_KEY) and stop reading ``.env``.

    Returns the monkeypatch, so the test sets only the variables it needs with ``setenv``.
    """
    for name in [*Settings.model_fields, "google_api_key"]:
        monkeypatch.delenv(name.upper(), raising=False)
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    return monkeypatch
