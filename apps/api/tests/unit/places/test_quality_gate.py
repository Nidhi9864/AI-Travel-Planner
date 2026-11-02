"""Quality gate rules of app/places/quality_gate.py (§5.6; FR-019, FR-022, FR-023; IMP-205).

TC-111 (outside the bounding box), TC-112 (unparseable hours), TC-113 (shortfall, with the report
renderer), TC-102 (unknown suitability is None, never False). Pure: no database, no files.
"""

from datetime import date, time
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

from app.places import import_pipeline, quality_gate, vocabulary
from app.places.quality_gate import DestinationBox, HoursLine, PlaceRow, SourceRecord

BOX = DestinationBox(
    min_lat=Decimal("53.85"),
    max_lat=Decimal("53.95"),
    min_lon=Decimal("2.1"),
    max_lon=Decimal("2.3"),
)
SOURCE = SourceRecord(
    name="SAMPLE fixture (synthetic)",
    source_type="other",
    licence="synthetic test data",
    attribution_text=None,
    url=None,
    retrieved_on=date(2026, 10, 31),
    notes="synthetic",
)
VALID_CELLS = {
    "external_ref": "sample-001",
    "source_name": SOURCE.name,
    "name": "Sample Harbour Lookout (sample)",
    "category": "sight",
    "tags": "views;outdoor",
    "description": "Synthetic sight place for tests (sample).",
    "address": "",
    "lat": "53.868000",
    "lon": "2.115000",
    "typical_duration_min": "60",
    "price_min": "0.00",
    "price_max": "5.00",
    "price_currency": "GBP",
    "price_label": "estimate",
    "hours_label": "estimate",
    "hours_checked_on": "",
    "verification_status": "estimated",
    "step_free": "true",
    "child_friendly": "",
    "indoor": "false",
    "website_url": "",
    "booking_url": "",
}
MONDAY = {
    "external_ref": "sample-001",
    "weekday": "1",
    "is_closed": "false",
    "open_time": "09:00",
    "close_time": "17:00",
    "closes_next_day": "false",
}


def hours(**changes: str) -> HoursLine:
    return HoursLine(line=2, cells={**MONDAY, **changes})


def row(
    source: SourceRecord | None = SOURCE,
    hours_lines: tuple[HoursLine, ...] = (HoursLine(line=2, cells=MONDAY),),
    **changes: str,
) -> PlaceRow:
    return PlaceRow(line=2, cells={**VALID_CELLS, **changes}, source=source, hours=hours_lines)


def rejects(place: PlaceRow) -> list[str]:
    return quality_gate.check(place, BOX).rejects


def test_a_valid_row_is_accepted_with_typed_values() -> None:
    result = quality_gate.check(row(), BOX)
    assert result.accepted
    assert result.flags == []
    assert result.values["lat"] == Decimal("53.868000")
    assert result.values["typical_duration_min"] == 60
    assert result.values["tags"] == ["views", "outdoor"]
    assert result.hours == [(1, False, time(9, 0), time(17, 0), False)]
    assert result.values["hours_label"] == "estimate"


# FR-022 AC1, TC-108: provenance


def test_tc_108_a_row_without_a_known_source_is_rejected() -> None:
    assert rejects(row(source=None, source_name="Nobody")) == [
        "source 'Nobody' is not in sources.csv"
    ]
    assert rejects(row(source=None, source_name="")) == ["source_name is missing"]


def test_a_source_without_a_licence_is_rejected() -> None:
    unlicensed = SourceRecord(**{**SOURCE.__dict__, "licence": None})
    assert rejects(row(source=unlicensed)) == [f"source {SOURCE.name!r} has no licence"]


def test_a_source_without_a_retrieved_date_is_rejected() -> None:
    undated = SourceRecord(**{**SOURCE.__dict__, "retrieved_on": None})
    assert rejects(row(source=undated)) == [f"source {SOURCE.name!r} has no retrieved date"]


def test_tc_108_a_row_without_verification_status_is_rejected() -> None:
    assert rejects(row(verification_status="")) == ["verification_status is missing"]
    assert rejects(row(verification_status="verified")) == [
        "verification_status 'verified' is not allowed"
    ]


def test_a_row_without_external_ref_is_rejected() -> None:
    assert rejects(row(external_ref="")) == ["external_ref is missing"]


