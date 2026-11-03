"""The itinerary tables (migration 0004): itinerary_days, itinerary_items, itinerary_warnings and
itinerary_versions, plus trips.plan_revision (§5.2), written only by MOD-B08 (§3). Every function
takes the caller's session and opens no transaction of its own. budget_settings is only read.
"""

from datetime import date, time, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    BudgetSettings,
    ItineraryDay,
    ItineraryItem,
    ItineraryVersion,
    ItineraryWarning,
    Trip,
)
from app.schemas.ai import ItineraryOutput


async def lock_trip(session: AsyncSession, trip_id: UUID, user_id: UUID) -> Trip | None:
    query = (
        select(Trip)
        .where(Trip.id == trip_id, Trip.user_id == user_id, Trip.deleted_at.is_(None))
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    return await session.scalar(query)


async def replace_plan(
    session: AsyncSession,
    trip_id: UUID,
    start_date: date,
    output: ItineraryOutput,
    *,
    origin: str,
    generation_id: UUID,
) -> list[dict[str, Any]]:
    """Replace the trip's days, items and warnings with the output; returns the snap-1 days.

    Times and durations are stored as the output gives them; cost and travel columns stay null
    until the budget engine and routing fill them (IMP-308).
    """
    await session.execute(delete(ItineraryWarning).where(ItineraryWarning.trip_id == trip_id))
    # Items go with their day (foreign key on delete cascade).
    await session.execute(delete(ItineraryDay).where(ItineraryDay.trip_id == trip_id))
    snapshot_days: list[dict[str, Any]] = []
    for day in sorted(output.days, key=lambda d: d.day_number):
        plan_date = start_date + timedelta(days=day.day_number - 1)
        day_row = ItineraryDay(
            trip_id=trip_id,
            day_number=day.day_number,
            plan_date=plan_date,
            theme=day.theme or None,
            source_generation_id=generation_id,
        )
        session.add(day_row)
        await session.flush()
        items: list[dict[str, Any]] = []
        for position, item in enumerate(day.items, start=1):
            note = item.note or None
            values: dict[str, Any] = {
                "position": position,
                "slot_type": item.slot_type,
                "duration_min": item.duration_min,
                "origin": origin,
                "note": note,
                "note_origin": "ai" if note else "none",
                "is_locked": False,
            }
            session.add(
                ItineraryItem(
                    trip_id=trip_id,
                    day_id=day_row.id,
                    place_id=UUID(item.place_id),
                    start_time=time.fromisoformat(item.start_time),
                    **values,
                )
            )
            items.append({"place_id": item.place_id, "start_time": item.start_time, **values})
        snapshot_days.append(
            {
                "day_number": day.day_number,
                "plan_date": plan_date.isoformat(),
                "theme": day_row.theme,
                "items": items,
            }
        )
    await session.flush()
    return snapshot_days


async def budget_settings_snapshot(session: AsyncSession, trip_id: UUID) -> dict[str, Any]:
    row = await session.get(BudgetSettings, trip_id)
    if row is None:
        return {}
    return {
        "transport_allowance_per_day": _amount(row.transport_allowance_per_day),
        "stay_budget_per_night": _amount(row.stay_budget_per_night),
        "contingency_pct": _amount(row.contingency_pct),
    }


def _amount(value: Any) -> str | None:
    return None if value is None else f"{value:.2f}"


async def mark_plan_saved(session: AsyncSession, trip_id: UUID) -> int:
    """plan_revision + 1, status ready, plan_stale false; returns the new plan_revision."""
    statement = (
        update(Trip)
        .where(Trip.id == trip_id)
        .values(
            plan_revision=Trip.plan_revision + 1,
            status="ready",
            plan_stale=False,
            updated_at=func.now(),
        )
        .returning(Trip.plan_revision)
    )
    return int((await session.execute(statement)).scalar_one())


async def insert_version(
    session: AsyncSession,
    trip_id: UUID,
    *,
    reason: str,
    plan_revision: int,
    snapshot: dict[str, Any],
    validation_summary: dict[str, Any],
    generation_id: UUID | None,
    created_by: UUID | None,
) -> UUID:
    """A version with version_no = the trip's highest + 1 (the trip row is locked by the caller)."""
    highest = await session.scalar(
        select(func.max(ItineraryVersion.version_no)).where(ItineraryVersion.trip_id == trip_id)
    )
    row = ItineraryVersion(
        trip_id=trip_id,
        version_no=(highest or 0) + 1,
        reason=reason,
        plan_revision=plan_revision,
        snapshot=snapshot,
        validation_summary=validation_summary,
        generation_id=generation_id,
        created_by=created_by,
    )
    session.add(row)
    await session.flush()
    return row.id


async def version_for_generation(
    session: AsyncSession, generation_id: UUID
) -> ItineraryVersion | None:
    query = (
        select(ItineraryVersion)
        .where(ItineraryVersion.generation_id == generation_id)
        .order_by(ItineraryVersion.version_no.desc())
        .limit(1)
    )
    return await session.scalar(query)
