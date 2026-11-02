"""TC-345: browser roles read zero rows from every public table (US-008 AC2, NFR-012; IMP-106).

One row is written to each of the 15 MVP tables and the 2 RAG tables (migration 0007) through
the ORM models, inside the test's rolled-back transaction, so every table has something to read.
Then, for roles ``anon`` and ``authenticated`` (the latter with the row owner's id as
``auth.uid()``), each table in schema public, ``alembic_version`` included, must give zero readable
rows. Migration 0005 revokes every table privilege (§5.4 Lock 3), so a read is refused; a refused
read counts as zero rows.
"""

import uuid
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

import pytest
from fixtures.db import insert_auth_user
from psycopg import errors
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AiGeneration,
    Base,
    BudgetSettings,
    DataSource,
    Destination,
    ItineraryDay,
    ItineraryItem,
    ItineraryVersion,
    ItineraryWarning,
    Place,
    PlaceOpeningHours,
    Profile,
    RagChunk,
    RagDocument,
    RouteCache,
    Trip,
    TripPlace,
    TripPreferences,
    metadata,
)

BROWSER_ROLES = ("anon", "authenticated")

# Fixed ids keep the run repeatable (§5.6); the transaction is rolled back after the test.
USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000345")
DESTINATION_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")
SOURCE_ID = uuid.UUID("00000000-0000-4000-8000-000000000002")
PLACE_A_ID = uuid.UUID("00000000-0000-4000-8000-000000000003")
PLACE_B_ID = uuid.UUID("00000000-0000-4000-8000-000000000004")
TRIP_ID = uuid.UUID("00000000-0000-4000-8000-000000000005")
GENERATION_ID = uuid.UUID("00000000-0000-4000-8000-000000000006")
DAY_ID = uuid.UUID("00000000-0000-4000-8000-000000000007")
RAG_DOCUMENT_ID = uuid.UUID("00000000-0000-4000-8000-000000000008")


async def _insert(session: AsyncSession, row: Base) -> None:
    # The models declare no relationships, so the unit of work does not order inserts by foreign
    # key; each row is flushed in dependency order instead.
    session.add(row)
    await session.flush()


