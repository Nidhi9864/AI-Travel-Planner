"""Itinerary service (MOD-B08): the only writer of the plan (§3, IMD-13).

``save_generated_plan`` is step 11 of the pipeline (§8.2): it runs in the caller's transaction,
which also completes the generation record, so the plan, the version and the record are saved
together or not at all (NFR-008).
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.itinerary import repository
from app.schemas.ai import ItineraryOutput

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