# FR-023 AC1, TC-111: coordinates


@pytest.mark.parametrize(
    ("lat", "lon"),
    [("53.849999", "2.2"), ("53.950001", "2.2"), ("53.9", "2.099"), ("53.9", "2.31")],
)
def test_tc_111_coordinates_outside_the_bounding_box_are_rejected(lat: str, lon: str) -> None:
    [reason] = rejects(row(lat=lat, lon=lon))
    assert "outside the destination bounding box" in reason


def test_coordinates_on_the_box_edge_are_inside() -> None:
    assert rejects(row(lat="53.85", lon="2.3")) == []


def test_missing_or_malformed_coordinates_are_rejected() -> None:
    assert rejects(row(lat="")) == ["lat and lon are required"]
    assert rejects(row(lon="east")) == ["lon is not a number: 'east'"]


# Category and tags (FR-019 AC1)


def test_an_unknown_category_is_rejected() -> None:
    assert rejects(row(category="beach")) == ["category 'beach' is not in the vocabulary"]


def test_stay_is_in_the_vocabulary_but_not_offered() -> None:
    assert rejects(row(category="stay")) == []
    assert "stay" in vocabulary.CATEGORIES
    assert "stay" not in vocabulary.OFFERED_CATEGORIES
    assert {"stay"} == vocabulary.CATEGORIES - vocabulary.OFFERED_CATEGORIES


def test_an_unknown_tag_is_rejected() -> None:
    assert rejects(row(tags="views;sunbathing;karaoke")) == [
        "tags not in the vocabulary: sunbathing, karaoke"
    ]


def test_the_budget_tags_are_in_the_vocabulary() -> None:
    assert rejects(row(tags="child_half;child_free;price_per_group")) == []


# Prices


def test_price_min_above_price_max_is_rejected() -> None:
    assert rejects(row(price_min="9.00", price_max="5.00")) == ["price_max is below price_min"]


def test_a_negative_price_is_rejected() -> None:
    assert rejects(row(price_min="-1.00")) == ["price_min is negative"]


def test_a_price_without_currency_is_rejected() -> None:
    assert rejects(row(price_currency="")) == ["a price is given without price_currency"]


def test_a_price_with_label_unavailable_is_rejected() -> None:
    assert rejects(row(price_label="unavailable")) == [
        "price_label is unavailable but a price is given"
    ]


def test_a_priced_label_without_a_price_is_rejected() -> None:
    assert rejects(row(price_min="", price_max="", price_currency="")) == [
        "price_label estimate needs price_min"
    ]


def test_no_price_with_label_unavailable_is_accepted() -> None:
    place = row(price_min="", price_max="", price_currency="", price_label="unavailable")
    assert rejects(place) == []


# Duration


@pytest.mark.parametrize("minutes", ["14", "481", "0"])
def test_a_duration_outside_15_to_480_is_rejected(minutes: str) -> None:
    [reason] = rejects(row(typical_duration_min=minutes))
    assert "outside 15 to 480" in reason


@pytest.mark.parametrize("minutes", ["15", "480"])
def test_the_duration_limits_are_inclusive(minutes: str) -> None:
    assert rejects(row(typical_duration_min=minutes)) == []


def test_a_missing_duration_is_rejected() -> None:
    assert rejects(row(typical_duration_min="")) == ["typical_duration_min is missing"]


# Values the places table would refuse


def test_name_and_description_limits() -> None:
    assert rejects(row(name="")) == ["name is missing"]
    assert rejects(row(name="x" * 161)) == ["name is longer than 160 characters"]
    assert rejects(row(description="x" * 601)) == ["description is longer than 600 characters"]


def test_labels_must_be_known() -> None:
    assert rejects(row(hours_label="live")) == ["hours_label 'live' is not allowed"]
    assert rejects(row(hours_label="curated")) == ["hours_label curated needs hours_checked_on"]
    assert rejects(row(hours_label="curated", hours_checked_on="2026-10-01")) == []


# FR-019 AC2, TC-102: suitability


def test_tc_102_unknown_suitability_is_none_never_false() -> None:
    result = quality_gate.check(row(step_free="", child_friendly="", indoor=""), BOX)
    assert result.accepted
    assert (result.values["step_free"], result.values["child_friendly"]) == (None, None)
    assert result.values["indoor"] is None


