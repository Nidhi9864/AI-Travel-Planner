"""Itinerary, edit and version routes API-09, API-24 to API-29, API-32 and API-35 to API-38
(specification §6.6.5; IMD-18, IMD-23).

API-09 and API-24 are built (IMP-211). The others are declared with their final shapes and answer
501 NOT_IMPLEMENTED until their cards build them (IMD-37): IMP-408 (API-26, API-27), IMP-504
(API-25), IMP-505 (API-28, API-29), IMP-405 (API-32), IMP-609 (API-35), IMP-610 (API-36 to API-38).
API-30 and API-31 live in generation/router.py (IMD-13).
"""

from uuid import UUID

from fastapi import APIRouter, status

from app.auth.deps import CurrentUser, DbSession
from app.core.errors import EndpointNotImplemented
from app.itinerary import service
from app.itinerary.schemas import (
    AlternativesOut,
    EditResultOut,
    ItemAddIn,
    ItemPatchIn,
    ItineraryOut,
    LatestItineraryOut,
    PlanRevisionIn,
    ReplaceIn,
    TripSummaryOut,
    ValidateOut,
    VersionCreateIn,
    VersionOut,
)

router = APIRouter(tags=["itinerary"])


@router.get(
    "/itineraries/latest",
    response_model=LatestItineraryOut,
    summary="API-09 Find my most recently changed itinerary",
)
async def latest_itinerary(user: CurrentUser, session: DbSession) -> LatestItineraryOut:
    return await service.latest_itinerary(session, user.user_id)


@router.get(
    "/trips/{trip_id}/itinerary",
    response_model=ItineraryOut,
    summary="API-24 Read my trip's itinerary",
)
async def get_itinerary(
    trip_id: UUID, user: CurrentUser, session: DbSession, version_id: UUID | None = None
) -> ItineraryOut:
    return await service.get_itinerary(session, user.user_id, trip_id, version_id)


@router.post(
    "/trips/{trip_id}/itinerary/items",
    response_model=EditResultOut,
    summary="API-25 Add a place to a day",
)
async def add_item(trip_id: UUID, body: ItemAddIn) -> EditResultOut:
    raise EndpointNotImplemented()


@router.patch(
    "/itinerary/items/{item_id}",
    response_model=EditResultOut,
    summary="API-26 Move, retime, lock or unlock an item",
)
async def update_item(item_id: UUID, body: ItemPatchIn) -> EditResultOut:
    raise EndpointNotImplemented()


@router.delete(
    "/itinerary/items/{item_id}",
    response_model=EditResultOut,
    summary="API-27 Remove an item",
)
async def delete_item(item_id: UUID, plan_revision: int) -> EditResultOut:
    raise EndpointNotImplemented()


@router.get(
    "/itinerary/items/{item_id}/alternatives",
    response_model=AlternativesOut,
    summary="API-28 List alternatives for an item",
)
async def list_alternatives(item_id: UUID) -> AlternativesOut:
    raise EndpointNotImplemented()


@router.post(
    "/itinerary/items/{item_id}/replace",
    response_model=EditResultOut,
    summary="API-29 Replace an item with an alternative",
)
async def replace_item(item_id: UUID, body: ReplaceIn) -> EditResultOut:
    raise EndpointNotImplemented()


@router.post(
    "/trips/{trip_id}/itinerary/validate",
    response_model=ValidateOut,
    summary="API-32 Revalidate my trip's itinerary",
)
async def validate_itinerary(trip_id: UUID, body: PlanRevisionIn) -> ValidateOut:
    raise EndpointNotImplemented()


@router.get(
    "/trips/{trip_id}/summary",
    response_model=TripSummaryOut,
    summary="API-35 Read my trip's printable summary",
)
async def trip_summary(trip_id: UUID) -> TripSummaryOut:
    raise EndpointNotImplemented()


@router.get(
    "/trips/{trip_id}/versions",
    response_model=list[VersionOut],
    summary="API-36 List my trip's saved versions",
)
async def list_versions(trip_id: UUID) -> list[VersionOut]:
    raise EndpointNotImplemented()


@router.post(
    "/trips/{trip_id}/versions",
    response_model=VersionOut,
    status_code=status.HTTP_201_CREATED,
    summary="API-37 Save a named version",
)
async def create_version(trip_id: UUID, body: VersionCreateIn) -> VersionOut:
    raise EndpointNotImplemented()


@router.post(
    "/trips/{trip_id}/versions/{version_id}/restore",
    response_model=ItineraryOut,
    summary="API-38 Restore a saved version",
)
async def restore_version(trip_id: UUID, version_id: UUID, body: PlanRevisionIn) -> ItineraryOut:
    raise EndpointNotImplemented()
