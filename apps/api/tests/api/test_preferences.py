"""API-14 and API-15 (§6.6.2, §6.5 PreferencesIn / PreferencesOut; FR-009, FR-005: TC-074, TC-075,
TC-076; IMD-25, IMD-40, IMD-45).

Runs against the migrated test database with Sampleton loaded through the seed; every test is
rolled back. Trips are created through API-07 (IMP-203).
"""

import uuid
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fixtures.auth import AuthUser
from fixtures.db import insert_auth_user
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    DataSource,
    Destination,
    ItineraryDay,
    Place,
    Trip,
    TripPlace,
    TripPreferences,
)
from app.places import seed

REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLETON = REPO_ROOT / "data" / "fixtures" / "sampleton"

FULL_PREFERENCES: dict[str, Any] = {
    "interests": ["museum", "food"],
    "pace": "relaxed",
    "budget_priority": "saving",
    "transport_pref": "local_transport",
    "accommodation_type": "mid_range",
    "step_free_required": True,
    "notes": "We like quiet mornings.\nNo early starts.",
}
EXPECTED_EFFECTS = [
    {"field": "interests", "effect": "rank"},
    {"field": "pace", "effect": "rank"},
    {"field": "budget_priority", "effect": "rank"},
    {"field": "transport_pref", "effect": "note"},
    {"field": "accommodation_type", "effect": "note"},
    {"field": "step_free_required", "effect": "filter"},
    {"field": "notes", "effect": "note"},
    {"field": "must_visit_place_ids", "effect": "filter"},
]


@pytest_asyncio.fixture
async def sampleton(db_session: AsyncSession) -> Destination:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    return destination


@pytest_asyncio.fixture
async def places(db_session: AsyncSession, sampleton: Destination) -> dict[str, Place]:
    rows = await db_session.scalars(select(Place).where(Place.destination_id == sampleton.id))
    return {str(place.external_ref): place for place in rows}


@pytest_asyncio.fixture
async def trip(api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination) -> str:
    response = await api_client.post(
        "/api/v1/trips",
        json={
            "title": "Weekend in Sampleton",
            "destination_id": str(sampleton.id),
            "start_date": "2026-12-04",
            "end_date": "2026-12-06",
            "adults": 2,
        },
        headers=auth_user.headers,
    )
    assert response.status_code == 201, response.text
    trip_id: str = response.json()["id"]
    return trip_id


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> AuthUser:
    user_id = await insert_auth_user(db_session)
    return AuthUser(user_id=user_id, email=f"{user_id}@example.test")


async def put(
    client: httpx.AsyncClient, user: AuthUser, trip_id: str, body: dict[str, Any]
) -> httpx.Response:
    return await client.put(f"/api/v1/trips/{trip_id}/preferences", json=body, headers=user.headers)


def error_fields(response: httpx.Response) -> list[str]:
    assert response.status_code == 422, response.text
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    return [detail["field"] for detail in error["details"]]


async def must_visit_rows(session: AsyncSession, trip_id: str) -> dict[uuid.UUID, str]:
    rows = await session.scalars(select(TripPlace).where(TripPlace.trip_id == uuid.UUID(trip_id)))
    return {row.place_id: row.relation for row in rows}


# TC-074, TC-076


@pytest.mark.asyncio
async def test_tc_074_saved_preferences_are_returned_unchanged(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    places: dict[str, Place],
) -> None:
    must_visit = [str(places["sample-005"].id), str(places["sample-001"].id)]
    body = {**FULL_PREFERENCES, "must_visit_place_ids": must_visit}

    saved = await put(api_client, auth_user, trip, body)
    read = await api_client.get(f"/api/v1/trips/{trip}/preferences", headers=auth_user.headers)

    assert saved.status_code == 200, saved.text
    assert read.status_code == 200
    assert read.json() == saved.json()
    out = read.json()
    for field, value in FULL_PREFERENCES.items():
        assert out[field] == value, field
    assert set(out["must_visit_place_ids"]) == set(must_visit)
    assert out["saved"] is True

    row = await db_session.get(TripPreferences, uuid.UUID(trip))
    assert row is not None
    assert (row.pace, row.notes) == ("relaxed", FULL_PREFERENCES["notes"])
    assert row.interests == ["museum", "food"]


@pytest.mark.asyncio
async def test_api_15_before_saving_returns_the_defaults_with_saved_false(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str
) -> None:
    response = await api_client.get(f"/api/v1/trips/{trip}/preferences", headers=auth_user.headers)

    assert response.status_code == 200
    assert response.json() == {
        "interests": [],
        "pace": "balanced",
        "budget_priority": "balanced",
        "transport_pref": "walking",
        "accommodation_type": "any",
        "step_free_required": False,
        "notes": None,
        "must_visit_place_ids": [],
        "must_visit_places": [],
        "effects": EXPECTED_EFFECTS,
        "saved": False,
    }


