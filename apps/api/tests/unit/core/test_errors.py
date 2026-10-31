"""The §6.3 error envelope: domain exceptions, request validation and unexpected errors (IMP-103)."""

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

from app.core import errors
from app.core.config import Settings
from app.main import create_app
from app.schemas.common import ErrorDetail

# HTTP status and code of each domain exception, as in the §6.3 table.
EXPECTED = [
    (errors.Unauthenticated, 401, "UNAUTHENTICATED"),
    (errors.NotFound, 404, "NOT_FOUND"),
    (errors.StalePlan, 409, "STALE_PLAN"),
    (errors.GenerationInProgress, 409, "GENERATION_IN_PROGRESS"),
    (errors.Conflict, 409, "CONFLICT"),
    (errors.ValidationFailed, 422, "VALIDATION_ERROR"),
    (errors.InvalidEdit, 422, "INVALID_EDIT"),
    (errors.RateLimited, 429, "RATE_LIMITED"),
    (errors.QuotaReached, 429, "AI_QUOTA_REACHED"),
    (errors.Internal, 500, "INTERNAL"),
    (errors.EndpointNotImplemented, 501, "NOT_IMPLEMENTED"),
    (errors.ServiceUnavailable, 503, "SERVICE_UNAVAILABLE"),
]


class TripIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    days: int


@pytest.fixture
def app(clean_settings_env: pytest.MonkeyPatch) -> FastAPI:
    settings = Settings(app_env="test", database_url="postgresql+psycopg://u:p@db.invalid/app")
    app = create_app(settings)

    @app.get("/raise/{name}")
    async def raise_domain_error(name: str) -> None:
        raise getattr(errors, name)()

    @app.get("/rate-limited")
    async def rate_limited() -> None:
        raise errors.RateLimited(retry_after_s=30)

    @app.get("/invalid-field")
    async def invalid_field() -> None:
        raise errors.ValidationFailed(
            details=[ErrorDetail(field="end_date", message="End date must be after start date.")]
        )

    @app.post("/trips")
    async def create_trip(trip: TripIn) -> TripIn:
        return trip

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("internal detail with secret-token-not-real")

    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_every_error_code_has_an_exception() -> None:
    assert {code for _, _, code in EXPECTED} == {code.value for code in errors.ErrorCode}


@pytest.mark.parametrize(("error_class", "status", "code"), EXPECTED)
def test_domain_error_maps_to_status_and_code(
    client: TestClient, error_class: type[errors.DomainError], status: int, code: str
) -> None:
    response = client.get(f"/raise/{error_class.__name__}")
    assert response.status_code == status
    body = response.json()["error"]
    assert body["code"] == code
    assert body["message"] == error_class.default_message
    assert body["details"] == []
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_rate_limited_sets_retry_after(client: TestClient) -> None:
    response = client.get("/rate-limited")
    assert response.status_code == 429
    assert response.headers["Retry-After"] == "30"
    assert response.json()["error"]["retry_after_s"] == 30


def test_details_name_fields(client: TestClient) -> None:
    response = client.get("/invalid-field")
    assert response.json()["error"]["details"] == [
        {"field": "end_date", "message": "End date must be after start date."}
    ]


def test_request_validation_maps_to_validation_error(client: TestClient) -> None:
    response = client.post("/trips", json={"days": "many", "user_id": "someone-else"})
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["message"] == "Some fields need attention."
    assert {detail["field"] for detail in body["details"]} == {"title", "days", "user_id"}
    assert "many" not in response.text
    assert "someone-else" not in response.text


def test_unexpected_error_is_internal_without_trace(client: TestClient) -> None:
    request_id = str(uuid.uuid4())
    response = client.get("/boom", headers={"X-Request-ID": request_id})
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL"
    assert body["error"]["request_id"] == request_id
    assert response.headers["X-Request-ID"] == request_id
    assert "Traceback" not in response.text
    assert "RuntimeError" not in response.text
    assert "secret-token-not-real" not in response.text


def test_method_not_allowed_uses_the_envelope(client: TestClient) -> None:
    response = client.delete("/health")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert "GET" in response.headers["Allow"]
