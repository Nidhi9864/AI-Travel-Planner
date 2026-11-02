"""API-06 and basic API-16 (§6.6.3, §6.5 Destination and PlaceSummary; FR-019: TC-069, TC-101,
TC-102; IMP-205 places-api-search part).

Runs against the migrated test database with Sampleton loaded through the seed (IMP-107, IMP-205);
every test is rolled back.
"""

import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
import pytest
import pytest_asyncio
from fixtures.auth import AuthUser
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DataSource, Destination, Place
from app.places import seed, vocabulary

REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLETON = REPO_ROOT / "data" / "fixtures" / "sampleton"

DESTINATION_FIELDS = {
    "id",
    "slug",
    "name",
    "region",
    "country_code",
    "timezone",
    "currency",
    "is_sample",
    "center",
    "bbox",
}
PLACE_FIELDS = {
    "id",
    "name",
    "category",
    "tags",
    "lat",
    "lon",
    "typical_duration_min",
    "price",
    "price_label",
    "hours_label",
    "verification_status",
    "suitability",
}


@pytest_asyncio.fixture
async def sampleton(db_session: AsyncSession) -> Destination:
    await seed.load_fixture(db_session, seed.read_fixture(SAMPLETON))
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    return destination


def destination_row(slug: str, name: str, *, active: bool = True) -> Destination:
    return Destination(
        slug=slug,
        name=name,
        country_code="GB",
        timezone="Europe/London",
        currency="GBP",
        center_lat=Decimal("53.9"),
        center_lon=Decimal("2.2"),
        bbox_min_lat=Decimal("53.8"),
        bbox_max_lat=Decimal("54.0"),
        bbox_min_lon=Decimal("2.1"),
        bbox_max_lon=Decimal("2.3"),
        is_active=active,
    )


async def add_destination_with_place(
    session: AsyncSession, sampleton: Destination, *, active: bool, place_name: str
) -> Destination:
    destination = destination_row(f"t-{uuid.uuid4().hex[:8]}", f"Test {place_name}", active=active)
    session.add(destination)
    await session.flush()
    source = await session.scalar(select(DataSource))
    assert source is not None
    session.add(
        Place(
            destination_id=destination.id,
            source_id=source.id,
            external_ref=f"other-{uuid.uuid4().hex[:8]}",
            name=place_name,
            category="sight",
            lat=Decimal("53.9"),
            lon=Decimal("2.2"),
            typical_duration_min=30,
        )
    )
    await session.flush()
    return destination


async def search(
    client: httpx.AsyncClient, user: AuthUser, destination: Destination, **params: Any
) -> httpx.Response:
    return await client.get(
        "/api/v1/places",
        params={"destination_id": str(destination.id), **params},
        headers=user.headers,
    )


# API-06


