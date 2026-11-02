"""Smoke checks against a deployed API (IMP-112; TC-288, TC-351).

GET /health answers 200 with the provider name (API-01, FR-123); GET /health/ready is checked only
when the deployment has it (IMP-201); a CORS preflight from a foreign origin gets no allow header
(NFR-015), while the web origin given with --web-origin is allowed (US-002 AC2). Read-only: no
account, no database write and no provider call.
"""

import httpx

FOREIGN_ORIGIN = "https://smoke-foreign-origin.invalid"


def test_health_returns_200_with_provider(smoke_client: httpx.Client) -> None:
    response = smoke_client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["provider"] in {"GEMINI", "MOCK", "FINETUNED_MODEL"}
    assert body["environment"] in {"local", "test", "staging", "production"}


def test_health_ready_when_present(smoke_client: httpx.Client) -> None:
    response = smoke_client.get("/health/ready")

    # /health/ready arrives with IMP-201; until then a 404 means "not present", not a failure.
    if response.status_code == 404:
        return
    assert response.status_code == 200


def test_foreign_origin_gets_no_cors_allow_header(smoke_client: httpx.Client) -> None:
    response = smoke_client.options(
        "/health",
        headers={"Origin": FOREIGN_ORIGIN, "Access-Control-Request-Method": "GET"},
    )

    assert "access-control-allow-origin" not in response.headers


def test_foreign_origin_simple_request_gets_no_cors_allow_header(
    smoke_client: httpx.Client,
) -> None:
    response = smoke_client.get("/health", headers={"Origin": FOREIGN_ORIGIN})

    assert "access-control-allow-origin" not in response.headers


def test_web_origin_gets_cors_allow_header(smoke_client: httpx.Client, web_origin: str) -> None:
    response = smoke_client.options(
        "/health",
        headers={"Origin": web_origin, "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == web_origin
