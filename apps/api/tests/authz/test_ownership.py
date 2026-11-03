"""Two-user ownership suite for every implemented owned route (IMP-215; US-013, FR-005, NFR-012:
TC-063, TC-064, TC-065, TC-345, TC-346).

User A owns a trip with preferences and a must-visit place, a completed generation and the saved
itinerary, all built through the API with the MOCK provider: API-22's job is captured and run on
the test's rolled-back session (as in tests/api/test_generations.py), so no provider is reached.
User B then calls every route of tests/authz/route_matrix.py with A's identifiers. A ``foreign``
route answers 404 NOT_FOUND, exactly as for a missing resource; a ``scoped`` route answers with B's
own data. No response to B holds A's data, and after each call A's trip, preferences, generation
and every itinerary row are unchanged. Child resources (the generation, the plan rows) inherit the
trip's ownership (TC-346). Routes that answer 501 are skipped until their cards build them
(IMD-37); ``test_tc_065_*`` fails as soon as an implemented owned route is missing from the matrix.
"""

import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fastapi import APIRouter, FastAPI
from fixtures.auth import AuthUser, auth_test_settings, client_for
from fixtures.db import insert_auth_user
from route_matrix import (
    MATRIX,
    Owned,
    RouteCase,
    api_routes,
    not_implemented_routes,
    unlisted_routes,
)
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import get_model_provider
from app.ai.providers.base import ModelProvider
from app.ai.providers.mock import MockProvider
from app.core.errors import EndpointNotImplemented
from app.db.models import Destination, Place
from app.generation import jobs
from app.main import create_app
from app.places import seed

SAMPLETON = Path(__file__).resolve().parents[4] / "data" / "fixtures" / "sampleton"
FOREIGN = [case for case in MATRIX if case.access == "foreign"]

# Every row of A's trip, in each table the trip owns (§5), as text; compared before and after B.
TRIP_TABLES = (
    "trip_preferences",
    "trip_places",
    "budget_settings",
    "ai_generations",
    "itinerary_days",
    "itinerary_items",
    "itinerary_warnings",
    "itinerary_versions",
)


async def make_user(session: AsyncSession, name: str) -> AuthUser:
    user_id = uuid.uuid4()
    email = f"{name}-{user_id}@example.test"
    await insert_auth_user(session, user_id, email)
    return AuthUser(user_id=user_id, email=email)


@pytest_asyncio.fixture
async def users(db_session: AsyncSession) -> tuple[AuthUser, AuthUser]:
    return await make_user(db_session, "a"), await make_user(db_session, "b")


