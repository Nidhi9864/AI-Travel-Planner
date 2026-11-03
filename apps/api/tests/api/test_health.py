"""API-01 GET /health, the 404 envelope and CORS (IMP-103; TC-288, TC-044, TC-351).

API-02 GET /health/ready against the migrated test database and a closed port (IMP-201; TC-289).
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient

from app.ai.factory import get_provider
from app.core import health
from app.core.config import Settings
from app.main import create_app
from app.schemas.ai import HealthStatus

MIGRATIONS = Path(__file__).resolve().parents[2] / "migrations"
CLOSED_PORT_URL = "postgresql+psycopg://ready-user:ready-db-secret@127.0.0.1:9/nowhere"

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


# ---------- API-02 GET /health/ready (IMP-201) ----------


def ready_client(database_url: str, **overrides: Any) -> TestClient:
    values: dict[str, Any] = {
        "app_env": "test",
        "ai_provider": "MOCK",
        "build_version": "test-build",
        "database_url": database_url,
        **overrides,
    }
    return TestClient(create_app(Settings(**values)))


def test_health_ready_migration_head_matches_the_migrations() -> None:
    # The image has no migrations folder, so the head is a constant; a new migration updates it.
    head = ScriptDirectory(str(MIGRATIONS)).get_current_head()
    assert head == health.MIGRATION_HEAD


def test_health_ready_with_a_migrated_database(
    clean_settings_env: pytest.MonkeyPatch, migrated_database_url: str
) -> None:
    client = ready_client(migrated_database_url)
    response = client.get("/health/ready")
    assert response.status_code == 200
    model_id = get_provider(client.app.state.settings).get_model_metadata().model_id
    assert response.json() == {
        "status": "ready",
        "version": "test-build",
        "checks": {
            "database": "ok",
            "migration": health.MIGRATION_HEAD,
            "provider": {"name": "MOCK", "model_id": model_id, "status": "ok"},
        },
    }


# TC-289: the database unreachable -> 503 not_ready naming the database; no secret in the body.
def test_health_ready_database_down_is_503_not_ready(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    response = ready_client(CLOSED_PORT_URL).get("/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["database"] == "down"
    assert body["checks"]["migration"] == "behind"
    assert body["checks"]["provider"]["status"] == "ok"
    assert "ready-db-secret" not in response.text
    assert "127.0.0.1" not in response.text


# PD-12, FR-044 AC2: a provider that is down degrades readiness but is not a 503.
def test_health_ready_provider_down_is_200_degraded(
    clean_settings_env: pytest.MonkeyPatch, migrated_database_url: str
) -> None:
    client = ready_client(migrated_database_url, ai_provider="GEMINI", gemini_model_id="m-test")
    response = client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["provider"] == {"name": "GEMINI", "model_id": "m-test", "status": "down"}


def test_health_ready_database_behind_the_head_is_degraded(
    clean_settings_env: pytest.MonkeyPatch, migrated_database_url: str
) -> None:
    clean_settings_env.setattr(health, "MIGRATION_HEAD", "9999")
    response = ready_client(migrated_database_url).get("/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["checks"]["migration"] == "behind"


def test_health_ready_caches_the_provider_check(
    clean_settings_env: pytest.MonkeyPatch, migrated_database_url: str
) -> None:
    client = ready_client(migrated_database_url)
    provider = get_provider(client.app.state.settings)
    calls = []

    async def counting_health_check() -> HealthStatus:
        calls.append(1)
        return HealthStatus(status="ok", detail=None, checked_at=datetime.now(UTC))

    clean_settings_env.setattr(provider, "health_check", counting_health_check)
    client.app.state.model_provider = provider
    for _ in range(3):
        assert client.get("/health/ready").status_code == 200
    assert len(calls) == 1  # cached for PROVIDER_CACHE_S


# TC-342: readiness answers carry the request ID, and a client UUID is echoed.
def test_health_ready_echoes_a_client_request_id(clean_settings_env: pytest.MonkeyPatch) -> None:
    request_id = str(uuid.uuid4())
    response = ready_client(CLOSED_PORT_URL).get(
        "/health/ready", headers={"X-Request-ID": request_id}
    )
    assert response.headers["X-Request-ID"] == request_id
