"""Place routes API-06 and API-16 (basic) (specification §6.6.3; FR-007, FR-016, FR-019).

Mounted under /api/v1, whose router requires CurrentUser (IMP-108): reference data still needs a
token (§6.2). API-16 has the basic filters the must-visit picker needs (destination_id, q,
category, paging); IMP-509 and IMP-604 add the others. The handlers only call places/service.py.

API-17 (IMP-604) and API-19 to API-21 (IMP-605) are declared with their final shapes and answer
501 NOT_IMPLEMENTED until those cards build them (IMD-37).
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.auth.deps import DbSession
from app.core.errors import EndpointNotImplemented
from app.places import service
from app.places.schemas import Destination, PlaceOut, PlaceSummary
from app.places.vocabulary import OfferedCategory
from app.schemas.common import Page

router = APIRouter(tags=["places"])


@router.get(
    "/destinations",
    response_model=list[Destination],
    summary="API-06 List the supported destinations",
)
async def list_destinations(session: DbSession) -> list[Destination]:
    return await service.list_destinations(session)


@router.get("/places", response_model=Page[PlaceSummary], summary="API-16 Search places")
async def search_places(
    session: DbSession,
    destination_id: UUID,
    q: Annotated[str | None, Query(min_length=1, max_length=80)] = None,
    category: Annotated[list[OfferedCategory] | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[PlaceSummary]:
    return await service.search_places(
        session,
        destination_id,
        q=q,
        categories=[c.value for c in category or []],
        limit=limit,
        offset=offset,
    )


@router.get("/places/{place_id}", response_model=PlaceOut, summary="API-17 Read one place")
async def get_place(place_id: UUID, trip_id: UUID | None = None) -> PlaceOut:
    raise EndpointNotImplemented()


@router.put(
    "/trips/{trip_id}/saved-places/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="API-19 Save a place to my trip",
)
async def save_place(trip_id: UUID, place_id: UUID) -> None:
    raise EndpointNotImplemented()


@router.delete(
    "/trips/{trip_id}/saved-places/{place_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="API-20 Remove a saved place from my trip",
)
async def unsave_place(trip_id: UUID, place_id: UUID) -> None:
    raise EndpointNotImplemented()


@router.get(
    "/trips/{trip_id}/saved-places",
    response_model=list[PlaceSummary],
    summary="API-21 List my trip's saved places",
)
async def list_saved_places(trip_id: UUID) -> list[PlaceSummary]:
    raise EndpointNotImplemented()
