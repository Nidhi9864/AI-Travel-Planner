"""API-22 and API-23, the walking-skeleton generation job (§6.4, §6.6.4, §8.2; IMP-210: TC-012,
TC-115, TC-151, TC-162; FR-024, FR-025, FR-038, NFR-008).

MOCK provider only; the socket guard of tests/conftest.py blocks every provider host. API-22's
job is captured instead of started, and each test runs it with ``jobs.run`` on its rolled-back
session, so the request and the job never share the session at the same time.
"""

import asyncio
import logging
import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from datetime import timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fixtures.auth import AuthUser
from fixtures.db import insert_auth_user
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_model_provider
from app.ai.providers.base import ModelProvider
from app.ai.providers.mock import MockProvider
from app.core.config import MockScenario
from app.db.models import (
    AiGeneration,
    Destination,
    ItineraryDay,
    ItineraryItem,
    ItineraryVersion,
    Place,
    Trip,
)
from app.generation import jobs, records, repository
from app.places import seed
from app.schemas.ai import GenerationRequest, ItineraryOutput, ProviderResult

REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLETON = REPO_ROOT / "data" / "fixtures" / "sampleton"
NOTES = "We like quiet mornings near the river."
PREFERENCES: dict[str, Any] = {
    "interests": ["museum", "food"],
    "pace": "balanced",
    "budget_priority": "balanced",
    "transport_pref": "walking",
    "accommodation_type": "any",
    "step_free_required": False,
    "notes": NOTES,
}
TERMINAL = ("completed", "failed")

Job = tuple[uuid.UUID, ModelProvider]
Sessions = Callable[[], AbstractAsyncContextManager[AsyncSession]]


@pytest_asyncio.fixture
async def sampleton(db_session: AsyncSession) -> Destination:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    return destination


@pytest.fixture
def submitted(api_app: FastAPI) -> list[Job]:
    """The jobs API-22 submitted, in order, instead of asyncio tasks."""
    queue: list[Job] = []
    api_app.dependency_overrides[jobs.get_submit] = lambda: lambda gid, p: queue.append((gid, p))
    return queue


@pytest.fixture
def sessions(db_session: AsyncSession) -> Sessions:
    """The job's transactions, as savepoints of the test's rolled-back session."""

    @asynccontextmanager
    async def job_transaction() -> AsyncIterator[AsyncSession]:
        async with db_session.begin_nested():
            yield db_session

    return job_transaction


def use_provider(app: FastAPI, scenario: MockScenario) -> None:
    app.dependency_overrides[get_model_provider] = lambda: MockProvider(scenario, app_env="test")


async def create_trip(
    client: httpx.AsyncClient, user: AuthUser, destination: Destination, *, prefs: bool = True
) -> str:
    response = await client.post(
        "/api/v1/trips",
        json={
            "title": "Weekend in Sampleton",
            "destination_id": str(destination.id),
            "start_date": "2026-12-04",
            "end_date": "2026-12-06",
            "adults": 2,
        },
        headers=user.headers,
    )
    assert response.status_code == 201, response.text
    trip_id: str = response.json()["id"]
    if prefs:
        saved = await client.put(
            f"/api/v1/trips/{trip_id}/preferences",
            json={**PREFERENCES, "must_visit_place_ids": []},
            headers=user.headers,
        )
        assert saved.status_code == 200, saved.text
    return trip_id


@pytest_asyncio.fixture
async def trip(api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination) -> str:
    return await create_trip(api_client, auth_user, sampleton)


async def start(
    client: httpx.AsyncClient, user: AuthUser, trip_id: str, **body: Any
) -> httpx.Response:
    return await client.post(
        f"/api/v1/trips/{trip_id}/generations", json=body or {"mode": "ai"}, headers=user.headers
    )


