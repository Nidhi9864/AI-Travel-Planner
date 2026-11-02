"""Distance-based travel-time estimate and buffers (app/routing/estimate.py, service.py; §9.3.5,
FR-079: TC-236, TC-237). Pure: no database and no network.
"""

import ast
import asyncio
import inspect
import math
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

import pytest

from app.routing import estimate as estimate_module
from app.routing import service
from app.routing.estimate import (
    BUFFER_MIN,
    DETOUR_FACTOR,
    SPEED_M_PER_MIN,
    TravelEstimate,
    TravelMode,
    buffer_minutes,
    estimate,
    haversine_m,
)

# One degree of latitude on the 6,371 km sphere: 2 * pi * 6371000 / 360 metres.
ONE_DEGREE_LAT_M = 2 * math.pi * 6_371_000 / 360


@dataclass(frozen=True)
class Spot:
    lat: Decimal | float
    lon: Decimal | float


# ---------- §9.3.5 constants ----------


def test_the_constants_are_those_of_section_9_3_5() -> None:
    assert DETOUR_FACTOR == 1.3
    assert SPEED_M_PER_MIN == {
        TravelMode.WALKING: 75,
        TravelMode.LOCAL_TRANSPORT: 400,  # routed as driving-car, a driving mode
        TravelMode.CAR: 400,
    }
    assert {mode.value for mode in TravelMode} == {"walking", "local_transport", "car"}


# ---------- known distance pairs ----------


def test_one_degree_of_latitude_is_about_111_km() -> None:
    assert haversine_m(0, 0, 1, 0) == pytest.approx(ONE_DEGREE_LAT_M, rel=1e-12)
    assert haversine_m(12.30, 76.65, 13.30, 76.65) == pytest.approx(ONE_DEGREE_LAT_M, rel=1e-9)


def test_known_city_pair_distance() -> None:
    # Mysuru palace (12.3052, 76.6552) to Chamundi hill temple (12.2724, 76.6710): about 4 km.
    d = haversine_m(12.3052, 76.6552, 12.2724, 76.6710)
    assert 4_000 < d < 4_100


def test_the_distance_is_symmetric() -> None:
    assert haversine_m(12.30, 76.65, 12.31, 76.66) == pytest.approx(
        haversine_m(12.31, 76.66, 12.30, 76.65)
    )


@pytest.mark.parametrize(
    ("mode", "speed"),
    [(TravelMode.WALKING, 75), (TravelMode.LOCAL_TRANSPORT, 400), (TravelMode.CAR, 400)],
)
def test_minutes_follow_the_formula_for_each_mode(mode: TravelMode, speed: int) -> None:
    result = estimate(12.30, 76.65, 12.31, 76.65, mode)
    d = haversine_m(12.30, 76.65, 12.31, 76.65)
    assert result.distance_m == round(d)
    assert result.minutes == math.ceil(Fraction(13, 10) * round(d) / speed)
    assert result.mode is mode


def test_a_one_kilometre_walk() -> None:
    # 1,000 m north: 1.3 * 1000 / 75 = 17.33 -> 18 minutes; by car 1.3 * 1000 / 400 = 3.25 -> 4.
    lat = 1000 / ONE_DEGREE_LAT_M
    assert estimate(0, 0, lat, 0, "walking").minutes == 18
    assert estimate(0, 0, lat, 0, "car").minutes == 4
    assert estimate(0, 0, lat, 0, "car").distance_m == 1000


# ---------- rounding up ----------


def test_minutes_are_rounded_up() -> None:
    # 75 m walking: 1.3 * 75 / 75 = 1.3 -> 2 minutes, never 1.
    lat = 75 / ONE_DEGREE_LAT_M
    assert estimate(0, 0, lat, 0, "walking").minutes == 2
    # 1 m by car is still one minute.
    assert estimate(0, 0, 1 / ONE_DEGREE_LAT_M, 0, "car").minutes == 1


@pytest.mark.parametrize(("metres", "minutes"), [(750, 13), (1500, 26), (3000, 52)])
def test_an_exact_multiple_is_not_rounded_further(metres: int, minutes: int) -> None:
    # 1.3 * d / 75 is a whole number here; float error must not add a minute.
    assert estimate(0, 0, metres / ONE_DEGREE_LAT_M, 0, "walking").minutes == minutes


# ---------- identical points ----------


@pytest.mark.parametrize("mode", list(TravelMode))
def test_identical_points_give_zero(mode: TravelMode) -> None:
    result = estimate(12.3052, 76.6552, 12.3052, 76.6552, mode)
    assert (result.minutes, result.distance_m) == (0, 0)


# ---------- TC-236: the fallback label ----------


def test_tc_236_the_fallback_value_is_labelled_fallback_estimate_shown_as_estimate() -> None:
    result = estimate(12.30, 76.65, 12.31, 76.66, "walking")
    assert result.travel_source == "fallback_estimate"
    assert result.label == "Estimate"


def test_routing_values_are_labelled_estimate_only_for_local_transport() -> None:
    walking = TravelEstimate(
        minutes=10, distance_m=700, mode=TravelMode.WALKING, travel_source="routing_api"
    )
    transit = TravelEstimate(
        minutes=10, distance_m=700, mode=TravelMode.LOCAL_TRANSPORT, travel_source="routing_api"
    )
    assert walking.label is None
    assert transit.label == "Estimate"  # no transit timetables (§9.3.5)


def test_an_unknown_mode_is_refused() -> None:
    with pytest.raises(ValueError, match="bicycle"):
        estimate(0, 0, 1, 1, "bicycle")


# ---------- TC-237: buffers ----------


def test_tc_237_fallback_values_carry_15_minutes_and_routing_values_5() -> None:
    assert buffer_minutes("fallback_estimate") == 15
    assert buffer_minutes("routing_api") == 5
    assert BUFFER_MIN == {"routing_api": 5, "fallback_estimate": 15}
    result = estimate(12.30, 76.65, 12.31, 76.66, "car")
    assert buffer_minutes(result.travel_source) == 15


def test_an_unknown_travel_source_has_no_buffer() -> None:
    with pytest.raises(ValueError, match="unknown travel_source"):
        buffer_minutes("guess")  # type: ignore[arg-type]  # deliberately outside TravelSource


# ---------- purity and determinism ----------


def test_estimate_is_deterministic() -> None:
    results = {estimate(12.3052, 76.6552, 12.2724, 76.6710, "walking") for _ in range(50)}
    assert len(results) == 1


def test_the_estimate_module_imports_only_the_standard_library() -> None:
    tree = ast.parse(inspect.getsource(estimate_module))
    imported = {
        (node.module or "") if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    assert imported <= {"math", "dataclasses", "enum", "fractions", "typing"}


# ---------- routing service ----------


def test_the_service_returns_the_estimate_from_place_coordinates() -> None:
    a = Spot(Decimal("12.305200"), Decimal("76.655200"))
    b = Spot(Decimal("12.272400"), Decimal("76.671000"))
    result = asyncio.run(service.travel_time(a, b, "local_transport"))
    assert result == estimate(12.3052, 76.6552, 12.2724, 76.6710, "local_transport")
    assert result.travel_source == "fallback_estimate"


def test_the_service_signature_is_stable_for_imp_307() -> None:
    assert list(inspect.signature(service.travel_time).parameters) == ["place_a", "place_b", "mode"]
    assert inspect.iscoroutinefunction(service.travel_time)