@pytest.mark.asyncio
async def test_destinations_lists_only_active_destinations_ordered_by_name(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    db_session.add_all(
        [
            destination_row(f"a-{uuid.uuid4().hex[:6]}", "Aardvark Bay (test)"),
            destination_row(f"z-{uuid.uuid4().hex[:6]}", "Zed Hidden (test)", active=False),
        ]
    )
    await db_session.flush()

    response = await api_client.get("/api/v1/destinations", headers=auth_user.headers)

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert "Zed Hidden (test)" not in names
    assert names == sorted(names)
    assert {"Aardvark Bay (test)", sampleton.name} <= set(names)


@pytest.mark.asyncio
async def test_tc_069_destinations_return_the_section_6_5_shape(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    response = await api_client.get("/api/v1/destinations", headers=auth_user.headers)
    [item] = [d for d in response.json() if d["slug"] == "sampleton"]

    assert set(item) == DESTINATION_FIELDS
    assert item == {
        "id": str(sampleton.id),
        "slug": "sampleton",
        "name": "Sampleton (sample)",
        "region": "Sample region (synthetic)",
        "country_code": "GB",
        "timezone": "Europe/London",
        "currency": "GBP",
        "is_sample": True,
        "center": {"lat": 53.9, "lon": 2.2},
        "bbox": {"min_lat": 53.85, "max_lat": 53.95, "min_lon": 2.1, "max_lon": 2.3},
    }


@pytest.mark.asyncio
async def test_destinations_and_places_need_a_token(api_client: httpx.AsyncClient) -> None:
    for path in ("/api/v1/destinations", f"/api/v1/places?destination_id={uuid.uuid4()}"):
        response = await api_client.get(path)
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHENTICATED"


# API-16


@pytest.mark.asyncio
async def test_places_returns_a_page_of_the_destinations_active_places_by_name(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    response = await search(api_client, auth_user, sampleton)

    assert response.status_code == 200
    page = response.json()
    assert (page["total"], page["limit"], page["offset"]) == (30, 20, 0)
    assert len(page["items"]) == 20
    assert all(set(item) == PLACE_FIELDS for item in page["items"])
    names = [item["name"] for item in page["items"]]
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_places_pages_with_limit_and_offset(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    first = (await search(api_client, auth_user, sampleton, limit=25)).json()
    rest = (await search(api_client, auth_user, sampleton, limit=25, offset=25)).json()

    assert (len(first["items"]), len(rest["items"])) == (25, 5)
    ids = [item["id"] for item in first["items"] + rest["items"]]
    assert len(set(ids)) == 30


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("params", "field"),
    [
        ({"limit": 51}, "limit"),
        ({"limit": 0}, "limit"),
        ({"offset": -1}, "offset"),
        ({"q": "x" * 81}, "q"),
        ({"category": "beach"}, "category.0"),
        ({"category": "stay"}, "category.0"),
    ],
    ids=["limit above 50", "limit 0", "negative offset", "q too long", "unknown", "stay"],
)
async def test_places_rejects_bad_query_values(
    api_client: httpx.AsyncClient,
    auth_user: AuthUser,
    sampleton: Destination,
    params: dict[str, Any],
    field: str,
) -> None:
    response = await search(api_client, auth_user, sampleton, **params)
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert [detail["field"] for detail in error["details"]] == [field]


@pytest.mark.asyncio
async def test_places_needs_a_destination_id(
    api_client: httpx.AsyncClient, auth_user: AuthUser
) -> None:
    response = await api_client.get("/api/v1/places", headers=auth_user.headers)
    assert response.status_code == 422
    assert [d["field"] for d in response.json()["error"]["details"]] == ["destination_id"]


@pytest.mark.asyncio
async def test_places_filters_by_name_case_insensitively(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    page = (await search(api_client, auth_user, sampleton, q="harbour LOOKOUT")).json()
    assert [item["name"] for item in page["items"]] == ["Sample Harbour Lookout (sample)"]
    assert page["total"] == 1

    # LIKE wildcards in q are plain characters.
    wildcard = (await search(api_client, auth_user, sampleton, q="%")).json()
    assert wildcard == {"items": [], "total": 0, "limit": 20, "offset": 0}


@pytest.mark.asyncio
async def test_places_filters_by_one_or_more_categories(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    food = (await search(api_client, auth_user, sampleton, category="food", limit=50)).json()
    assert food["total"] == 6
    assert {item["category"] for item in food["items"]} == {"food"}

    both = (
        await search(api_client, auth_user, sampleton, category=["food", "museum"], limit=50)
    ).json()
    assert both["total"] == 10
    assert {item["category"] for item in both["items"]} == {"food", "museum"}

    combined = (await search(api_client, auth_user, sampleton, category="food", q="zzz")).json()
    assert combined["total"] == 0  # an empty page is valid


@pytest.mark.asyncio
async def test_places_hides_inactive_places_and_other_destinations(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    await db_session.execute(
        update(Place).where(Place.external_ref == "sample-001").values(is_active=False)
    )
    other = await add_destination_with_place(
        db_session, sampleton, active=True, place_name="Elsewhere Tower"
    )

    page = (await search(api_client, auth_user, sampleton, limit=50)).json()
    names = {item["name"] for item in page["items"]}
    assert page["total"] == 29
    assert "Sample Harbour Lookout (sample)" not in names
    assert "Elsewhere Tower" not in names

    theirs = (await search(api_client, auth_user, other)).json()
    assert [item["name"] for item in theirs["items"]] == ["Elsewhere Tower"]


@pytest.mark.asyncio
async def test_places_of_an_inactive_or_unknown_destination_are_an_empty_page(
    api_client: httpx.AsyncClient,
    db_session: AsyncSession,
    auth_user: AuthUser,
    sampleton: Destination,
) -> None:
    hidden = await add_destination_with_place(
        db_session, sampleton, active=False, place_name="Hidden Tower"
    )
    page = (await search(api_client, auth_user, hidden)).json()
    assert page == {"items": [], "total": 0, "limit": 20, "offset": 0}

    unknown = await api_client.get(
        "/api/v1/places", params={"destination_id": str(uuid.uuid4())}, headers=auth_user.headers
    )
    assert unknown.json()["total"] == 0


@pytest.mark.asyncio
async def test_tc_101_tc_102_tags_from_the_vocabulary_and_unknown_suitability_as_null(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    items = (await search(api_client, auth_user, sampleton, limit=50)).json()["items"]
    by_name = {item["name"]: item for item in items}

    assert all(set(item["tags"]) <= vocabulary.TAGS for item in items)
    lookout = by_name["Sample Harbour Lookout (sample)"]  # sample-001
    assert set(lookout["tags"]) == {"views", "outdoor"}
    assert lookout["suitability"] == {"step_free": True, "child_friendly": True, "indoor": False}
    tower = by_name["Sample Old Signal Tower (sample)"]  # sample-002: step_free left empty
    assert tower["suitability"]["step_free"] is None  # unknown, never false


@pytest.mark.asyncio
async def test_places_show_prices_as_money_and_null_when_unpriced(
    api_client: httpx.AsyncClient, auth_user: AuthUser, sampleton: Destination
) -> None:
    items = (await search(api_client, auth_user, sampleton, q="Signal Tower")).json()["items"]
    [tower] = items
    assert tower["price"] == {"min": "3.00", "max": "5.00", "currency": "GBP", "label": "estimate"}
    assert (tower["lat"], tower["lon"]) == (53.876, 2.12)
    assert tower["verification_status"] == "estimated"

    page = (await search(api_client, auth_user, sampleton, limit=50)).json()
    unpriced = [item for item in page["items"] if item["price_label"] == "unavailable"]
    assert unpriced
    assert all(item["price"] is None for item in unpriced)