async def poll(
    client: httpx.AsyncClient,
    user: AuthUser,
    generation_id: str,
    queue: list[Job],
    sessions: Sessions,
) -> dict[str, Any]:
    """Poll API-23 until a terminal status, running the submitted jobs between polls."""
    for _ in range(5):
        response = await client.get(f"/api/v1/generations/{generation_id}", headers=user.headers)
        assert response.status_code == 200, response.text
        body: dict[str, Any] = response.json()
        if body["status"] in TERMINAL:
            return body
        while queue:
            await jobs.run(*queue.pop(0), sessions)
    raise AssertionError("generation did not finish")


async def plan_rows(session: AsyncSession, trip_id: str) -> tuple[list[uuid.UUID], int]:
    trip = uuid.UUID(trip_id)
    days = list(await session.scalars(select(ItineraryDay.id).where(ItineraryDay.trip_id == trip)))
    items = await session.scalar(
        select(func.count()).select_from(ItineraryItem).where(ItineraryItem.trip_id == trip)
    )
    return days, int(items or 0)


async def queued_row(
    session: AsyncSession, user: AuthUser, trip_id: str, mode: str = "ai"
) -> uuid.UUID:
    """An active generation inserted directly, as another request for the trip would leave it."""
    return await repository.create_queued(
        session,
        trip_id=uuid.UUID(trip_id),
        user_id=user.user_id,
        provider="MOCK",
        model_id="mock-v1",
        prompt_template_id="itinerary_generate",
        prompt_version="v1",
        mapping_version="pm-1",
        scope="full",
        request_hash=records.request_hash({"trip_id": trip_id, "mode": mode}),
    )


# TC-162, TC-012, TC-151


@pytest.mark.asyncio
async def test_tc_162_mock_generation_completes_and_saves_the_plan(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    sessions: Sessions,
    provider_socket_guard: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    assert provider_socket_guard.active  # any Gemini host lookup would raise

    response = await start(api_client, auth_user, trip)
    assert response.status_code == 202, response.text
    queued = response.json()
    assert (queued["status"], queued["scope"], queued["mode"]) == ("queued", "full", "ai")
    assert queued["itinerary_version_id"] is None

    with caplog.at_level(logging.DEBUG):
        done = await poll(api_client, auth_user, queued["id"], submitted, sessions)

    assert (done["status"], done["outcome"], done["failure_reason"]) == ("completed", "model", None)
    assert done["plan_revision"] == 1
    assert done["latency_ms"] is not None
    assert done["validation_summary"] == {"errors": 0, "warnings": 0, "infos": 0}
    days, items = await plan_rows(db_session, trip)
    assert len(days) == 3
    assert items > 0
    version = await db_session.get(ItineraryVersion, uuid.UUID(done["itinerary_version_id"]))
    assert version is not None
    assert (version.version_no, version.reason, version.plan_revision) == (1, "generation", 1)
    assert version.snapshot["schema"] == "snap-1"
    assert [d["day_number"] for d in version.snapshot["days"]] == [1, 2, 3]
    trip_row = await db_session.get(Trip, uuid.UUID(trip), populate_existing=True)
    assert trip_row is not None
    assert (trip_row.plan_revision, trip_row.status, trip_row.plan_stale) == (1, "ready", False)
    item_rows = list(
        await db_session.scalars(
            select(ItineraryItem).where(ItineraryItem.trip_id == uuid.UUID(trip))
        )
    )
    assert {item.origin for item in item_rows} == {"model"}
    assert all(item.cost_min is None and item.source_chunk_ids == [] for item in item_rows)
    # FR-125 AC2: notes and model text never reach the log.
    assert NOTES not in caplog.text
    assert "SAMPLE note" not in caplog.text


@pytest.mark.asyncio
async def test_tc_012_tc_151_the_record_names_provider_model_template_and_mapping(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    sessions: Sessions,
) -> None:
    generation_id = (await start(api_client, auth_user, trip)).json()["id"]
    done = await poll(api_client, auth_user, generation_id, submitted, sessions)

    assert (done["provider"], done["model_id"], done["prompt_version"]) == ("MOCK", "mock-v1", "v1")
    assert done["retrieval_mode"] is None
    assert done["embedding_model_id"] is None
    assert done["retrieval_ms"] is None
    row = await db_session.get(AiGeneration, uuid.UUID(generation_id), populate_existing=True)
    assert row is not None
    assert (row.provider, row.model_id, row.prompt_template_id, row.prompt_version) == (
        "MOCK",
        "mock-v1",
        "itinerary_generate",
        "v1",
    )
    assert (row.mapping_version, row.adapter_version) == ("pm-1", "mock-1")
    assert row.retrieval_mode is None
    assert row.embedding_model_id is None


# FR-024: idempotency and the in-progress conflict


@pytest.mark.asyncio
async def test_same_request_while_active_returns_the_same_generation(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str, submitted: list[Job]
) -> None:
    first = await start(api_client, auth_user, trip)
    again = await start(api_client, auth_user, trip)

    assert (first.status_code, again.status_code) == (202, 200)
    assert again.json()["id"] == first.json()["id"]
    assert len(submitted) == 1


@pytest.mark.asyncio
async def test_a_different_request_while_active_is_refused(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
) -> None:
    await queued_row(db_session, auth_user, trip, mode="rule_based")

    response = await start(api_client, auth_user, trip)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "GENERATION_IN_PROGRESS"
    assert submitted == []


# TC-115 and the other create rules


@pytest.mark.asyncio
async def test_tc_115_an_incomplete_trip_lists_the_missing_fields(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination, submitted: list[Job]
) -> None:
    trip_id = await create_trip(api_client, auth_user, sampleton, prefs=False)

    response = await start(api_client, auth_user, trip_id)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert [d["field"] for d in error["details"]] == ["preferences"]
    assert submitted == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("body", "field"), [({"mode": "ai", "scope": "day"}, "scope"), ({"mode": "rule_based"}, "mode")]
)
async def test_unknown_fields_and_rule_based_mode_are_refused(
    api_client: httpx.AsyncClient,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    body: dict[str, Any],
    field: str,
) -> None:
    response = await start(api_client, auth_user, trip, **body)

    assert response.status_code == 422
    assert field in [d["field"] for d in response.json()["error"]["details"]]
    assert submitted == []


