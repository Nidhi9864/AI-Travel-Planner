"""API-07, API-08 and API-10 (§6.6.2; FR-005, FR-007, FR-008: TC-063, TC-068 to TC-073).

Runs against the migrated test database (tests/fixtures/db.py); every test is rolled back. The
supported destination is the Sampleton SAMPLE fixture, loaded through the seed (IMP-107).
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fixtures.auth import AuthUser, bearer, make_token
from fixtures.db import insert_auth_user
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BudgetSettings, Destination, Trip, TripPreferences
from app.places import seed

REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLETON = REPO_ROOT / "data" / "fixtures" / "sampleton"
START = date(2026, 12, 4)

TRIP_OUT_FIELDS = {
    "id",
    "title",
    "destination_id",
    "start_date",
    "end_date",
    "num_days",
    "adults",
    "children",
    "group_needs",
    "budget",
    "status",
    "plan_revision",
    "plan_stale",
    "has_itinerary",
    "destination",
    "created_at",
    "updated_at",
}


@pytest_asyncio.fixture
async def sampleton(db_session: AsyncSession) -> Destination:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    return destination


@pytest_asyncio.fixture
async def inactive_destination(db_session: AsyncSession) -> Destination:
    destination = Destination(
        slug=f"closed-{uuid.uuid4().hex[:8]}",
        name="Closedville (inactive test row)",
        country_code="GB",
        timezone="Europe/London",
        currency="GBP",
        center_lat=53.9,
        center_lon=2.2,
        bbox_min_lat=53.8,
        bbox_max_lat=54.0,
        bbox_min_lon=2.1,
        bbox_max_lon=2.3,
        is_active=False,
    )
    db_session.add(destination)
    await db_session.flush()
    return destination


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession) -> AuthUser:
    user_id = await insert_auth_user(db_session)
    return AuthUser(user_id=user_id, email=f"{user_id}@example.test")


def trip_body(destination: Destination, **changes: Any) -> dict[str, Any]:
    body: dict[str, Any] = {
        "title": "Weekend in Sampleton",
        "destination_id": str(destination.id),
        "start_date": START.isoformat(),
        "end_date": (START + timedelta(days=2)).isoformat(),
        "adults": 2,
        "children": 1,
        "group_needs": ["children"],
        "budget": {"amount": "15000.00", "currency": "GBP"},
    }
    body.update(changes)
    return body


async def trip_count(session: AsyncSession, user_id: uuid.UUID | None = None) -> int:
    query = select(func.count()).select_from(Trip)
    if user_id is not None:
        query = query.where(Trip.user_id == user_id)
    return int(await session.scalar(query) or 0)


async def create(
    client: httpx.AsyncClient, user: AuthUser, destination: Destination, **changes: Any
) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/trips", json=trip_body(destination, **changes), headers=user.headers
    )
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


def error_fields(response: httpx.Response) -> list[str]:
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    return [detail["field"] for detail in error["details"]]


# API-07


@pytest.mark.asyncio
async def test_tc_068_valid_input_creates_a_draft_trip_visible_in_the_list(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    trip = await create(api_client, auth_user, sampleton)

    assert set(trip) == TRIP_OUT_FIELDS
    assert trip["status"] == "draft"
    assert trip["plan_revision"] == 0
    assert trip["plan_stale"] is False
    assert trip["has_itinerary"] is False
    assert trip["title"] == "Weekend in Sampleton"
    assert trip["num_days"] == 3
    assert (trip["adults"], trip["children"]) == (2, 1)
    assert trip["budget"] == {"amount": "15000.00", "currency": "GBP"}
    assert trip["destination"] == {
        "id": str(sampleton.id),
        "name": sampleton.name,
        "timezone": "Europe/London",
        "currency": "GBP",
        "is_sample": True,
    }
    assert trip["created_at"].endswith("Z")
    assert trip["updated_at"].endswith("Z")

    listed = await api_client.get("/api/v1/trips", headers=auth_user.headers)
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [trip["id"]]

    row = await db_session.get(Trip, uuid.UUID(trip["id"]))
    assert row is not None
    assert row.user_id == auth_user.user_id
    assert (row.budget_amount, row.budget_currency) == (15000, "GBP")


@pytest.mark.asyncio
async def test_api_07_writes_default_budget_settings_and_no_preferences(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    trip_id = uuid.UUID((await create(api_client, auth_user, sampleton))["id"])

    settings = await db_session.get(BudgetSettings, trip_id)
    assert settings is not None
    assert settings.contingency_pct == 10
    assert settings.transport_allowance_per_day is None
    assert settings.stay_budget_per_night is None
    # IMD-25: API-14 creates the preferences row, not API-07.
    assert await db_session.get(TripPreferences, trip_id) is None


@pytest.mark.asyncio
async def test_a_trip_without_budget_or_group_needs_uses_the_defaults(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    body = trip_body(sampleton)
    for name in ("budget", "group_needs", "adults", "children"):
        body.pop(name)
    response = await api_client.post("/api/v1/trips", json=body, headers=auth_user.headers)

    assert response.status_code == 201, response.text
    trip = response.json()
    assert trip["budget"] is None
    assert trip["group_needs"] == []
    assert (trip["adults"], trip["children"]) == (1, 0)


@pytest.mark.asyncio
async def test_the_title_is_trimmed(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    trip = await create(api_client, auth_user, sampleton, title="  Coast walk  ")
    assert trip["title"] == "Coast walk"


@pytest.mark.asyncio
async def test_tc_069_an_unknown_destination_is_rejected_with_the_supported_list(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
    inactive_destination: Destination,
) -> None:
    for destination_id in (uuid.uuid4(), inactive_destination.id):
        response = await api_client.post(
            "/api/v1/trips",
            json={**trip_body(sampleton), "destination_id": str(destination_id)},
            headers=auth_user.headers,
        )
        assert response.status_code == 422
        assert error_fields(response) == ["destination_id"]
        message = response.json()["error"]["details"][0]["message"]
        assert sampleton.name in message
        assert str(sampleton.id) in message
        # An inactive destination is not offered as supported.
        assert inactive_destination.name not in message
    assert await trip_count(db_session, auth_user.user_id) == 0


@pytest.mark.asyncio
async def test_tc_070_group_needs_are_stored(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    needs = ["children", "older_adults", "reduced_mobility"]
    trip = await create(api_client, auth_user, sampleton, group_needs=needs)

    assert trip["group_needs"] == needs
    row = await db_session.get(Trip, uuid.UUID(trip["id"]))
    assert row is not None
    assert row.group_needs == needs
    read = await api_client.get(f"/api/v1/trips/{trip['id']}", headers=auth_user.headers)
    assert read.json()["group_needs"] == needs


@pytest.mark.asyncio
async def test_an_unknown_group_need_is_rejected(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, group_needs=["pets"]),
        headers=auth_user.headers,
    )
    assert response.status_code == 422
    assert error_fields(response) == ["group_needs.0"]


@pytest.mark.asyncio
async def test_tc_071_end_before_start_returns_422_naming_end_date(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, end_date=(START - timedelta(days=1)).isoformat()),
        headers=auth_user.headers,
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["details"][0] == {
        "field": "end_date",
        "message": "End date must be on or after start date.",
    }
    assert await trip_count(db_session, auth_user.user_id) == 0


@pytest.mark.asyncio
async def test_tc_072_a_trip_longer_than_14_days_is_rejected_with_the_limit(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, end_date=(START + timedelta(days=14)).isoformat()),
        headers=auth_user.headers,
    )

    assert response.status_code == 422
    assert error_fields(response) == ["end_date"]
    assert "14 days" in response.json()["error"]["details"][0]["message"]
    assert await trip_count(db_session, auth_user.user_id) == 0

    longest = await create(
        api_client, auth_user, sampleton, end_date=(START + timedelta(days=13)).isoformat()
    )
    assert longest["num_days"] == 14


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", ["0.00", "0", "-5.00"])
async def test_tc_073_a_budget_of_zero_or_less_is_rejected(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
    amount: str,
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, budget={"amount": amount, "currency": "GBP"}),
        headers=auth_user.headers,
    )

    assert response.status_code == 422
    assert error_fields(response) == ["budget.amount"]
    assert await trip_count(db_session, auth_user.user_id) == 0


@pytest.mark.asyncio
async def test_the_budget_currency_must_be_the_destination_currency(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    assert sampleton.currency == "GBP"
    rejected = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, budget={"amount": "15000.00", "currency": "INR"}),
        headers=auth_user.headers,
    )
    assert rejected.status_code == 422
    assert rejected.json()["error"]["details"] == [
        {
            "field": "budget.currency",
            "message": f"Budget currency must be GBP, the currency of {sampleton.name}.",
        }
    ]
    assert await trip_count(db_session, auth_user.user_id) == 0

    accepted = await create(
        api_client, auth_user, sampleton, budget={"amount": "15000.00", "currency": "GBP"}
    )
    assert accepted["budget"] == {"amount": "15000.00", "currency": "GBP"}


@pytest.mark.asyncio
async def test_traveller_counts_and_currency_are_checked(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(
            sampleton, adults=0, children=21, budget={"amount": "10.00", "currency": "gb"}
        ),
        headers=auth_user.headers,
    )
    assert response.status_code == 422
    assert error_fields(response) == ["adults", "children", "budget.currency"]


@pytest.mark.asyncio
async def test_a_body_naming_a_user_is_rejected(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    other_user: AuthUser,
    sampleton: Destination,
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, user_id=str(other_user.user_id)),
        headers=auth_user.headers,
    )
    assert response.status_code == 422
    assert error_fields(response) == ["user_id"]
    assert await trip_count(db_session) == 0


@pytest.mark.asyncio
async def test_api_07_accepts_no_contingency_pct(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    response = await api_client.post(
        "/api/v1/trips",
        json=trip_body(sampleton, contingency_pct="20"),
        headers=auth_user.headers,
    )
    assert response.status_code == 422
    assert error_fields(response) == ["contingency_pct"]


# API-10


@pytest.mark.asyncio
async def test_api_10_reads_my_trip(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    trip = await create(api_client, auth_user, sampleton)
    response = await api_client.get(f"/api/v1/trips/{trip['id']}", headers=auth_user.headers)
    assert response.status_code == 200
    assert response.json() == trip


@pytest.mark.asyncio
async def test_tc_063_another_users_trip_is_404_with_no_trip_data(
    api_client: httpx.AsyncClient,
    auth_user: AuthUser,
    other_user: AuthUser,
    sampleton: Destination,
) -> None:
    trip = await create(api_client, auth_user, sampleton, title="Private plans")

    foreign = await api_client.get(f"/api/v1/trips/{trip['id']}", headers=other_user.headers)
    missing = await api_client.get(f"/api/v1/trips/{uuid.uuid4()}", headers=other_user.headers)

    assert foreign.status_code == missing.status_code == 404
    foreign_error = foreign.json()["error"]
    missing_error = missing.json()["error"]
    assert foreign_error["code"] == "NOT_FOUND"
    # Identical to a missing trip apart from the request id.
    foreign_error.pop("request_id")
    missing_error.pop("request_id")
    assert foreign_error == missing_error
    assert trip["id"] not in foreign.text
    assert "Private plans" not in foreign.text


@pytest.mark.asyncio
async def test_a_soft_deleted_trip_is_404_and_not_listed(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    trip = await create(api_client, auth_user, sampleton)
    await db_session.execute(
        update(Trip).where(Trip.id == uuid.UUID(trip["id"])).values(deleted_at=func.now())
    )

    read = await api_client.get(f"/api/v1/trips/{trip['id']}", headers=auth_user.headers)
    listed = await api_client.get("/api/v1/trips", headers=auth_user.headers)
    assert read.status_code == 404
    assert listed.json()["items"] == []
    assert listed.json()["total"] == 0


@pytest.mark.asyncio
async def test_a_malformed_trip_id_is_422(
    api_client: httpx.AsyncClient, auth_user: AuthUser
) -> None:
    response = await api_client.get("/api/v1/trips/not-a-uuid", headers=auth_user.headers)
    assert response.status_code == 422
    assert error_fields(response) == ["trip_id"]


# API-08


@pytest.mark.asyncio
async def test_api_08_lists_only_my_trips_newest_first(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    other_user: AuthUser,
    sampleton: Destination,
) -> None:
    # The updated_at trigger sets now(), which is fixed inside the test transaction, so these rows
    # are inserted with their own timestamps (the trigger runs only on update).
    await api_client.get("/api/v1/me", headers=auth_user.headers)  # ensures the profile row
    base = datetime(2026, 10, 1, tzinfo=UTC)
    for n in (0, 2, 1):
        db_session.add(
            Trip(
                user_id=auth_user.user_id,
                destination_id=sampleton.id,
                title=f"Mine {n}",
                start_date=START,
                end_date=START,
                created_at=base,
                updated_at=base + timedelta(hours=n),
            )
        )
    await db_session.flush()
    await create(api_client, other_user, sampleton, title="Theirs")

    response = await api_client.get("/api/v1/trips", headers=auth_user.headers)

    assert response.status_code == 200
    page = response.json()
    assert set(page) == {"items", "total", "limit", "offset"}
    assert (page["total"], page["limit"], page["offset"]) == (3, 20, 0)
    assert [item["title"] for item in page["items"]] == ["Mine 2", "Mine 1", "Mine 0"]
    assert all(set(item) == TRIP_OUT_FIELDS for item in page["items"])


@pytest.mark.asyncio
async def test_api_08_pages_with_limit_and_offset(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    created = {(await create(api_client, auth_user, sampleton))["id"] for _ in range(3)}

    first = (await api_client.get("/api/v1/trips?limit=2", headers=auth_user.headers)).json()
    second = (
        await api_client.get("/api/v1/trips?limit=2&offset=2", headers=auth_user.headers)
    ).json()

    assert (len(first["items"]), first["total"], first["limit"]) == (2, 3, 2)
    assert (len(second["items"]), second["total"], second["offset"]) == (1, 3, 2)
    assert {item["id"] for item in first["items"] + second["items"]} == created


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("query", "field"), [("limit=51", "limit"), ("limit=0", "limit"), ("offset=-1", "offset")]
)
async def test_api_08_limit_is_1_to_50_and_offset_not_negative(
    api_client: httpx.AsyncClient, auth_user: AuthUser, query: str, field: str
) -> None:
    response = await api_client.get(f"/api/v1/trips?{query}", headers=auth_user.headers)
    assert response.status_code == 422
    assert error_fields(response) == [field]


@pytest.mark.asyncio
async def test_api_08_accepts_the_maximum_limit(
    api_client: httpx.AsyncClient, auth_user: AuthUser
) -> None:
    response = await api_client.get("/api/v1/trips?limit=50", headers=auth_user.headers)
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "limit": 50, "offset": 0}


@pytest.mark.asyncio
async def test_api_08_hides_archived_trips_unless_asked(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    kept = await create(api_client, auth_user, sampleton, title="Kept")
    archived = await create(api_client, auth_user, sampleton, title="Archived")
    await db_session.execute(
        update(Trip).where(Trip.id == uuid.UUID(archived["id"])).values(status="archived")
    )

    default = (await api_client.get("/api/v1/trips", headers=auth_user.headers)).json()
    everything = (
        await api_client.get("/api/v1/trips?include_archived=true", headers=auth_user.headers)
    ).json()

    assert [item["id"] for item in default["items"]] == [kept["id"]]
    assert default["total"] == 1
    assert {item["id"] for item in everything["items"]} == {kept["id"], archived["id"]}


@pytest.mark.asyncio
async def test_trip_routes_need_a_token(api_client: httpx.AsyncClient) -> None:
    for method, path in (
        ("POST", "/api/v1/trips"),
        ("GET", "/api/v1/trips"),
        ("GET", f"/api/v1/trips/{uuid.uuid4()}"),
    ):
        response = await api_client.request(method, path)
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHENTICATED"
    expired = bearer(make_token(uuid.uuid4(), expired=True))
    assert (await api_client.get("/api/v1/trips", headers=expired)).status_code == 401
