"""The ai_generations table (migration 0004). MOD-B06 is its only writer (§3).

Every function takes the caller's ``AsyncSession``; the generation service and job open it with
``app.db.session.transaction()``, one short transaction per status change (§8.16), and this module
opens no engine. The rules of ``generation/records.py`` are applied before a row is written, so an
illegal status change or a forbidden value raises and leaves the row as it was.

Never stored here: prompt text, the raw model response, traveller notes, e-mail or name (FR-038
AC3). ``cost_estimate_usd`` and ``cost_basis`` stay null until a dated cost basis exists.
"""

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFound
from app.db.models import AiGeneration
from app.generation import records
from app.generation.records import (
    CompletedOutcome,
    FailureReason,
    GenerationScope,
    GenerationStatus,
    TokenUsage,
)
from app.schemas.ai import ProviderName


async def create_queued(
    session: AsyncSession,
    *,
    trip_id: UUID,
    user_id: UUID,
    provider: ProviderName,
    model_id: str,
    prompt_template_id: str,
    prompt_version: str,
    mapping_version: str,
    scope: GenerationScope,
    request_hash: str,
    generation_settings: Mapping[str, Any] | None = None,
    scope_day_number: int | None = None,
) -> UUID:
    """Step 0 (§8.16): insert a queued generation and return its id.

    ``request_hash`` is ``records.request_hash(<canonical gr-1 request>)``; anything that is not a
    SHA-256 hex digest is refused, so request content cannot land in the column.
    """
    records.check_scope(scope, scope_day_number)
    records.check_request_hash(request_hash)
    row = AiGeneration(
        trip_id=trip_id,
        user_id=user_id,
        provider=provider,
        model_id=model_id,
        prompt_template_id=prompt_template_id,
        prompt_version=prompt_version,
        mapping_version=mapping_version,
        generation_settings=records.clean_generation_settings(generation_settings),
        scope=scope,
        scope_day_number=scope_day_number,
        status="queued",
        request_hash=request_hash,
    )
    session.add(row)
    await session.flush()
    return row.id


async def _locked(session: AsyncSession, generation_id: UUID) -> AiGeneration:
    query = (
        select(AiGeneration)
        .where(AiGeneration.id == generation_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    row = await session.scalar(query)
    if row is None:
        raise NotFound()
    return row


async def _advance(
    session: AsyncSession, generation_id: UUID, target: GenerationStatus, **values: Any
) -> AiGeneration:
    row = await _locked(session, generation_id)
    records.check_transition(row.status, target)
    row.status = target
    for name, value in values.items():
        setattr(row, name, value)
    await session.flush()
    await session.refresh(row)
    return row


async def mark_running(session: AsyncSession, generation_id: UUID) -> AiGeneration:
    """Step 1: queued -> running."""
    return await _advance(session, generation_id, "running")


async def mark_validating(session: AsyncSession, generation_id: UUID) -> AiGeneration:
    """Steps 8 and 9: running (or repairing, after a repair) -> validating."""
    return await _advance(session, generation_id, "validating")


async def mark_repairing(session: AsyncSession, generation_id: UUID) -> AiGeneration:
    """Step 10: validating -> repairing."""
    return await _advance(session, generation_id, "repairing")


async def complete(
    session: AsyncSession,
    generation_id: UUID,
    *,
    outcome: CompletedOutcome,
    usage: TokenUsage | None,
    latency_ms: int | None,
    repair_attempts: int = 0,
    deterministic_repairs: int = 0,
    validation_summary: Mapping[str, Any] | None = None,
    adapter_version: str | None = None,
    model_version: str | None = None,
) -> AiGeneration:
    """Step 11: validating or repairing -> completed, with failure_reason null (IMD-22).

    A provider failure that led to the rule-based fallback goes in
    ``validation_summary["provider_failure"]``, never in failure_reason.
    """
    records.check_outcome(outcome)
    return await _advance(
        session,
        generation_id,
        "completed",
        outcome=outcome,
        failure_reason=None,
        latency_ms=latency_ms,
        repair_attempts=repair_attempts,
        deterministic_repairs=deterministic_repairs,
        validation_summary=dict(validation_summary or {}),
        adapter_version=adapter_version,
        model_version=model_version,
        completed_at=func.now(),
        **records.usage_columns(usage),
    )


async def fail(
    session: AsyncSession,
    generation_id: UUID,
    failure_reason: FailureReason,
    *,
    usage: TokenUsage | None = None,
    latency_ms: int | None = None,
    validation_summary: Mapping[str, Any] | None = None,
) -> AiGeneration:
    """Any active status -> failed, with outcome failed and the failure reason (§8.14)."""
    records.check_failure_reason(failure_reason)
    values: dict[str, Any] = {
        "outcome": "failed",
        "failure_reason": failure_reason,
        "latency_ms": latency_ms,
        "completed_at": func.now(),
        **records.usage_columns(usage),
    }
    if validation_summary is not None:
        values["validation_summary"] = dict(validation_summary)
    return await _advance(session, generation_id, "failed", **values)


async def find_active_for_trip(session: AsyncSession, trip_id: UUID) -> AiGeneration | None:
    """The trip's newest generation in queued, running, validating or repairing, if any."""
    query = (
        select(AiGeneration)
        .where(
            AiGeneration.trip_id == trip_id,
            AiGeneration.status.in_(sorted(records.ACTIVE_STATUSES)),
        )
        .order_by(AiGeneration.created_at.desc(), AiGeneration.id)
        .limit(1)
    )
    return await session.scalar(query)


async def get_for_user(session: AsyncSession, generation_id: UUID, user_id: UUID) -> AiGeneration:
    """The caller's generation; another user's or a missing one is NotFound (404, never 403)."""
    query = select(AiGeneration).where(
        AiGeneration.id == generation_id, AiGeneration.user_id == user_id
    )
    row = await session.scalar(query)
    if row is None:
        raise NotFound()
    return row