@pytest.mark.asyncio
async def test_a_trip_with_an_itinerary_is_refused(
    api_client: httpx.AsyncClient,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    sessions: Sessions,
) -> None:
    await poll(
        api_client,
        auth_user,
        (await start(api_client, auth_user, trip)).json()["id"],
        submitted,
        sessions,
    )

    response = await start(api_client, auth_user, trip)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


# NFR-008: a failing job leaves the previous plan as it was


@pytest.mark.asyncio
async def test_a_provider_timeout_fails_and_leaves_the_previous_plan_untouched(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    sessions: Sessions,
) -> None:
    await poll(
        api_client,
        auth_user,
        (await start(api_client, auth_user, trip)).json()["id"],
        submitted,
        sessions,
    )
    before = await plan_rows(db_session, trip)

    # API-22 refuses a trip with a plan, so the second job is started as API-31 will start it.
    generation_id = await queued_row(db_session, auth_user, trip)
    await jobs.run(generation_id, MockProvider("timeout", app_env="test"), sessions)
    failed = await poll(api_client, auth_user, str(generation_id), submitted, sessions)

    # Interim until IMP-403 routes a timeout to the rule-based fallback.
    assert (failed["status"], failed["outcome"]) == ("failed", "failed")
    assert failed["failure_reason"] == "provider_timeout"
    assert failed["next_action"] == "retry_rule_based"
    assert failed["itinerary_version_id"] is None
    assert await plan_rows(db_session, trip) == before
    trip_row = await db_session.get(Trip, uuid.UUID(trip), populate_existing=True)
    assert trip_row is not None
    assert trip_row.plan_revision == 1


