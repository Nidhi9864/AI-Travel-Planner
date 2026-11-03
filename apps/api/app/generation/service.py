"""Generation service (MOD-B06): start a generation (API-22) and read its status (API-23).

Create rules of §6.4, in order: trip owned and not archived; trip complete; no current itinerary;
mode ai only (rule_based waits for IMP-402). The AI-notice check (IMP-305) and the daily caps
(IMP-511) are added by their cards. ``request_hash`` covers {trip_id, scope, day_number, mode,
plan_revision}: the same request while one is active returns that generation, a different one is
refused with GENERATION_IN_PROGRESS.
"""

from typing import Final
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import GENERATE_TEMPLATE_ID
from app.ai.prompts import registry
from app.ai.providers.base import ModelProvider
from app.core.errors import Conflict, GenerationInProgress, ValidationFailed
from app.db.models import AiGeneration
from app.generation import jobs, records, repository
from app.generation.schemas import GenerationOut, GenerationStartIn
from app.itinerary import service as itinerary_service
from app.schemas.common import ErrorDetail
from app.trips import preference_mapping
from app.trips import service as trips_service
from app.validation.schemas import ValidationSummary

RULE_BASED_MODEL_ID: Final = "rule_based_planner_v1"
TIMED_OUT_MESSAGE: Final = "Generation timed out."

# §6.4: failure_reason -> (failure_message, next_action).
FAILURE_TEXT: Final[dict[str, tuple[str, str]]] = {
    "provider_timeout": ("The AI service did not return a usable plan.", "retry_rule_based"),
    "provider_rate_limited": ("The AI service did not return a usable plan.", "retry_rule_based"),
    "provider_unavailable": ("The AI service did not return a usable plan.", "retry_rule_based"),
    "invalid_output": ("The AI service did not return a usable plan.", "retry_rule_based"),
    "provider_quota_exhausted": ("AI generation is paused for today.", "retry_rule_based"),
    "unresolved_validation": (
        "No plan satisfied the checks; adjust the trip or must-visit places.",
        "edit_trip",
    ),
    "config_error": ("The AI service is not available right now.", "retry_rule_based"),
    "internal": ("Something went wrong on our side.", "retry"),
}


async def start_generation(
    session: AsyncSession,
    user_id: UUID,
    trip_id: UUID,
    body: GenerationStartIn,
    provider: ModelProvider,
    submit: jobs.Submit,
) -> tuple[GenerationOut, bool]:
    """Returns the generation and whether it is new (202) rather than already active (200)."""
    await repository.lock_trip(session, trip_id, user_id)  # serialises concurrent starts
    trip = await trips_service.get_trip(session, user_id, trip_id)  # NotFound if not the caller's
    if trip.status == "archived":
        raise Conflict("This trip is archived. Restore it before generating a plan.")
    # Title, destination, dates and adults are NOT NULL and checked on save (FR-008); only the
    # preferences row can be missing (IMD-25).
    if not (await trips_service.get_preferences(session, user_id, trip_id)).saved:
        raise ValidationFailed(
            details=[ErrorDetail(field="preferences", message="Save the trip's preferences.")]
        )
    if trip.has_itinerary:
        raise Conflict("This trip already has an itinerary. Regenerate it instead.")
    if body.mode == "rule_based":
        raise ValidationFailed(
            details=[ErrorDetail(field="mode", message="Rule-based planning is not available yet.")]
        )

    request_hash = records.request_hash(
        {
            "trip_id": str(trip_id),
            "scope": "full",
            "day_number": None,
            "mode": body.mode,
            "plan_revision": trip.plan_revision,
        }
    )
    active = await repository.find_active_for_trip(session, trip_id)
    if active is not None:
        if active.request_hash != request_hash:
            raise GenerationInProgress()
        return await _to_out(session, active), False

    metadata = provider.get_model_metadata()
    template = registry.load(GENERATE_TEMPLATE_ID)
    generation_id = await repository.create_queued(
        session,
        trip_id=trip_id,
        user_id=user_id,
        provider=metadata.provider,
        model_id=metadata.model_id,
        prompt_template_id=template.template_id,
        prompt_version=template.version,
        mapping_version=preference_mapping.MAPPING_VERSION,
        scope="full",
        request_hash=request_hash,
    )
    row = await repository.get_for_user(session, generation_id, user_id)
    out = await _to_out(session, row)
    await session.commit()  # the job reads the row in its own transaction (§6.4)
    submit(generation_id, provider)
    return out, True


async def get_generation(
    session: AsyncSession, user_id: UUID, generation_id: UUID
) -> GenerationOut:
    row = await repository.get_for_user(session, generation_id, user_id)
    # Reaping refreshes this same row object in the session.
    await repository.fail_stale(
        session, jobs.STALE_AFTER, generation_id=generation_id, validation_summary=jobs.TIMED_OUT
    )
    return await _to_out(session, row)


async def _to_out(session: AsyncSession, row: AiGeneration) -> GenerationOut:
    summary = row.validation_summary or {}
    message, next_action = FAILURE_TEXT.get(row.failure_reason or "", (None, None))
    if summary.get("timed_out"):
        message = TIMED_OUT_MESSAGE
    saved = await itinerary_service.saved_plan_for_generation(session, row.id)
    return GenerationOut.model_validate(
        {
            "id": row.id,
            "trip_id": row.trip_id,
            "scope": row.scope,
            "day_number": row.scope_day_number,
            "mode": "rule_based" if row.model_id == RULE_BASED_MODEL_ID else "ai",
            "status": row.status,
            "outcome": row.outcome,
            "failure_reason": row.failure_reason,
            "failure_message": message,
            "next_action": next_action,
            "fallback_reason": summary.get("provider_failure"),
            "provider": row.provider,
            "model_id": row.model_id,
            "prompt_version": row.prompt_version,
            "repair_attempts": row.repair_attempts,
            "deterministic_repairs": row.deterministic_repairs,
            "validation_summary": ValidationSummary(
                errors=summary.get("errors", 0),
                warnings=summary.get("warnings", 0),
                infos=summary.get("infos", 0),
            ),
            "latency_ms": row.latency_ms,
            "itinerary_version_id": saved.version_id if saved else None,
            "plan_revision": saved.plan_revision if saved else None,
            "created_at": row.created_at,
            "completed_at": row.completed_at,
        }
    )
