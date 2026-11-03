"""JSON request logging and redaction (IMP-201; TC-292, TC-293, TC-358; FR-125, NFR-013)."""

import io
import json
import logging
import uuid
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.types import Receive, Scope, Send

from app.core.config import Settings
from app.core.logging import REDACTED, configure_logging, redact_text
from app.core.request_id import RequestIdMiddleware, user_hash
from app.main import create_app

EMAIL = "traveller.private@example.test"
FAKE_KEY = "fake-key-0123456789-not-real"


@pytest.fixture
def log_output() -> Iterator[io.StringIO]:
    """The JSON handler writing to a buffer; the root and uvicorn loggers are restored after."""
    root = logging.getLogger()
    saved = (root.handlers[:], root.level, logging.getLogger("uvicorn.access").disabled)
    buffer = io.StringIO()
    configure_logging("INFO", stream=buffer)
    yield buffer
    root.handlers[:], root.level = saved[0], saved[1]
    logging.getLogger("uvicorn.access").disabled = saved[2]


def lines(buffer: io.StringIO) -> list[dict[str, Any]]:
    return [json.loads(line) for line in buffer.getvalue().splitlines()]


@pytest.fixture
def client(clean_settings_env: pytest.MonkeyPatch) -> TestClient:
    settings = Settings(
        app_env="test",
        ai_provider="MOCK",
        database_url="postgresql+psycopg://unused:unused@127.0.0.1:9/unused",
        supabase_jwt_secret="logging-test-jwt-secret-not-real",  # noqa: S106  # fake
    )
    return TestClient(create_app(settings))


# TC-292: one access line per request, with request_id and latency_ms.
def test_logging_one_access_line_per_request(client: TestClient, log_output: io.StringIO) -> None:
    request_id = str(uuid.uuid4())
    client.get("/health", headers={"X-Request-ID": request_id})

    access = [line for line in lines(log_output) if line["logger"] == "app.access"]
    assert len(access) == 1
    line = access[0]
    assert line["request_id"] == request_id
    assert isinstance(line["latency_ms"], int | float)
    assert line["latency_ms"] >= 0
    assert (line["method"], line["route"], line["status"]) == ("GET", "/health", 200)
    assert line["user_hash"] is None
    assert {"timestamp", "level", "message"} <= set(line)


def test_logging_access_line_names_the_route_template_not_the_path(
    client: TestClient, log_output: io.StringIO
) -> None:
    trip_id = str(uuid.uuid4())
    client.get(f"/api/v1/trips/{trip_id}")  # 401: no token
    (line,) = [line for line in lines(log_output) if line["logger"] == "app.access"]
    assert line["route"] == "/api/v1/trips/{trip_id}"
    assert line["status"] == 401
    assert trip_id not in json.dumps(line)


def test_logging_access_line_carries_the_user_hash_when_the_user_is_known(
    log_output: io.StringIO,
) -> None:
    user_id = uuid.uuid4()

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        scope["state"]["user_id"] = user_id
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    TestClient(RequestIdMiddleware(app)).get("/anything")
    (line,) = [line for line in lines(log_output) if line["logger"] == "app.access"]
    assert line["user_hash"] == user_hash(user_id)
    assert len(line["user_hash"]) == 12
    assert str(user_id) not in log_output.getvalue()


# TC-293, TC-358: a request with an e-mail and a fake key leaves neither in the log output.
def test_logging_request_with_email_and_key_leaves_neither_in_the_log(
    client: TestClient, log_output: io.StringIO
) -> None:
    client.get(
        f"/health?email={EMAIL}&api_key={FAKE_KEY}",
        headers={"Authorization": f"Bearer {FAKE_KEY}", "X-Api-Key": FAKE_KEY},
    )
    client.get(f"/api/v1/me?email={EMAIL}", headers={"Authorization": f"Bearer {FAKE_KEY}"})

    output = log_output.getvalue()
    assert len([line for line in lines(log_output) if line["logger"] == "app.access"]) == 2
    assert EMAIL not in output
    assert FAKE_KEY not in output


def test_logging_filter_redacts_messages_extras_and_exceptions(log_output: io.StringIO) -> None:
    logger = logging.getLogger("app.test_logging")
    logger.warning(
        "call for %s with Authorization: Bearer %s and api_key=%s",
        EMAIL,
        FAKE_KEY,
        FAKE_KEY,
        extra={
            "prompt": "SYSTEM: plan a trip for the traveller",
            "notes": "my phone is private",
            "user_text": "hello",
            "system_text": "you are a planner",
            "gemini_api_key": FAKE_KEY,
            "refresh_token": FAKE_KEY,
            "db_password": FAKE_KEY,
            "client_secret": FAKE_KEY,
            "contact": f"write to {EMAIL}",
        },
    )
    try:
        raise ValueError(f"lookup failed for {EMAIL}")
    except ValueError:
        logger.exception("unhandled error")

    output = log_output.getvalue()
    for leaked in (EMAIL, FAKE_KEY, "plan a trip", "my phone", "you are a planner"):
        assert leaked not in output
    first, second = lines(log_output)
    assert first["message"].startswith(f"call for {REDACTED} with Authorization: Bearer ")
    assert REDACTED in second["exception"]
    assert "ValueError" in second["exception"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (f"user {EMAIL} signed in", f"user {REDACTED} signed in"),
        (f'{{"token": "{FAKE_KEY}"}}', f'{{"token": "{REDACTED}"}}'),
        (f"GEMINI_API_KEY={FAKE_KEY}", f"GEMINI_API_KEY={REDACTED}"),
        (f"authorization: Bearer {FAKE_KEY}", f"authorization: Bearer {REDACTED}"),
        # A start-up message that names a variable without a value stays readable (FR-124).
        ("GEMINI_API_KEY: required in staging", "GEMINI_API_KEY: required in staging"),
    ],
)
def test_logging_redact_text(text: str, expected: str) -> None:
    assert redact_text(text) == expected


def test_logging_level_comes_from_the_setting(log_output: io.StringIO) -> None:
    configure_logging("WARNING", stream=log_output)
    logging.getLogger("app.test_logging").info("hidden")
    logging.getLogger("app.test_logging").warning("shown")
    assert [line["message"] for line in lines(log_output)] == ["shown"]
    assert (
        len(logging.getLogger().handlers)
        == len([h for h in logging.getLogger().handlers if h.get_name() != "app-json"]) + 1
    )  # replaced, not added twice