def test_explicit_suitability_values_are_kept() -> None:
    result = quality_gate.check(row(step_free="TRUE", indoor="false"), BOX)
    assert (result.values["step_free"], result.values["indoor"]) == (True, False)


def test_a_suitability_value_that_is_not_true_or_false_is_rejected() -> None:
    assert rejects(row(step_free="yes")) == ["step_free must be true, false or empty: 'yes'"]


def test_the_suitability_flags_are_the_three_columns() -> None:
    assert vocabulary.SUITABILITY_FLAGS == ("step_free", "child_friendly", "indoor")


# FR-023 AC2, TC-112: opening hours


@pytest.mark.parametrize(
    "bad",
    [
        {"open_time": "9am"},
        {"weekday": "8"},
        {"weekday": "Mon"},
        {"close_time": ""},
        {"close_time": "08:00"},
        {"is_closed": "true"},
        {"is_closed": "maybe"},
    ],
    ids=[
        "time format",
        "weekday range",
        "weekday text",
        "no close time",
        "closes before it opens",
        "closed with times",
        "closed flag",
    ],
)
def test_tc_112_unparseable_hours_flag_the_row_and_store_unavailable(bad: dict[str, str]) -> None:
    result = quality_gate.check(row(hours_lines=(hours(**bad),)), BOX)
    assert result.accepted  # the place is kept
    assert result.hours == []
    assert result.values["hours_label"] == "unavailable"
    [flag] = result.flags
    assert flag.startswith("hours not parseable (opening_hours.csv line 2")


def test_hours_past_midnight_and_closed_days_parse() -> None:
    late = hours(open_time="18:00", close_time="02:00", closes_next_day="true")
    closed = HoursLine(
        line=3,
        cells={**MONDAY, "weekday": "2", "is_closed": "true", "open_time": "", "close_time": ""},
    )
    result = quality_gate.check(row(hours_lines=(late, closed)), BOX)
    assert result.flags == []
    assert [(r[0], r[1], r[4]) for r in result.hours] == [(1, False, True), (2, True, False)]


def test_the_same_slot_twice_is_unparseable() -> None:
    result = quality_gate.check(row(hours_lines=(hours(), hours())), BOX)
    assert result.hours == []
    assert "twice" in result.flags[0]


def test_no_hours_rows_label_the_place_unavailable_without_a_flag() -> None:
    result = quality_gate.check(row(hours_lines=()), BOX)
    assert result.accepted
    assert result.flags == []
    assert result.values["hours_label"] == "unavailable"


def test_every_failing_rule_is_listed_at_once() -> None:
    place = row(source=None, verification_status="", category="beach", typical_duration_min="5")
    assert len(rejects(place)) == 4


# FR-023 AC3, TC-113: shortfall in the report


def prepared(minimum: int | None, accepted: int, rejected: int = 0) -> Any:
    rows = [
        import_pipeline.CheckedRow(
            line=n + 2, source_name=SOURCE.name, result=quality_gate.check(row(), BOX)
        )
        for n in range(accepted)
    ]
    rows += [
        import_pipeline.CheckedRow(
            line=n + 100,
            source_name=None,
            result=quality_gate.check(row(source=None, source_name="Nobody"), BOX),
        )
        for n in range(rejected)
    ]
    return import_pipeline.Prepared(
        directory=Path("unused"),
        destination={"slug": "sampleton", "name": "Sampleton (sample)"},
        min_usable_places=minimum,
        sources=[SOURCE],
        rows=rows,
        hours_rows_read=accepted,
    )


def test_tc_113_a_shortfall_is_stated_in_the_report() -> None:
    item = prepared(minimum=30, accepted=25, rejected=2)
    assert item.shortfall == 5
    report = import_pipeline.render_report(item)
    assert "Shortfall: 25 usable places, 5 below the minimum of 30." in report
    assert "| Rejected | 2 |" in report
    assert "source 'Nobody' is not in sources.csv" in report


def test_the_report_states_a_met_minimum_and_a_missing_one() -> None:
    assert "Minimum met: 30 usable places" in import_pipeline.render_report(prepared(30, 30))
    assert prepared(30, 30).shortfall == 0
    assert "No minimum is set" in import_pipeline.render_report(prepared(None, 3))
    assert prepared(None, 3).shortfall == 0
