"""The trips table (migration 0003). MOD-B03 is its only writer (§3, §5.2).

Every trip query takes the caller's user_id and filters by it and by deleted_at IS NULL, so a
foreign, missing or soft-deleted trip looks the same: absent (CLAUDE.md §4 rule 4, FR-005).
destinations and itinerary_days are only read here.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Destination, ItineraryDay, Trip


@dataclass(frozen=True)
class TripRow:
    trip: Trip
    destination: Destination
    has_itinerary: bool


def _owned_trips(user_id: UUID) -> Select[Trip, Destination, bool]:
    has_itinerary = exists().where(ItineraryDay.trip_id == Trip.id).label("has_itinerary")
    return (
        select(Trip, Destination, has_itinerary)
        .join(Destination, Destination.id == Trip.destination_id)
        .where(Trip.user_id == user_id, Trip.deleted_at.is_(None))
    )


async def active_destinations(session: AsyncSession) -> Sequence[Destination]:
    query = select(Destination).where(Destination.is_active.is_(True)).order_by(Destination.name)
    return (await session.scalars(query)).all()


async def insert_trip(
    session: AsyncSession,
    user_id: UUID,
    *,
    title: str,
    destination_id: UUID,
    start_date: date,
    end_date: date,
    adults: int,
    children: int,
    group_needs: list[str],
    budget_amount: Decimal | None,
    budget_currency: str | None,
) -> UUID:
    """Insert a draft trip with plan_revision 0 (API-07) and return its id."""
    trip = Trip(
        user_id=user_id,
        title=title,
        destination_id=destination_id,
        start_date=start_date,
        end_date=end_date,
        adults=adults,
        children=children,
        group_needs=group_needs,
        budget_amount=budget_amount,
        budget_currency=budget_currency,
        status="draft",
        plan_revision=0,
    )
    session.add(trip)
    await session.flush()
    return trip.id


async def get_owned(session: AsyncSession, user_id: UUID, trip_id: UUID) -> TripRow | None:
    # populate_existing reloads the server-side defaults of a trip inserted in this session.
    query = (
        _owned_trips(user_id).where(Trip.id == trip_id).execution_options(populate_existing=True)
    )
    row = (await session.execute(query)).one_or_none()
    return None if row is None else TripRow(row[0], row[1], bool(row[2]))


async def list_owned(
    session: AsyncSession, user_id: UUID, *, limit: int, offset: int, include_archived: bool
) -> tuple[list[TripRow], int]:
    """One page of the caller's trips, newest first (index ix_trips_user), and the total."""
    owned = _owned_trips(user_id)
    if not include_archived:
        owned = owned.where(Trip.status != "archived")
    total = await session.scalar(select(func.count()).select_from(owned.subquery()))
    query = (
        owned.order_by(Trip.updated_at.desc(), Trip.created_at.desc(), Trip.id)
        .limit(limit)
        .offset(offset)
    )
    rows = [TripRow(r[0], r[1], bool(r[2])) for r in (await session.execute(query)).all()]
    return rows, int(total or 0)
