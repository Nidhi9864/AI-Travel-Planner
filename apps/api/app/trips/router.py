"""Trip routes API-07, API-08 and API-10 (specification §6.6.2; FR-005, FR-007, FR-008).

Mounted under /api/v1, whose router requires CurrentUser (IMP-108); the user comes from the token.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.auth.deps import CurrentUser, DbSession
from app.schemas.common import Page
from app.trips import service
from app.trips.schemas import TripIn, TripOut

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post(
    "",
    response_model=TripOut,
    status_code=status.HTTP_201_CREATED,
    summary="API-07 Create a draft trip",
)
async def create_trip(body: TripIn, user: CurrentUser, session: DbSession) -> TripOut:
    return await service.create_trip(session, user.user_id, body)


@router.get("", response_model=Page[TripOut], summary="API-08 List my trips")
async def list_trips(
    user: CurrentUser,
    session: DbSession,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    include_archived: bool = False,
) -> Page[TripOut]:
    return await service.list_trips(
        session, user.user_id, limit=limit, offset=offset, include_archived=include_archived
    )


@router.get("/{trip_id}", response_model=TripOut, summary="API-10 Read one of my trips")
async def get_trip(trip_id: UUID, user: CurrentUser, session: DbSession) -> TripOut:
    return await service.get_trip(session, user.user_id, trip_id)
