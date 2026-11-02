"""Read-only queries over the place reference tables (MOD-B04; §6.6.3 API-06, API-16).

Destinations and places are shared reference data with no owner, so no query takes a user_id;
every query reads active rows only (§6.2: inactive destinations and places are invisible). Only
the seed writes these tables.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Destination, Place


async def active_destinations(session: AsyncSession) -> Sequence[Destination]:
    query = (
        select(Destination)
        .where(Destination.is_active.is_(True))
        .order_by(Destination.name, Destination.id)
    )
    return (await session.scalars(query)).all()


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


async def search_places(
    session: AsyncSession,
    destination_id: UUID,
    *,
    q: str | None,
    categories: Sequence[str],
    limit: int,
    offset: int,
) -> tuple[list[Place], int]:
    """One page of active places of an active destination, ordered by name, and the total.

    ``q`` matches anywhere in the name, case-insensitively; ``categories`` keeps places in any of
    them (index ix_places_dest_cat).
    """
    query = (
        select(Place)
        .join(Destination, Destination.id == Place.destination_id)
        .where(
            Place.destination_id == destination_id,
            Place.is_active.is_(True),
            Destination.is_active.is_(True),
        )
    )
    if q:
        query = query.where(Place.name.ilike(f"%{_escape_like(q)}%", escape="\\"))
    if categories:
        query = query.where(Place.category.in_(list(categories)))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    page = query.order_by(Place.name, Place.id).limit(limit).offset(offset)
    return list((await session.scalars(page)).all()), int(total or 0)
