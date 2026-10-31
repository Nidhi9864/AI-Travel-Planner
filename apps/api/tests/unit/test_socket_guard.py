"""The provider socket guard of tests/conftest.py (IMP-101 card criterion 6, specification §13.1).

Nothing here leaves the machine: the resolver under the guard (``_socket.getaddrinfo``) is stubbed,
so a blocked call fails before any lookup and an allowed call is answered with a loopback address.
"""

import _socket
import re
import socket
from collections.abc import Callable, Iterator
from typing import Any

import httpx
import pytest
import respx

# The provider hosts step 9 of IMP-101 requires the guard to refuse.
GEMINI_HOST = "generativelanguage.googleapis.com"
ORS_HOST = "api.openrouteservice.org"
PROVIDER_HOSTS = [GEMINI_HOST, ORS_HOST]


class StubResolver:
    """Stands in for the C resolver; answers every name with one loopback address."""

    def __init__(self, port: int) -> None:
        self.port = port
        self.calls: list[object] = []

    def __call__(self, host: object, *args: Any, **kwargs: Any) -> list[tuple[Any, ...]]:
        self.calls.append(host)
        return [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", ("127.0.0.1", self.port))
        ]


@pytest.fixture
def loopback_listener() -> Iterator[socket.socket]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        yield server


@pytest.fixture
def stub_resolver(
    monkeypatch: pytest.MonkeyPatch, loopback_listener: socket.socket
) -> StubResolver:
    resolver = StubResolver(loopback_listener.getsockname()[1])
    monkeypatch.setattr(_socket, "getaddrinfo", resolver)
    return resolver


def _getaddrinfo(host: str) -> object:
    return socket.getaddrinfo(host, 443)


def _create_connection(host: str) -> object:
    return socket.create_connection((host, 443), timeout=1)


def _socket_connect(host: str) -> object:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect((host, 443))


def _socket_connect_ex(host: str) -> object:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, 443))


def _httpx_get(host: str) -> object:
    return httpx.get(f"https://{host}/", timeout=1)


CONNECT_PATHS: dict[str, Callable[[str], object]] = {
    "getaddrinfo": _getaddrinfo,
    "create_connection": _create_connection,
    "socket.connect": _socket_connect,
    "socket.connect_ex": _socket_connect_ex,
    "httpx": _httpx_get,
}


def test_guard_is_active_and_lists_the_provider_hosts(provider_socket_guard: Any) -> None:
    assert provider_socket_guard.active
    assert set(PROVIDER_HOSTS) <= set(provider_socket_guard.hosts)
    # A network-error fallback (for example the routing estimate) must not swallow the guard.
    assert not issubclass(provider_socket_guard.error, OSError)


@pytest.mark.parametrize("path", CONNECT_PATHS.values(), ids=CONNECT_PATHS.keys())
@pytest.mark.parametrize("host", PROVIDER_HOSTS)
def test_unmarked_test_cannot_reach_a_provider_host(
    provider_socket_guard: Any,
    stub_resolver: StubResolver,
    host: str,
    path: Callable[[str], object],
) -> None:
    with pytest.raises(provider_socket_guard.error, match=re.escape(host)) as caught:
        path(host)
    assert "socket guard" in str(caught.value)
    assert stub_resolver.calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("host", PROVIDER_HOSTS)
async def test_unmarked_async_client_cannot_reach_a_provider_host(
    provider_socket_guard: Any, stub_resolver: StubResolver, host: str
) -> None:
    async with httpx.AsyncClient(timeout=1) as client:
        with pytest.raises(provider_socket_guard.error, match=re.escape(host)):
            await client.get(f"https://{host}/")
    assert stub_resolver.calls == []


@pytest.mark.parametrize("host", [GEMINI_HOST.upper(), f"{ORS_HOST}."])
def test_guard_ignores_case_and_a_trailing_dot(
    provider_socket_guard: Any, stub_resolver: StubResolver, host: str
) -> None:
    with pytest.raises(provider_socket_guard.error):
        socket.getaddrinfo(host, 443)
    assert stub_resolver.calls == []


def test_guard_lets_other_hosts_resolve(stub_resolver: StubResolver) -> None:
    socket.getaddrinfo("localhost", 443)
    assert stub_resolver.calls == ["localhost"]


def test_mocked_http_to_a_provider_host_is_not_blocked() -> None:
    with respx.mock(assert_all_called=True) as router:
        router.get(f"https://{ORS_HOST}/v2/directions").mock(return_value=httpx.Response(200))
        assert httpx.get(f"https://{ORS_HOST}/v2/directions").status_code == 200


def test_wildcard_pattern_matches_the_domain_and_its_subdomains(
    provider_socket_guard: Any,
) -> None:
    match = provider_socket_guard.match
    assert match("en.wikipedia.org", ["*.wikipedia.org"]) == "*.wikipedia.org"
    assert match("wikipedia.org", ["*.wikipedia.org"]) == "*.wikipedia.org"
    assert match("notwikipedia.org", ["*.wikipedia.org"]) is None
    assert match(f"x.{GEMINI_HOST}", [GEMINI_HOST]) is None
    assert match(GEMINI_HOST.encode(), [GEMINI_HOST]) == GEMINI_HOST
    assert match(None, [GEMINI_HOST]) is None


# Marked live only to show the guard steps aside; the stubbed resolver sends the connection to a
# loopback listener, so this runs offline under make test-unit (make live-smoke selects
# tests/contract only).
@pytest.mark.live
@pytest.mark.parametrize("host", PROVIDER_HOSTS)
def test_live_test_is_not_blocked_by_the_guard(
    provider_socket_guard: Any,
    stub_resolver: StubResolver,
    loopback_listener: socket.socket,
    host: str,
) -> None:
    assert not provider_socket_guard.active
    with socket.create_connection((host, 443), timeout=1) as conn:
        assert conn.getpeername() == loopback_listener.getsockname()
    assert stub_resolver.calls == [host]
