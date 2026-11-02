"""API-01 GET /health, the 404 envelope and CORS (IMP-103; TC-288, TC-044, TC-351)."""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

ALLOWED_ORIGIN = "http://localhost:3000"
# Fake values: the test asserts that none of them is returned.
SECRETS = {
    "database_url": "postgresql+psycopg://health-user:health-db-secret@db.invalid/app",
    "gemini_api_key": "health-test-gemini-key-not-real",
    "supabase_jwt_secret": "health-test-jwt-secret-not-real",
    "ors_api_key": "health-test-ors-key-not-real",
}


@pytest.fixture
def client(clean_settings_env: pytest.MonkeyPatch) -> TestClient:
    settings = Settings(
        app_env="test",
        ai_provider="MOCK",
        build_version="test-build",
        allowed_origins=[ALLOWED_ORIGIN],
        **SECRETS,
    )
    return TestClient(create_app(settings))


# TC-288, TC-044: 200 with exactly the four fields and no secret.
def test_health_returns_status_version_environment_provider(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "test-build",
        "environment": "test",
        "provider": "MOCK",
    }
    for secret in SECRETS.values():
        assert secret not in response.text
        assert all(secret not in value for value in response.headers.values())


def test_health_is_outside_api_v1(client: TestClient) -> None:
    assert client.get("/api/v1/health").status_code == 404


def test_health_has_a_request_id(client: TestClient) -> None:
    response = client.get("/health")
    assert uuid.UUID(response.headers["X-Request-ID"])


def test_health_echoes_a_client_request_id(client: TestClient) -> None:
    request_id = str(uuid.uuid4())
    response = client.get("/health", headers={"X-Request-ID": request_id})
    assert response.headers["X-Request-ID"] == request_id


def test_health_replaces_a_request_id_that_is_not_a_uuid(client: TestClient) -> None:
    response = client.get("/health", headers={"X-Request-ID": "not-a-uuid"})
    assert response.headers["X-Request-ID"] != "not-a-uuid"
    assert uuid.UUID(response.headers["X-Request-ID"])


# Card step 7: an unknown route returns the 404 envelope with the request ID.
def test_health_unknown_route_returns_not_found_envelope(client: TestClient) -> None:
    response = client.get("/no-such-route")
    assert response.status_code == 404
    body = response.json()
    assert set(body) == {"error"}
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["details"] == []
    assert body["error"]["retry_after_s"] is None
    assert body["error"]["request_id"] == response.headers["X-Request-ID"]
    assert uuid.UUID(body["error"]["request_id"])


def test_health_unknown_api_v1_route_returns_not_found_envelope(client: TestClient) -> None:
    request_id = str(uuid.uuid4())
    response = client.get("/api/v1/no-such-route", headers={"X-Request-ID": request_id})
    assert response.status_code == 404
    assert response.json()["error"]["request_id"] == request_id


# TC-351: only the exact configured origin gets a CORS allow header.
def test_health_cors_allows_the_configured_origin(client: TestClient) -> None:
    response = client.get("/health", headers={"Origin": ALLOWED_ORIGIN})
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


@pytest.mark.parametrize(
    "origin",
    ["https://evil.example", "http://localhost:3001", "http://localhost:3000.evil.example"],
)
def test_health_cors_refuses_other_origins(client: TestClient, origin: str) -> None:
    response = client.get("/health", headers={"Origin": origin})
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers

    preflight = client.options(
        "/health", headers={"Origin": origin, "Access-Control-Request-Method": "GET"}
    )
    assert "access-control-allow-origin" not in preflight.headers


def test_health_docs_are_served_outside_production(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200


def test_health_docs_are_disabled_in_production(clean_settings_env: pytest.MonkeyPatch) -> None:
    settings = Settings(
        app_env="production",
        ai_provider="GEMINI",
        gemini_api_key="health-test-gemini-key-not-real",
        gemini_model_id="test-model-id",
        database_url=SECRETS["database_url"],
    )
    production = TestClient(create_app(settings))
    assert production.get("/docs").status_code == 404
    assert production.get("/openapi.json").status_code == 404
    assert production.get("/health").json()["environment"] == "production"
