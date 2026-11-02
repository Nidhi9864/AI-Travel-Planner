"""Routing service (MOD-B10): the travel time between two consecutive places (§9.3.5, FR-079).

For now every travel time is the distance estimate of ``routing/estimate.py``. IMP-307 puts the
route cache and OpenRouteService in front of it (lookup order §9.3.5: cache, routing service,
estimate) without changing ``travel_time``'s signature; it is async for that reason. The places
are read from the arguments only: nothing here touches the database.
"""

from decimal import Decimal
from typing import Protocol

from app.routing.estimate import TravelEstimate, TravelMode, estimate


class Located(Protocol):
    """Anything with coordinates, such as a ``places`` row."""

    @property
    def lat(self) -> Decimal | float: ...
    @property
    def lon(self) -> Decimal | float: ...


async def travel_time(place_a: Located, place_b: Located, mode: TravelMode | str) -> TravelEstimate:
    """Travel time and distance from ``place_a`` to ``place_b`` with its source label."""
    return estimate(
        float(place_a.lat), float(place_a.lon), float(place_b.lat), float(place_b.lon), mode
    )
