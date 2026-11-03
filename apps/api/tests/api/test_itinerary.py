"""API-24 and API-09, reading the saved itinerary (§6.6.5; IMP-211: US-153 AC1, FR-005 AC2, TC-064;
FR-059; Amendment A1 §7.1).

A's plan is made through API-07, API-14 and API-22 with the MOCK provider; the submitted job runs on
the test's rolled-back session, as in test_generations.py. No provider host is reached.
"""

import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fixtures.auth import AuthUser
from fixtures.db import insert_auth_user
from sqlalchemy import event, select, update
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from app.ai.factory import get_model_provider
from app.ai.providers.base import ModelProvider
from app.ai.providers.mock import MockProvider
from app.db.models import Destination, ItineraryDay, ItineraryItem, ItineraryVersion
from app.generation import jobs
from app.places import seed

SAMPLETON = Path(__file__).resolve().parents[4] / "data" / "fixtures" / "sampleton"

Generate = Callable[[AuthUser], Any]


@pytest_asyncio.fixture
async def destination(db_session: AsyncSession) -> Destination:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    row = await db_session.scalar(select(Destination).where(Destination.slug == "sampleton"))
    assert row is not None
    return row


async def make_user(session: AsyncSession) -> AuthUser:
    user_id = uuid.uuid4()
    await insert_auth_user(session, user_id)
    return AuthUser(user_id=user_id, email=f"{user_id}@example.test")


@pytest.fixture
def jobs_queue(api_app: FastAPI) -> list[tuple[uuid.UUID, ModelProvider]]:
    queue: list[tuple[uuid.UUID, ModelProvider]] = []
    api_app.dependency_overrides[jobs.get_submit] = lambda: lambda g, p: queue.append((g, p))
    api_app.dependency_overrides[get_model_provider] = lambda: MockProvider("ok", app_env="test")
    return queue