async def _write_one_row_per_table(session: AsyncSession) -> None:
    await insert_auth_user(session, USER_ID)
    await _insert(session, Profile(id=USER_ID))
    await _insert(
        session,
        Destination(
            id=DESTINATION_ID,
            slug="rls-check",
            name="RLS check (SAMPLE)",
            country_code="GB",
            timezone="Europe/London",
            currency="GBP",
            center_lat=Decimal("51.5"),
            center_lon=Decimal("-0.1"),
            bbox_min_lat=Decimal("51.0"),
            bbox_max_lat=Decimal("52.0"),
            bbox_min_lon=Decimal("-1.0"),
            bbox_max_lon=Decimal("1.0"),
            is_sample=True,
        ),
    )
    await _insert(
        session,
        DataSource(id=SOURCE_ID, name="RLS check source", source_type="other", licence="none"),
    )
    for place_id, name in ((PLACE_A_ID, "Place A"), (PLACE_B_ID, "Place B")):
        await _insert(
            session,
            Place(
                id=place_id,
                destination_id=DESTINATION_ID,
                source_id=SOURCE_ID,
                name=name,
                category="sight",
                lat=Decimal("51.5"),
                lon=Decimal("-0.1"),
                typical_duration_min=60,
            ),
        )
    await _insert(session, PlaceOpeningHours(place_id=PLACE_A_ID, weekday=1, is_closed=True))
    await _insert(
        session,
        Trip(
            id=TRIP_ID,
            user_id=USER_ID,
            destination_id=DESTINATION_ID,
            title="RLS check trip",
            start_date=date(2026, 11, 2),
            end_date=date(2026, 11, 3),
        ),
    )
    await _insert(session, TripPreferences(trip_id=TRIP_ID))
    await _insert(session, TripPlace(trip_id=TRIP_ID, place_id=PLACE_A_ID, relation="saved"))
    await _insert(session, BudgetSettings(trip_id=TRIP_ID))
    await _insert(
        session,
        AiGeneration(
            id=GENERATION_ID,
            trip_id=TRIP_ID,
            user_id=USER_ID,
            provider="MOCK",
            model_id="mock",
            prompt_template_id="itinerary",
            prompt_version="v1",
            mapping_version="v1",
            scope="full",
            request_hash="0" * 64,
        ),
    )
    await _insert(
        session,
        ItineraryDay(
            id=DAY_ID,
            trip_id=TRIP_ID,
            day_number=1,
            plan_date=date(2026, 11, 2),
            source_generation_id=GENERATION_ID,
        ),
    )
    await _insert(
        session,
        ItineraryItem(
            trip_id=TRIP_ID,
            day_id=DAY_ID,
            position=1,
            place_id=PLACE_A_ID,
            start_time=time(9, 0),
            duration_min=60,
            origin="user",
        ),
    )
    await _insert(
        session,
        ItineraryWarning(
            trip_id=TRIP_ID, plan_revision=0, code="DAY_TOO_LONG", severity="warning", message="x"
        ),
    )
    await _insert(
        session,
        ItineraryVersion(
            trip_id=TRIP_ID,
            version_no=1,
            reason="edit",
            plan_revision=0,
            snapshot={"schema": "snap-1", "plan_revision": 0, "days": []},
            created_by=USER_ID,
        ),
    )
    await _insert(
        session,
        RouteCache(
            from_place_id=PLACE_A_ID,
            to_place_id=PLACE_B_ID,
            mode="walking",
            travel_minutes=5,
            distance_m=400,
            travel_source="fallback_estimate",
            expires_at=datetime.now(UTC) + timedelta(days=30),
        ),
    )
    await _insert(
        session,
        RagDocument(
            id=RAG_DOCUMENT_ID,
            destination_id=DESTINATION_ID,
            kind="guide",
            source_id=SOURCE_ID,
            doc_key="guide:rls-check/sample",
            title="RLS check guide (SAMPLE)",
            content_sha256="0" * 64,
        ),
    )
    await _insert(
        session,
        RagChunk(
            document_id=RAG_DOCUMENT_ID,
            chunk_index=0,
            content="SAMPLE chunk.",
            content_sha256="0" * 64,
            token_estimate=3,
        ),
    )


async def _readable_rows(session: AsyncSession, role: str, table: str) -> int:
    """Rows of public.<table> that ``role`` can read; a refused read counts as zero."""
    savepoint = await session.begin_nested()
    try:
        # SET LOCAL and set_config(..., true) end with the savepoint, so the next read starts clean.
        await session.execute(
            text("select set_config('request.jwt.claim.sub', :sub, true)"), {"sub": str(USER_ID)}
        )
        await session.execute(text(f"set local role {role}"))
        result = await session.execute(text(f'select count(*) from public."{table}"'))  # noqa: S608  # name from pg_tables
        return int(result.scalar_one())
    except ProgrammingError as exc:
        if isinstance(exc.orig, errors.InsufficientPrivilege):
            return 0
        raise
    finally:
        await savepoint.rollback()


@pytest.mark.asyncio
async def test_rls_browser_roles_read_zero_rows(db_session: AsyncSession) -> None:
    await _write_one_row_per_table(db_session)

    tables = (
        (
            await db_session.execute(
                text("select tablename from pg_tables where schemaname = 'public' order by 1")
            )
        )
        .scalars()
        .all()
    )
    assert set(tables) == set(metadata.tables) | {"alembic_version"}

    # The privileged test connection sees a row in every table, so a zero below means "blocked".
    for table in tables:
        query = text(f'select count(*) from public."{table}"')  # noqa: S608  # name from pg_tables
        count = (await db_session.execute(query)).scalar_one()
        assert count >= 1, f"{table} has no row to read"

    readable = {
        (role, table): await _readable_rows(db_session, role, table)
        for role in BROWSER_ROLES
        for table in tables
    }
    assert {key: rows for key, rows in readable.items() if rows != 0} == {}
