"""Generation pipeline, walking skeleton (§8.2 steps 1, 7, 8, 9 and 11; IMP-210).

mark_running -> provider.generate_itinerary -> mark_validating -> io-1 and place-ID checks ->
save the plan and complete the record in one transaction. Each status change is its own short
transaction, and none stays open across the provider call (§5.8). Retrieval, routing, costs, the
validator rules, repair and the rule-based fallback arrive with IMP-303 to IMP-502.

Never logged: the request built for the provider, its raw output, notes or prompt text (FR-125).
"""

import logging
import time
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from typing import Final
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.errors import ProviderError
from app.ai.providers.base import ModelProvider
from app.generation import repository, request_builder
from app.itinerary import service as itinerary_service
from app.schemas.ai import GenerationRequest, ItineraryOutput

logger = logging.getLogger(__name__)

Sessions = Callable[[], AbstractAsyncContextManager[AsyncSession]]

# The skeleton runs no validator rules, so the plan is saved with no findings.
NO_FINDINGS: Final = {"errors": 0, "warnings": 0, "infos": 0}


def output_problem(output: ItineraryOutput, request: GenerationRequest) -> str | None:
    """Why an answer cannot be saved (schema, day numbers or place IDs), or None."""
    try:
        ItineraryOutput.model_validate(output.model_dump())
    except ValidationError:
        return "schema"
    day_numbers = [day.day_number for day in output.days]
    if len(set(day_numbers)) != len(day_numbers) or max(day_numbers) > request.trip.num_days:
        return "day_numbers"
    if output.unknown_place_ids(request):
        return "unknown_place_ids"
    return None


async def run(generation_id: UUID, provider: ModelProvider, sessions: Sessions) -> None:
    started = time.perf_counter()

    def elapsed_ms() -> int:
        return round((time.perf_counter() - started) * 1000)

    async with sessions() as session:
        row = await repository.mark_running(session, generation_id)
        trip_id, user_id = row.trip_id, row.user_id
        request = await request_builder.build(
            session,
            trip_id=trip_id,
            user_id=user_id,
            prompt_template_id=row.prompt_template_id,
            prompt_version=row.prompt_version,
        )

    try:
        result = await provider.generate_itinerary(request)
    except ProviderError as exc:
        logger.warning("generation %s provider error %s", generation_id, exc.failure_reason)
        async with sessions() as session:
            await repository.fail(
                session, generation_id, exc.failure_reason, latency_ms=elapsed_ms()
            )
        return

    async with sessions() as session:
        await repository.mark_validating(session, generation_id)

    problem = output_problem(result.output, request)
    if problem is not None:
        logger.warning("generation %s invalid output: %s", generation_id, problem)
        async with sessions() as session:
            await repository.fail(
                session,
                generation_id,
                "invalid_output",
                usage=result.usage,
                latency_ms=elapsed_ms(),
            )
        return

    metadata = provider.get_model_metadata()
    async with sessions() as session:
        await itinerary_service.save_generated_plan(
            session, trip_id, user_id, result.output, generation_id, validation_summary=NO_FINDINGS
        )
        await repository.complete(
            session,
            generation_id,
            outcome="model",
            usage=result.usage,
            latency_ms=elapsed_ms(),
            validation_summary=NO_FINDINGS,
            adapter_version=metadata.adapter_version,
            model_version=metadata.model_version,
        )
    logger.info("generation %s completed in %d ms", generation_id, elapsed_ms())