@pytest_asyncio.fixture
async def client(api_app: FastAPI, db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    """The real app with the MOCK provider; API-22's jobs are queued on ``api_app.state``."""
    queue: list[tuple[uuid.UUID, ModelProvider]] = []
    api_app.state.jobs = queue
    api_app.dependency_overrides[jobs.get_submit] = lambda: lambda g, p: queue.append((g, p))
    api_app.dependency_overrides[get_model_provider] = lambda: MockProvider("ok", app_env="test")
    async with client_for(api_app) as http:
        yield http


async def run_jobs(app: FastAPI, session: AsyncSession) -> None:
    @asynccontextmanager
    async def job_transaction() -> AsyncIterator[AsyncSession]:
        async with session.begin_nested():
            yield session

    while app.state.jobs:
        await jobs.run(*app.state.jobs.pop(0), job_transaction)


@pytest_asyncio.fixture
async def owned(
    api_app: FastAPI,
    client: httpx.AsyncClient,
    db_session: AsyncSession,
    users: tuple[AuthUser, AuthUser],
) -> Owned:
    """A's trip, preferences, generation and itinerary, made by A through API-07, 14 and 22."""
    a = users[0]
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    place_id = await db_session.scalar(
        select(Place.id).where(Place.destination_id == destination.id).order_by(Place.name)
    )
    assert place_id is not None
    title = f"A's private trip {uuid.uuid4()}"

    created = await client.post(
        "/api/v1/trips",
        json={
            "title": title,
            "destination_id": str(destination.id),
            "start_date": "2026-12-04",
            "end_date": "2026-12-06",
            "adults": 2,
        },
        headers=a.headers,
    )
    assert created.status_code == 201, created.text
    trip_id = created.json()["id"]
    saved = await client.put(
        f"/api/v1/trips/{trip_id}/preferences",
        json={
            "interests": ["museum"],
            "notes": "A's notes.",
            "must_visit_place_ids": [str(place_id)],
        },
        headers=a.headers,
    )
    assert saved.status_code == 200, saved.text
    started = await client.post(
        f"/api/v1/trips/{trip_id}/generations", json={"mode": "ai"}, headers=a.headers
    )
    assert started.status_code == 202, started.text
    generation_id = started.json()["id"]
    await run_jobs(api_app, db_session)
    done = await client.get(f"/api/v1/generations/{generation_id}", headers=a.headers)
    assert done.json()["status"] == "completed", done.text

    owned = Owned(
        user_id=a.user_id,
        email=a.email,
        trip_id=uuid.UUID(trip_id),
        trip_title=title,
        generation_id=uuid.UUID(generation_id),
        destination_id=destination.id,
        place_id=place_id,
    )
    rows = await trip_rows(db_session, owned)
    for table in ("trip_places", "ai_generations", "itinerary_days", "itinerary_items"):
        assert rows[table] != "null", f"A has no {table} rows"  # the plan really exists
    return owned


async def trip_rows(session: AsyncSession, owned: Owned) -> dict[str, str]:
    rows = {}
    for table in ("trips", "profiles", *TRIP_TABLES):
        key = "trip_id" if table in TRIP_TABLES else "id"
        value = owned.user_id if table == "profiles" else owned.trip_id
        query = f"select json_agg(t order by t::text)::text from public.{table} t where {key} = :v"  # noqa: S608  # fixed table names
        rows[table] = await session.scalar(text(query), {"v": value})
    return rows


async def a_state(client: httpx.AsyncClient, session: AsyncSession, owned: Owned) -> dict[str, Any]:
    """What A reads through the API, plus every database row of A's trip."""
    headers = AuthUser(user_id=owned.user_id, email=owned.email).headers
    reads = {
        "trip": f"/api/v1/trips/{owned.trip_id}",
        "preferences": f"/api/v1/trips/{owned.trip_id}/preferences",
        "generation": f"/api/v1/generations/{owned.generation_id}",
        "trips": "/api/v1/trips?include_archived=true",
    }
    state: dict[str, Any] = {}
    for name, url in reads.items():
        response = await client.get(url, headers=headers)
        assert response.status_code == 200, f"A cannot read {url}: {response.text}"
        state[name] = response.json()
    state["rows"] = await trip_rows(session, owned)
    return state


async def call(
    client: httpx.AsyncClient, case: RouteCase, user: AuthUser, owned: Owned
) -> httpx.Response:
    return await client.request(
        case.method,
        case.url(owned),
        params=case.params,
        json=case.body(owned) if case.body else None,
        headers=user.headers,
    )


# TC-065


def test_tc_065_every_implemented_owned_route_is_in_the_matrix() -> None:
    app = create_app(auth_test_settings())
    assert unlisted_routes(app) == []
    # No stale entry: each listed route exists and is built.
    served = {f"{m} {p}" for m, p, _ in api_routes(app)}
    stubs = {f"{m} {p}" for m, p in not_implemented_routes(app)}
    for case in MATRIX:
        assert f"{case.method} {case.path}" in served - stubs, case.id


def test_tc_065_an_unlisted_route_fails_the_check() -> None:
    app = create_app(auth_test_settings())
    probe = APIRouter(prefix="/api/v1")

    @probe.get("/trips/{trip_id}/unlisted-probe")
    async def unlisted_probe(trip_id: uuid.UUID) -> dict[str, str]:
        return {"trip_id": str(trip_id)}

    @probe.get("/trips/{trip_id}/declared-probe")
    async def declared_probe(trip_id: uuid.UUID) -> None:
        raise EndpointNotImplemented()

    app.include_router(probe)
    # The built route is reported; the 501 stub is skipped (IMD-37).
    assert unlisted_routes(app) == ["GET /api/v1/trips/{trip_id}/unlisted-probe"]


# TC-063, TC-064, TC-345, TC-346


@pytest.mark.asyncio
@pytest.mark.parametrize("case", MATRIX, ids=lambda case: case.id)
async def test_tc_063_tc_064_user_b_cannot_read_or_change_user_a(
    case: RouteCase,
    client: httpx.AsyncClient,
    db_session: AsyncSession,
    users: tuple[AuthUser, AuthUser],
    owned: Owned,
) -> None:
    b = users[1]
    before = await a_state(client, db_session, owned)

    response = await call(client, case, b, owned)

    if case.access == "foreign":
        assert response.status_code == 404, response.text
        assert response.json()["error"]["code"] == "NOT_FOUND"
    else:
        assert response.status_code in (200, 201), response.text
    leaked = [value for value in owned.secrets() if value in response.text]
    assert leaked == []
    assert await a_state(client, db_session, owned) == before


@pytest.mark.asyncio
@pytest.mark.parametrize("case", FOREIGN, ids=lambda case: case.id)
async def test_the_same_request_reaches_user_a(
    case: RouteCase,
    client: httpx.AsyncClient,
    users: tuple[AuthUser, AuthUser],
    owned: Owned,
) -> None:
    # Control: B's 404 comes from ownership, not from a malformed request or a missing resource.
    response = await call(client, case, users[0], owned)
    assert response.status_code not in (404, 422), response.text


@pytest.mark.asyncio
async def test_tc_063_a_foreign_trip_answers_like_a_missing_one(
    client: httpx.AsyncClient, users: tuple[AuthUser, AuthUser], owned: Owned
) -> None:
    b = users[1]
    foreign = await client.get(f"/api/v1/trips/{owned.trip_id}", headers=b.headers)
    missing = await client.get(f"/api/v1/trips/{uuid.uuid4()}", headers=b.headers)
    assert foreign.status_code == missing.status_code == 404
    assert without_request_id(foreign) == without_request_id(missing)


def without_request_id(response: httpx.Response) -> dict[str, Any]:
    return {**response.json()["error"], "request_id": None}
