"""Itinerary service (MOD-B08): the only writer of the plan (§3, IMD-13).

``save_generated_plan`` is step 11 of the pipeline (§8.2): it runs in the caller's transaction,
which also completes the generation record, so the plan, the version and the record are saved
together or not at all (NFR-008). ``get_itinerary`` (API-24) and ``latest_itinerary`` (API-09)
read the saved plan for its owner (IMP-211).
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.budget.schemas import AmountRange
from app.core.errors import EndpointNotImplemented, NotFound
from app.db.models import ItineraryItem, Place
from app.itinerary import repository
from app.itinerary.schemas import (
    Day,
    DayCost,
    Item,
    ItineraryOut,
    ItinerarySource,
    LatestItineraryOut,
    Totals,
)
from app.schemas.ai import ItineraryOutput
from app.trips import service as trips_service

SNAPSHOT_SCHEMA = "snap-1"


@dataclass(frozen=True)
class SavedPlan:
    version_id: UUID
    plan_revision: int


async def save_generated_plan(
    session: AsyncSession,
    trip_id: UUID,
    user_id: UUID,
    output: ItineraryOutput,
    generation_id: UUID,
    *,
    validation_summary: dict[str, Any],
) -> SavedPlan:
    trip = await repository.lock_trip(session, trip_id, user_id)
    if trip is None:
        raise NotFound()
    days = await repository.replace_plan(
        session, trip_id, trip.start_date, output, origin="model", generation_id=generation_id
    )
    plan_revision = await repository.mark_plan_saved(session, trip_id)
    snapshot = {
        "schema": SNAPSHOT_SCHEMA,
        "plan_revision": plan_revision,
        "days": days,
        "budget_settings": await repository.budget_settings_snapshot(session, trip_id),
    }
    version_id = await repository.insert_version(
        session,
        trip_id,
        reason="generation",
        plan_revision=plan_revision,
        snapshot=snapshot,
        validation_summary=validation_summary,
        generation_id=generation_id,
        created_by=user_id,
    )
    return SavedPlan(version_id=version_id, plan_revision=plan_revision)


async def saved_plan_for_generation(session: AsyncSession, generation_id: UUID) -> SavedPlan | None:
    """The version a generation saved, for API-23's itinerary_version_id and plan_revision."""
    version = await repository.version_for_generation(session, generation_id)
    return None if version is None else SavedPlan(version.id, version.plan_revision)


NO_ITINERARY = "No itinerary yet."
AI_OUTCOMES = frozenset({"model", "model_repaired"})
ZERO = Decimal("0.00")


async def get_itinerary(
    session: AsyncSession, user_id: UUID, trip_id: UUID, version_id: UUID | None = None
) -> ItineraryOut:
    """API-24: the trip's current plan; a missing or foreign trip and an empty plan answer 404."""
    trip = await trips_service.get_trip(session, user_id, trip_id)
    if version_id is not None:
        raise EndpointNotImplemented()  # reading a stored version is IMP-610 (IMD-37)
    days = await repository.plan_days(session, trip_id)
    if not days:
        raise NotFound(NO_ITINERARY)
    rows = await repository.plan_items(session, trip_id)
    generation = await repository.latest_completed_generation(session, trip_id)
    ai_text = generation is not None and generation.outcome in AI_OUTCOMES
    currency = trip.destination.currency

    items_by_day: dict[UUID, list[tuple[ItineraryItem, Place, bool]]] = {}
    for row in rows:
        items_by_day.setdefault(row[0].day_id, []).append(row)

    out_days = []
    for day in days:
        day_rows = items_by_day.get(day.id, [])
        out_days.append(
            Day(
                day_number=day.day_number,
                date=day.plan_date,
                theme=day.theme,
                theme_origin="ai" if ai_text and day.theme else "none",
                items=[_item(*row) for row in day_rows],
                day_cost=DayCost(**_cost_sum([item for item, _, _ in day_rows]), currency=currency),
            )
        )

    total = _cost_sum([item for item, _, _ in rows])
    incomplete = sum(1 for item, _, _ in rows if item.cost_min is None)
    return ItineraryOut(
        trip_id=trip.id,
        plan_revision=trip.plan_revision,
        version_id=await repository.latest_version_id(session, trip_id),
        is_current=True,
        plan_stale=trip.plan_stale,
        source=None
        if generation is None
        else ItinerarySource.model_validate(
            {
                "generation_id": generation.id,
                "provider": generation.provider,
                "outcome": generation.outcome,
            }
        ),
        days=out_days,
        findings=[],  # warnings of the revision arrive with the validator (IMP-405)
        totals=Totals(
            currency=currency,
            estimate=AmountRange(min=total["min"], max=total["max"]),
            # shortcut: no transport, stay or contingency lines yet (BF-05 to BF-09); the
            # budget engine of IMP-308 replaces these totals and fills the item costs.
            planning_total=total["max"],
            complete=total["complete"],
            incomplete_count=incomplete,
        ),
    )


def _cost_sum(items: list[ItineraryItem]) -> dict[str, Any]:
    """BF-04: an item without a stored cost counts as 0 and makes the sum incomplete."""
    return {
        "min": sum((item.cost_min or ZERO for item in items), ZERO),
        "max": sum((item.cost_max or ZERO for item in items), ZERO),
        "complete": all(item.cost_min is not None for item in items),
    }


def _item(item: ItineraryItem, place: Place, must_visit: bool) -> Item:
    start = datetime.combine(datetime.min, item.start_time)
    end = (start + timedelta(minutes=item.duration_min)).time()
    cost = None
    if item.cost_min is not None and item.cost_max is not None:
        cost = {
            "min": item.cost_min,
            "max": item.cost_max,
            "currency": item.cost_currency,
            "label": item.cost_label,
        }
    travel = None
    if item.travel_from_prev_min is not None:
        travel = {
            "minutes": item.travel_from_prev_min,
            "distance_m": item.travel_from_prev_m,
            "mode": item.travel_mode,
            "source": item.travel_source,
        }
    # Stored text columns are checked against the response vocabularies here.
    return Item.model_validate(
        {
            "id": item.id,
            "position": item.position,
            "place": {
                "id": place.id,
                "name": place.name,
                "category": place.category,
                "lat": float(place.lat),
                "lon": float(place.lon),
                "hours_label": place.hours_label,
            },
            "slot_type": item.slot_type,
            "start_time": item.start_time.strftime("%H:%M"),
            "duration_min": item.duration_min,
            "end_time": end.strftime("%H:%M"),
            "origin": item.origin,
            "is_locked": item.is_locked,
            "must_visit": must_visit,
            "note": item.note,
            "note_origin": item.note_origin,
            "cost": cost,
            "travel_from_previous": travel,
            "sources": [],  # A1 §7.1: filled from source_chunk_ids by IMP-316
        }
    )


async def latest_itinerary(session: AsyncSession, user_id: UUID) -> LatestItineraryOut:
    """API-09: the caller's most recently changed itinerary, or nulls when there is none."""
    found = await repository.latest_itinerary_for_user(session, user_id)
    if found is None:
        return LatestItineraryOut(trip_id=None, plan_revision=None, updated_at=None)
    trip_id, plan_revision, updated_at = found
    return LatestItineraryOut(trip_id=trip_id, plan_revision=plan_revision, updated_at=updated_at)