@pytest.mark.asyncio
async def test_tc_076_each_field_reports_filter_rank_or_note(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str
) -> None:
    saved = await put(api_client, auth_user, trip, FULL_PREFERENCES)
    assert saved.json()["effects"] == EXPECTED_EFFECTS


@pytest.mark.asyncio
async def test_omitted_fields_take_the_defaults_on_a_full_replacement(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str
) -> None:
    await put(api_client, auth_user, trip, FULL_PREFERENCES)
    replaced = (await put(api_client, auth_user, trip, {"pace": "busy"})).json()
    assert replaced["pace"] == "busy"
    assert (replaced["interests"], replaced["notes"], replaced["step_free_required"]) == (
        [],
        None,
        False,
    )


@pytest.mark.asyncio
async def test_notes_are_stored_as_written_without_control_characters(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str
) -> None:
    notes = "Prefer\tshade.\nAvoid stairs \x07please\x00."
    saved = (await put(api_client, auth_user, trip, {"notes": notes})).json()
    assert saved["notes"] == "Prefer\tshade.\nAvoid stairs please."


# TC-075


@pytest.mark.asyncio
async def test_tc_075_must_visit_places_are_stored_as_trip_places_must_visit(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    places: dict[str, Place],
) -> None:
    first = [places["sample-001"].id, places["sample-002"].id]
    saved = await put(
        api_client, auth_user, trip, {"must_visit_place_ids": [str(p) for p in first]}
    )

    assert await must_visit_rows(db_session, trip) == dict.fromkeys(first, "must_visit")
    named = saved.json()["must_visit_places"]
    assert {item["id"] for item in named} == {str(p) for p in first}
    assert {item["name"] for item in named} == {
        places["sample-001"].name,
        places["sample-002"].name,
    }

    # Replacing the set removes the place that is no longer listed.
    second = [places["sample-002"].id, places["sample-003"].id]
    await put(api_client, auth_user, trip, {"must_visit_place_ids": [str(p) for p in second]})
    assert await must_visit_rows(db_session, trip) == dict.fromkeys(second, "must_visit")

    await put(api_client, auth_user, trip, {"must_visit_place_ids": []})
    assert await must_visit_rows(db_session, trip) == {}


@pytest.mark.asyncio
async def test_a_saved_place_becomes_must_visit_and_other_saved_places_stay(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    places: dict[str, Place],
) -> None:
    saved_only, promoted = places["sample-010"].id, places["sample-011"].id
    db_session.add_all(
        [
            TripPlace(trip_id=uuid.UUID(trip), place_id=saved_only, relation="saved"),
            TripPlace(trip_id=uuid.UUID(trip), place_id=promoted, relation="saved"),
        ]
    )
    await db_session.flush()

    await put(api_client, auth_user, trip, {"must_visit_place_ids": [str(promoted)]})

    assert await must_visit_rows(db_session, trip) == {
        saved_only: "saved",
        promoted: "must_visit",
    }


@pytest.mark.asyncio
async def test_a_must_visit_place_of_another_destination_is_rejected_naming_it(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    places: dict[str, Place],
) -> None:
    other = Destination(
        slug=f"other-{uuid.uuid4().hex[:8]}",
        name="Otherville (test)",
        country_code="GB",
        timezone="Europe/London",
        currency="GBP",
        center_lat=Decimal("53.9"),
        center_lon=Decimal("2.2"),
        bbox_min_lat=Decimal("53.8"),
        bbox_max_lat=Decimal("54.0"),
        bbox_min_lon=Decimal("2.1"),
        bbox_max_lon=Decimal("2.3"),
    )
    db_session.add(other)
    await db_session.flush()
    source = await db_session.scalar(select(DataSource))
    assert source is not None
    foreign = Place(
        destination_id=other.id,
        source_id=source.id,
        external_ref=f"other-{uuid.uuid4().hex[:8]}",
        name="Elsewhere Tower",
        category="sight",
        lat=Decimal("53.9"),
        lon=Decimal("2.2"),
        typical_duration_min=30,
    )
    db_session.add(foreign)
    await db_session.flush()
    good = str(places["sample-001"].id)

    response = await put(
        api_client, auth_user, trip, {"must_visit_place_ids": [good, str(foreign.id)]}
    )

    assert error_fields(response) == ["must_visit_place_ids.1"]
    assert str(foreign.id) in response.json()["error"]["details"][0]["message"]
    assert await must_visit_rows(db_session, trip) == {}
    assert await db_session.get(TripPreferences, uuid.UUID(trip)) is None


