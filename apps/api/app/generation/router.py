"""Generation routes API-22, API-23, API-30 and API-31 (specification §6.4, §6.6.4, §6.6.5; IMD-13).

API-22 and API-23 are built (IMP-210); API-30 and API-31 answer 501 NOT_IMPLEMENTED until IMP-607
builds them (IMD-37). API-22, API-30 and API-31 answer 202 for a new generation and 200 when the
same request is already active (FR-024 AC3).
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Response, status

from app.ai.factory import ModelProviderDep
from app.auth.deps import CurrentUser, DbSession
from app.core.errors import EndpointNotImplemented
from app.generation import service
from app.generation.jobs import SubmitDep
from app.generation.schemas import GenerationOut, GenerationStartIn, RegenerateIn
from app.schemas.ai import DayNumber

router = APIRouter(tags=["generation"])

_SAME_REQUEST_ACTIVE: dict[int | str, dict[str, Any]] = {
    200: {"model": GenerationOut, "description": "Same request already active"}
}


@router.post(
    "/trips/{trip_id}/generations",
    response_model=GenerationOut,
    status_code=status.HTTP_202_ACCEPTED,
    responses=_SAME_REQUEST_ACTIVE,
    summary="API-22 Start generating my trip's itinerary",
)
async def start_generation(
    trip_id: UUID,
    body: GenerationStartIn,
    user: CurrentUser,
    session: DbSession,
    provider: ModelProviderDep,
    submit: SubmitDep,
    response: Response,
) -> GenerationOut:
    out, created = await service.start_generation(
        session, user.user_id, trip_id, body, provider, submit
    )
    if not created:
        response.status_code = status.HTTP_200_OK
    return out


@router.get(
    "/generations/{generation_id}",
    response_model=GenerationOut,
    summary="API-23 Read a generation's status",
)
async def get_generation(
    generation_id: UUID, user: CurrentUser, session: DbSession
) -> GenerationOut:
    return await service.get_generation(session, user.user_id, generation_id)


@router.post(
    "/trips/{trip_id}/itinerary/days/{day_number}/regenerate",
    response_model=GenerationOut,
    status_code=status.HTTP_202_ACCEPTED,
    responses=_SAME_REQUEST_ACTIVE,
    summary="API-30 Regenerate one day",
)
async def regenerate_day(trip_id: UUID, day_number: DayNumber, body: RegenerateIn) -> GenerationOut:
    raise EndpointNotImplemented()


@router.post(
    "/trips/{trip_id}/itinerary/regenerate",
    response_model=GenerationOut,
    status_code=status.HTTP_202_ACCEPTED,
    responses=_SAME_REQUEST_ACTIVE,
    summary="API-31 Regenerate the whole itinerary",
)
async def regenerate_itinerary(trip_id: UUID, body: RegenerateIn) -> GenerationOut:
    raise EndpointNotImplemented()
