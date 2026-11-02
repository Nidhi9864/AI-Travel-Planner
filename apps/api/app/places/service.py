"""Places service (MOD-B04): read-only use cases behind API-06 and API-16 (basic) (§6.6.3).

The session is the request's transaction (app.auth.deps.DbSession), as in trips/service.py. Only
active destinations and places are read; nothing is written here (the seed is the only writer).
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.places import repository
from app.places.schemas import Destination, PlaceSummary
from app.schemas.common import Page


async def list_destinations(session: AsyncSession) -> list[Destination]:
    """API-06: the active destinations, ordered by name."""
    return [Destination.from_row(row) for row in await repository.active_destinations(session)]


async def search_places(
    session: AsyncSession,
    destination_id: UUID,
    *,
    q: str | None,
    categories: Sequence[str],
    limit: int,
    offset: int,
) -> Page[PlaceSummary]:
    """API-16 basic: active places of an active destination by name, category and page.

    An inactive or unknown destination gives an empty page (PD-IMP-205-7).
    """
    rows, total = await repository.search_places(
        session,
        destination_id,
        q=q.strip() if q else None,
        categories=categories,
        limit=limit,
        offset=offset,
    )
    return Page[PlaceSummary](
        items=[PlaceSummary.from_row(row) for row in rows], total=total, limit=limit, offset=offset
    )


async def active_place_names(
    session: AsyncSession, destination_id: UUID, place_ids: Sequence[UUID]
) -> dict[UUID, str]:
    """Name by id of the given places that are active in the destination, ordered by name.

    Used by the trips module (IMP-204) to check must-visit places and to name them; an id that
    is missing, inactive or of another destination is simply absent from the result.
    """
    rows = await repository.active_places_by_ids(session, destination_id, place_ids)
    return {row.id: row.name for row in rows}