@pytest.mark.asyncio
async def test_inactive_or_unknown_must_visit_places_are_rejected(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    places: dict[str, Place],
) -> None:
    inactive = places["sample-020"]
    await db_session.execute(update(Place).where(Place.id == inactive.id).values(is_active=False))
    unknown = uuid.uuid4()

    response = await put(
        api_client,
        auth_user,
        trip,
        {"must_visit_place_ids": [str(inactive.id), str(places["sample-001"].id), str(unknown)]},
    )

    assert error_fields(response) == ["must_visit_place_ids.0", "must_visit_place_ids.2"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("body", "field"),
    [
        ({"pace": "slow"}, "pace"),
        ({"budget_priority": "lavish"}, "budget_priority"),
        ({"transport_pref": "boat"}, "transport_pref"),
        ({"accommodation_type": "castle"}, "accommodation_type"),
        ({"interests": ["stay"]}, "interests.0"),
        ({"interests": ["food", "food"]}, "interests"),
        ({"notes": "x" * 1001}, "notes"),
        ({"must_visit_place_ids": [str(uuid.uuid4()) for _ in range(11)]}, "must_visit_place_ids"),
        ({"user_id": str(uuid.uuid4())}, "user_id"),
    ],
    ids=[
        "pace",
        "budget priority",
        "transport",
        "accommodation",
        "stay interest",
        "duplicate interest",
        "notes too long",
        "11 must-visit",
        "user_id",
    ],
)
async def test_api_14_rejects_values_outside_the_rules(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    trip: str,
    body: dict[str, Any],
    field: str,
) -> None:
    response = await put(api_client, auth_user, trip, body)
    assert error_fields(response) == [field]
    assert await db_session.get(TripPreferences, uuid.UUID(trip)) is None


@pytest.mark.asyncio
async def test_ten_must_visit_places_are_allowed(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str, places: dict[str, Place]
) -> None:
    ten = [str(places[f"sample-{n:03d}"].id) for n in range(1, 11)]
    response = await put(api_client, auth_user, trip, {"must_visit_place_ids": ten})
    assert response.status_code == 200
    assert len(response.json()["must_visit_places"]) == 10


# Trip state (IMD-25, FR-011)


@pytest.mark.asyncio
async def test_saving_preferences_makes_a_draft_ready(
    api_client: httpx.AsyncClient, auth_user: AuthUser, trip: str
) -> None:
    before = await api_client.get(f"/api/v1/trips/{trip}", headers=auth_user.headers)
    assert before.json()["status"] == "draft"

    await put(api_client, auth_user, trip, FULL_PREFERENCES)

    after = (await api_client.get(f"/api/v1/trips/{trip}", headers=auth_user.headers)).json()
    assert after["status"] == "ready"
    assert after["plan_stale"] is False  # no itinerary yet


@pytest.mark.asyncio
async def test_saving_preferences_marks_an_existing_itinerary_stale(
    api_client: httpx.AsyncClient, db_session: AsyncSession, auth_user: AuthUser, trip: str
) -> None:
    db_session.add(ItineraryDay(trip_id=uuid.UUID(trip), day_number=1, plan_date=date(2026, 12, 4)))
    await db_session.flush()

    await put(api_client, auth_user, trip, FULL_PREFERENCES)

    after = (await api_client.get(f"/api/v1/trips/{trip}", headers=auth_user.headers)).json()
    assert after["plan_stale"] is True


@pytest.mark.asyncio
async def test_an_archived_trip_is_read_only(
    api_client: httpx.AsyncClient, db_session: AsyncSession, auth_user: AuthUser, trip: str
) -> None:
    await db_session.execute(
        update(Trip).where(Trip.id == uuid.UUID(trip)).values(status="archived")
    )
    response = await put(api_client, auth_user, trip, FULL_PREFERENCES)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"
    assert await db_session.get(TripPreferences, uuid.UUID(trip)) is None


# Ownership (FR-005)


@pytest.mark.asyncio
async def test_another_users_trip_is_404_on_both_routes(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    other_user: AuthUser,
    trip: str,
) -> None:
    await put(api_client, auth_user, trip, FULL_PREFERENCES)

    read = await api_client.get(f"/api/v1/trips/{trip}/preferences", headers=other_user.headers)
    write = await put(api_client, other_user, trip, {"pace": "busy"})
    missing = await api_client.get(
        f"/api/v1/trips/{uuid.uuid4()}/preferences", headers=other_user.headers
    )

    for response in (read, write):
        assert response.status_code == 404
        error = response.json()["error"]
        assert error["code"] == "NOT_FOUND"
        assert error["message"] == missing.json()["error"]["message"]
        assert "quiet mornings" not in response.text
    stored = await db_session.get(TripPreferences, uuid.UUID(trip))
    assert stored is not None
    assert stored.pace == "relaxed"  # unchanged by the other user


@pytest.mark.asyncio
async def test_preference_routes_need_a_token(api_client: httpx.AsyncClient, trip: str) -> None:
    for method in ("GET", "PUT"):
        response = await api_client.request(method, f"/api/v1/trips/{trip}/preferences", json={})
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHENTICATED"