async def create_trip(client: httpx.AsyncClient, user: AuthUser, destination: Destination) -> str:
    created = await client.post(
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
    assert created.status_code == 201, created.text
    trip_id: str = created.json()["id"]
    saved = await client.put(
        f"/api/v1/trips/{trip_id}/preferences",
        json={"interests": ["museum", "food"], "must_visit_place_ids": []},
        headers=user.headers,
    )
    assert saved.status_code == 200, saved.text
    return trip_id


async def generate(
    client: httpx.AsyncClient,
    session: AsyncSession,
    queue: list[tuple[uuid.UUID, ModelProvider]],
    user: AuthUser,
    trip_id: str,
) -> dict[str, Any]:
    """Start API-22, run the captured job, and return the completed generation (API-23)."""
    started = await client.post(
        f"/api/v1/trips/{trip_id}/generations", json={"mode": "ai"}, headers=user.headers
    )
    assert started.status_code == 202, started.text

    @asynccontextmanager
    async def job_transaction() -> AsyncIterator[AsyncSession]:
        async with session.begin_nested():
            yield session

    while queue:
        await jobs.run(*queue.pop(0), job_transaction)
    done = await client.get(f"/api/v1/generations/{started.json()['id']}", headers=user.headers)
    body: dict[str, Any] = done.json()
    assert body["status"] == "completed", done.text
    return body


def item_selects(session: AsyncSession) -> list[str]:
    """Collects the SQL of every statement that reads itinerary_items on this session."""
    statements: list[str] = []
    assert isinstance(session.bind, AsyncConnection)  # db_session is bound to one connection
    connection = session.bind.sync_connection

    @event.listens_for(connection, "before_cursor_execute")
    def record(*args: Any) -> None:
        statement = str(args[2])
        if statement.lstrip().lower().startswith("select") and "itinerary_items" in statement:
            statements.append(statement)

    return statements


# US-153 AC1, TC-064, FR-059


@pytest.mark.asyncio
async def test_us_153_the_saved_plan_is_returned_in_order(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    destination: Destination,
    jobs_queue: list[tuple[uuid.UUID, ModelProvider]],
) -> None:
    trip_id = await create_trip(api_client, auth_user, destination)
    generation = await generate(api_client, db_session, jobs_queue, auth_user, trip_id)
    selects = item_selects(db_session)

    response = await api_client.get(f"/api/v1/trips/{trip_id}/itinerary", headers=auth_user.headers)

    assert response.status_code == 200, response.text
    body = response.json()
    assert len(selects) == 1  # every item in one query, not one per day
    assert body["trip_id"] == trip_id
    assert body["plan_revision"] == generation["plan_revision"] == 1
    assert body["version_id"] == generation["itinerary_version_id"]
    assert (body["is_current"], body["plan_stale"], body["findings"]) == (True, False, [])
    assert body["source"] == {
        "generation_id": generation["id"],
        "provider": "MOCK",
        "outcome": "model",
    }

    # Days and items in the stored order, as saved by the generation.
    stored = (
        await db_session.execute(
            select(ItineraryDay.day_number, ItineraryItem.id)
            .join(ItineraryItem, ItineraryItem.day_id == ItineraryDay.id)
            .where(ItineraryDay.trip_id == uuid.UUID(trip_id))
            .order_by(ItineraryDay.day_number, ItineraryItem.position)
        )
    ).all()
    assert [d["day_number"] for d in body["days"]] == [1, 2, 3]
    assert [d["date"] for d in body["days"]] == ["2026-12-04", "2026-12-05", "2026-12-06"]
    returned = [(d["day_number"], i["id"]) for d in body["days"] for i in d["items"]]
    assert returned == [(day, str(item_id)) for day, item_id in stored]

    items = [item for day in body["days"] for item in day["items"]]
    for day in body["days"]:
        assert [i["position"] for i in day["items"]] == list(range(1, len(day["items"]) + 1))
        assert day["theme_origin"] == ("ai" if day["theme"] else "none")
        assert day["day_cost"] == {
            "min": "0.00",
            "max": "0.00",
            "currency": "GBP",
            "complete": len(day["items"]) == 0,
        }
    for item in items:
        # A1 §7.1: sources is always present and empty until IMP-316.
        assert item["sources"] == []
        assert item["cost"] is None
        assert item["travel_from_previous"] is None
        assert item["origin"] == "model"
        assert item["must_visit"] is False
        start = datetime.strptime(item["start_time"], "%H:%M")
        end = start + timedelta(minutes=item["duration_min"])
        assert item["end_time"] == end.strftime("%H:%M")
        assert set(item["place"]) == {"id", "name", "category", "lat", "lon", "hours_label"}
    # BF-04: no item has a stored cost yet (IMP-308), so the totals are incomplete.
    assert body["totals"] == {
        "currency": "GBP",
        "estimate": {"min": "0.00", "max": "0.00"},
        "planning_total": "0.00",
        "complete": False,
        "incomplete_count": len(items),
    }


@pytest.mark.asyncio
async def test_a_must_visit_place_in_the_plan_is_flagged(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    destination: Destination,
    jobs_queue: list[tuple[uuid.UUID, ModelProvider]],
) -> None:
    trip_id = await create_trip(api_client, auth_user, destination)
    await generate(api_client, db_session, jobs_queue, auth_user, trip_id)
    url = f"/api/v1/trips/{trip_id}/itinerary"
    first = (await api_client.get(url, headers=auth_user.headers)).json()["days"][0]["items"][0]
    saved = await api_client.put(
        f"/api/v1/trips/{trip_id}/preferences",
        json={"must_visit_place_ids": [first["place"]["id"]]},
        headers=auth_user.headers,
    )
    assert saved.status_code == 200, saved.text

    items = [
        i
        for d in (await api_client.get(url, headers=auth_user.headers)).json()["days"]
        for i in d["items"]
    ]
    flagged = {i["place"]["id"] for i in items if i["must_visit"]}
    assert flagged == {first["place"]["id"]}


# FR-005 AC2, TC-064: no itinerary, another user's trip, a reserved query


@pytest.mark.asyncio
async def test_tc_064_a_trip_without_an_itinerary_answers_404_no_itinerary_yet(
    api_client: httpx.AsyncClient, auth_user: AuthUser, destination: Destination
) -> None:
    trip_id = await create_trip(api_client, auth_user, destination)

    response = await api_client.get(f"/api/v1/trips/{trip_id}/itinerary", headers=auth_user.headers)

    assert response.status_code == 404
    error = response.json()["error"]
    assert (error["code"], error["message"], error["details"]) == (
        "NOT_FOUND",
        "No itinerary yet.",
        [],
    )
    assert error["request_id"]


@pytest.mark.asyncio
async def test_tc_064_another_users_itinerary_answers_like_a_missing_trip(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    destination: Destination,
    jobs_queue: list[tuple[uuid.UUID, ModelProvider]],
) -> None:
    trip_id = await create_trip(api_client, auth_user, destination)
    await generate(api_client, db_session, jobs_queue, auth_user, trip_id)
    other = await make_user(db_session)

    foreign = await api_client.get(f"/api/v1/trips/{trip_id}/itinerary", headers=other.headers)
    missing = await api_client.get(f"/api/v1/trips/{uuid.uuid4()}/itinerary", headers=other.headers)

    assert foreign.status_code == missing.status_code == 404
    strip = [{**r.json()["error"], "request_id": None} for r in (foreign, missing)]
    assert strip[0] == strip[1]
    assert strip[0]["message"] == "Not found."  # never says whether a plan exists
    assert trip_id not in foreign.text


@pytest.mark.asyncio
async def test_reading_a_stored_version_is_not_built_yet(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    destination: Destination,
    jobs_queue: list[tuple[uuid.UUID, ModelProvider]],
) -> None:
    trip_id = await create_trip(api_client, auth_user, destination)
    generation = await generate(api_client, db_session, jobs_queue, auth_user, trip_id)

    response = await api_client.get(
        f"/api/v1/trips/{trip_id}/itinerary",
        params={"version_id": generation["itinerary_version_id"]},
        headers=auth_user.headers,
    )

    # IMD-37: version_id is reserved for IMP-610.
    assert response.status_code == 501
    assert response.json()["error"]["code"] == "NOT_IMPLEMENTED"


# API-09


@pytest.mark.asyncio
async def test_latest_is_null_when_the_caller_has_no_itinerary(
    api_client: httpx.AsyncClient, auth_user: AuthUser, destination: Destination
) -> None:
    await create_trip(api_client, auth_user, destination)  # a trip, but no plan

    response = await api_client.get("/api/v1/itineraries/latest", headers=auth_user.headers)

    assert response.status_code == 200
    assert response.json() == {"trip_id": None, "plan_revision": None, "updated_at": None}


@pytest.mark.asyncio
async def test_latest_returns_the_callers_most_recently_changed_itinerary_only(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    destination: Destination,
    jobs_queue: list[tuple[uuid.UUID, ModelProvider]],
) -> None:
    older = await create_trip(api_client, auth_user, destination)
    newer = await create_trip(api_client, auth_user, destination)
    await generate(api_client, db_session, jobs_queue, auth_user, older)
    await generate(api_client, db_session, jobs_queue, auth_user, newer)
    other = await make_user(db_session)
    foreign = await create_trip(api_client, other, destination)
    await generate(api_client, db_session, jobs_queue, other, foreign)
    # now() is fixed within the test's transaction: date the versions apart explicitly.
    for trip_id, age in ((older, 2), (newer, 1), (foreign, 0)):
        await db_session.execute(
            update(ItineraryVersion)
            .where(ItineraryVersion.trip_id == uuid.UUID(trip_id))
            .values(created_at=datetime(2026, 11, 3, 12) - timedelta(hours=age))
        )

    response = await api_client.get("/api/v1/itineraries/latest", headers=auth_user.headers)

    assert response.status_code == 200
    assert response.json() == {
        "trip_id": newer,
        "plan_revision": 1,
        "updated_at": "2026-11-03T11:00:00Z",
    }
