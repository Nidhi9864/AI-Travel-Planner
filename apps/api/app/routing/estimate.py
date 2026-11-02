"""Distance-based travel-time estimate and transfer buffers (specification §9.3.5, FR-079, IMD-30).

Pure: no I/O and no framework imports (§4.4 "Pure domain", checked by ``make imports``). Used
whenever no cached or routing value exists: the result is labelled ``fallback_estimate`` and shown
as Estimate, and the validator adds the larger buffer after it.

- d = haversine distance between the two points, in whole metres;
- minutes = ceil(1.3 · d / v), computed exactly, with v = 75 m/min walking and 400 m/min for the
  driving modes (``car`` and ``local_transport``, which §9.3.5 routes as ``driving-car``);
- buffer: 5 minutes after ``routing_api``, 15 minutes after ``fallback_estimate``.

All numbers are Proposed (§9.3.5) and are calibrated against routing results in Sprint 3.
"""

import math
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction
from typing import Final, Literal


class TravelMode(StrEnum):
    """itinerary_items.travel_mode (migration 0004)."""

    WALKING = "walking"
    LOCAL_TRANSPORT = "local_transport"
    CAR = "car"


TravelSource = Literal["routing_api", "fallback_estimate"]

# Proposed (§9.3.5): detour factor between straight-line and street distance.
DETOUR_FACTOR: Final = 1.3
# Proposed (§9.3.5): metres per minute; local_transport uses the driving speed (driving-car).
SPEED_M_PER_MIN: Final[dict[TravelMode, int]] = {
    TravelMode.WALKING: 75,
    TravelMode.LOCAL_TRANSPORT: 400,
    TravelMode.CAR: 400,
}
# Proposed (§9.3.5, FR-079 AC2): minutes added after a travel time of each source.
BUFFER_MIN: Final[dict[str, int]] = {"routing_api": 5, "fallback_estimate": 15}

EARTH_RADIUS_M: Final = 6_371_000.0
ESTIMATE_LABEL: Final = "Estimate"


@dataclass(frozen=True)
class TravelEstimate:
    minutes: int
    distance_m: int
    mode: TravelMode
    travel_source: TravelSource = "fallback_estimate"

    @property
    def label(self) -> str | None:
        """The Estimate label for a fallback value (FR-079 AC1) and for local_transport, which
        has no transit timetables (§9.3.5); None for a routing value of the other modes."""
        if self.travel_source == "fallback_estimate" or self.mode is TravelMode.LOCAL_TRANSPORT:
            return ESTIMATE_LABEL
        return None


def haversine_m(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> float:
    """Great-circle distance in metres on a sphere of radius 6,371 km."""
    phi1, phi2 = math.radians(from_lat), math.radians(to_lat)
    d_phi = phi2 - phi1
    d_lambda = math.radians(to_lon - from_lon)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(a)))


def estimate(
    from_lat: float, from_lon: float, to_lat: float, to_lon: float, mode: TravelMode | str
) -> TravelEstimate:
    """The labelled fallback travel time and distance between two points (§9.3.5)."""
    travel_mode = TravelMode(mode)
    distance_m = round(haversine_m(from_lat, from_lon, to_lat, to_lon))
    # Exact arithmetic on the whole-metre distance (the stored travel_from_prev_m), so float error
    # never adds a minute: 1500 m walking is exactly 26 minutes, not 27.
    exact = Fraction(str(DETOUR_FACTOR)) * distance_m / SPEED_M_PER_MIN[travel_mode]
    return TravelEstimate(minutes=math.ceil(exact), distance_m=distance_m, mode=travel_mode)


def buffer_minutes(travel_source: TravelSource) -> int:
    """The transfer buffer after a travel time from this source (FR-079 AC2)."""
    try:
        return BUFFER_MIN[travel_source]
    except KeyError:
        raise ValueError(f"unknown travel_source {travel_source!r}") from None
