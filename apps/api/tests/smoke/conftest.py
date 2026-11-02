"""Options for the deployed smoke tests (IMP-112), run only by make smoke URL=<base url>.

The normal test targets name their own directories (tests/unit, tests/contract, tests/api,
tests/authz), so they never collect this one. Without --base-url the smoke tests skip; without
--web-origin the allowed-origin check skips.
"""

from collections.abc import Iterator

import httpx
import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Base URL of a running API, for example http://localhost:8000 (make smoke URL=...)",
    )
    parser.addoption(
        "--web-origin",
        action="store",
        default=None,
        help="The web origin the API allows (its ALLOWED_ORIGINS); checked only when given",
    )


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest) -> str:
    url = request.config.getoption("--base-url", default=None)
    if not url:
        pytest.skip("smoke tests need --base-url (make smoke URL=<base url>)")
    return str(url).rstrip("/")


@pytest.fixture(scope="session")
def web_origin(request: pytest.FixtureRequest) -> str:
    origin = request.config.getoption("--web-origin", default=None)
    if not origin:
        pytest.skip("allowed-origin check needs --web-origin (make smoke ARGS='--web-origin ...')")
    return str(origin).rstrip("/")


@pytest.fixture(scope="session")
def smoke_client(base_url: str) -> Iterator[httpx.Client]:
    # A deployed service may be waking from idle (NFR-005), so allow a long first response.
    with httpx.Client(base_url=base_url, timeout=httpx.Timeout(90.0, connect=30.0)) as client:
        yield client