@pytest.mark.asyncio
async def test_an_answer_outside_the_shortlist_fails_with_invalid_output(
    api_app: FastAPI,
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    sessions: Sessions,
) -> None:
    use_provider(api_app, "unknown_place")
    generation_id = (await start(api_client, auth_user, trip)).json()["id"]

    failed = await poll(api_client, auth_user, generation_id, submitted, sessions)

    assert (failed["status"], failed["failure_reason"]) == ("failed", "invalid_output")
    assert await plan_rows(db_session, trip) == ([], 0)


class SlowProvider(MockProvider):
    async def generate_itinerary(
        self, request: GenerationRequest
    ) -> ProviderResult[ItineraryOutput]:
        await asyncio.sleep(5)
        return await super().generate_itinerary(request)


@pytest.mark.asyncio
async def test_the_job_timeout_fails_with_internal_and_says_timed_out(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    sessions: Sessions,
    submitted: list[Job],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(jobs, "PIPELINE_TIMEOUT_S", 0.05)
    generation_id = await queued_row(db_session, auth_user, trip)

    await jobs.run(generation_id, SlowProvider("ok", app_env="test"), sessions)
    failed = await poll(api_client, auth_user, str(generation_id), submitted, sessions)

    assert (failed["status"], failed["failure_reason"]) == ("failed", "internal")
    assert (failed["failure_message"], failed["next_action"]) == ("Generation timed out.", "retry")
    assert await plan_rows(db_session, trip) == ([], 0)


@pytest.mark.asyncio
async def test_api_23_reaps_a_stale_active_generation(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
    sessions: Sessions,
) -> None:
    generation_id = await queued_row(db_session, auth_user, trip)
    await db_session.execute(
        update(AiGeneration)
        .where(AiGeneration.id == generation_id)
        .values(created_at=func.now() - jobs.STALE_AFTER - timedelta(seconds=1))
    )

    reaped = await poll(api_client, auth_user, str(generation_id), submitted, sessions)

    assert (reaped["status"], reaped["failure_reason"]) == ("failed", "internal")
    assert reaped["failure_message"] == "Generation timed out."


# Ownership: another user's trip or generation is 404, never 403


@pytest.mark.asyncio
async def test_another_users_trip_and_generation_are_not_found(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    submitted: list[Job],
) -> None:
    other_id = await insert_auth_user(db_session)
    other = AuthUser(user_id=other_id, email=f"{other_id}@example.test")
    generation_id = (await start(api_client, auth_user, trip)).json()["id"]

    started = await start(api_client, other, trip)
    read = await api_client.get(f"/api/v1/generations/{generation_id}", headers=other.headers)
    missing = await api_client.get(f"/api/v1/generations/{uuid.uuid4()}", headers=auth_user.headers)

    for response in (started, read, missing):
        assert response.status_code == 404, response.text
        assert response.json()["error"]["code"] == "NOT_FOUND"
    assert len(submitted) == 1


@pytest.mark.asyncio
async def test_the_request_holds_only_trip_data_and_shortlisted_places(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
    trip: str,
) -> None:
    from app.generation import request_builder

    request = await request_builder.build(
        db_session,
        trip_id=uuid.UUID(trip),
        user_id=auth_user.user_id,
        prompt_template_id="itinerary_generate",
        prompt_version="v1",
    )

    active = list(
        await db_session.scalars(
            select(Place.id)
            .where(Place.destination_id == sampleton.id, Place.is_active.is_(True))
            .order_by(Place.name, Place.id)
            .limit(40)
        )
    )
    assert [p.place_id for p in request.shortlist] == active
    assert request.trip.num_days == 3
    assert request.scope.kind == "full"
    assert request.preferences.notes_quoted == NOTES
    dumped = request.model_dump_json()
    assert auth_user.email not in dumped
    assert str(auth_user.user_id) not in dumped
    assert "Weekend in Sampleton" not in dumped
