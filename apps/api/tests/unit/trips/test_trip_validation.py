"""Trip input rules of app/trips/domain.py (§6.5 TripIn, §9.3.2; FR-008: TC-071, TC-072, TC-073).

Pure rules: no database, no app.
"""

import uuid
from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import pytest

from app.trips import domain
from app.trips.domain import FieldError, SupportedDestination, TripDraft

START = date(2026, 12, 4)
SAMPLETON = SupportedDestination(id=uuid.uuid4(), name="Sampleton (sample)", currency="GBP")


def valid_draft(**changes: Any) -> TripDraft:
    draft = TripDraft(
        title="Weekend in Sampleton",
        destination_id=SAMPLETON.id,
        start_date=START,
        end_date=START + timedelta(days=2),
        adults=2,
        children=1,
        group_needs=["children"],
        budget_amount=Decimal("15000.00"),
        budget_currency="GBP",
    )
    return replace(draft, **changes)


def fields(errors: list[FieldError]) -> list[str]:
    return [error.field for error in errors]


def test_a_valid_trip_has_no_errors() -> None:
    assert domain.validate_trip(valid_draft()) == []
    assert domain.validate_destination(SAMPLETON.id, [SAMPLETON]) == []


def test_tc_071_end_before_start_names_end_date() -> None:
    errors = domain.validate_trip(valid_draft(end_date=START - timedelta(days=1)))
    assert errors == [FieldError("end_date", "End date must be on or after start date.")]


def test_a_one_day_trip_is_allowed() -> None:
    assert domain.validate_trip(valid_draft(end_date=START)) == []


def test_tc_072_fourteen_days_pass_fifteen_are_rejected_with_the_limit() -> None:
    assert domain.validate_trip(valid_draft(end_date=START + timedelta(days=13))) == []
    errors = domain.validate_trip(valid_draft(end_date=START + timedelta(days=14)))
    assert fields(errors) == ["end_date"]
    assert "14 days" in errors[0].message


def test_tc_072_the_maximum_is_configurable_but_never_above_the_database_check() -> None:
    errors = domain.validate_dates(START, START + timedelta(days=7), max_days=7)
    assert fields(errors) == ["end_date"]
    assert "7 days" in errors[0].message
    assert domain.validate_dates(START, START + timedelta(days=14), max_days=30) != []


def test_trip_length_counts_both_ends() -> None:
    assert domain.trip_length_days(START, START) == 1
    assert domain.trip_length_days(START, START + timedelta(days=2)) == 3


@pytest.mark.parametrize("amount", [Decimal("0"), Decimal("0.00"), Decimal("-1.00")])
def test_tc_073_a_budget_of_zero_or_less_is_rejected(amount: Decimal) -> None:
    errors = domain.validate_trip(valid_draft(budget_amount=amount))
    assert errors == [FieldError("budget.amount", "Budget must be greater than 0.")]


def test_no_budget_is_allowed() -> None:
    assert domain.validate_trip(valid_draft(budget_amount=None, budget_currency=None)) == []


def test_budget_amount_and_currency_come_together() -> None:
    assert fields(domain.validate_budget(Decimal("10.00"), None)) == ["budget.currency"]
    assert fields(domain.validate_budget(None, "GBP")) == ["budget.amount"]


@pytest.mark.parametrize("currency", ["gbp", "GB", "GBPX", "12A", ""])
def test_currency_must_be_three_upper_case_letters(currency: str) -> None:
    errors = domain.validate_trip(valid_draft(budget_currency=currency))
    assert fields(errors) == ["budget.currency"]


@pytest.mark.parametrize(
    ("adults", "children", "expected"),
    [
        (1, 0, []),
        (20, 20, []),
        (0, 0, ["adults"]),
        (21, 0, ["adults"]),
        (2, -1, ["children"]),
        (2, 21, ["children"]),
        (0, 21, ["adults", "children"]),
    ],
)
def test_traveller_counts(adults: int, children: int, expected: list[str]) -> None:
    assert fields(domain.validate_trip(valid_draft(adults=adults, children=children))) == expected


@pytest.mark.parametrize("title", ["", "   ", "x" * 121])
def test_title_is_1_to_120_characters_after_trimming(title: str) -> None:
    assert fields(domain.validate_trip(valid_draft(title=title))) == ["title"]


def test_a_title_of_120_characters_passes() -> None:
    assert domain.validate_trip(valid_draft(title="x" * 120)) == []


def test_group_needs_use_the_imd_40_vocabulary() -> None:
    every_need = ["children", "older_adults", "reduced_mobility"]
    assert [need.value for need in domain.GroupNeed] == every_need
    assert domain.validate_group_needs(every_need) == []
    assert domain.validate_group_needs([]) == []
    assert fields(domain.validate_group_needs(["pets"])) == ["group_needs"]
    assert fields(domain.validate_group_needs(["children", "children"])) == ["group_needs"]


def test_a_budget_in_the_destination_currency_passes() -> None:
    assert domain.validate_budget_currency("GBP", SAMPLETON) == []


def test_a_budget_in_another_valid_currency_names_budget_currency() -> None:
    errors = domain.validate_budget_currency("INR", SAMPLETON)
    assert errors == [
        FieldError(
            "budget.currency", "Budget currency must be GBP, the currency of Sampleton (sample)."
        )
    ]


def test_no_budget_needs_no_currency_match() -> None:
    assert domain.validate_budget_currency(None, SAMPLETON) == []


def test_a_malformed_currency_is_reported_once_by_the_format_rule() -> None:
    assert domain.validate_budget_currency("gbp", SAMPLETON) == []
    assert fields(domain.validate_budget(Decimal("10.00"), "gbp")) == ["budget.currency"]


def test_an_unknown_or_inactive_destination_lists_the_supported_ones() -> None:
    other = SupportedDestination(id=uuid.uuid4(), name="Otherville", currency="EUR")
    errors = domain.validate_destination(uuid.uuid4(), [SAMPLETON, other])
    assert fields(errors) == ["destination_id"]
    for destination in (SAMPLETON, other):
        assert destination.name in errors[0].message
        assert str(destination.id) in errors[0].message


def test_with_no_active_destination_every_destination_is_rejected() -> None:
    errors = domain.validate_destination(SAMPLETON.id, [])
    assert fields(errors) == ["destination_id"]


def test_every_failing_field_is_reported_at_once() -> None:
    draft = valid_draft(
        title="",
        end_date=START - timedelta(days=1),
        adults=0,
        group_needs=["pets"],
        budget_amount=Decimal("0"),
    )
    assert fields(domain.validate_trip(draft)) == [
        "title",
        "end_date",
        "adults",
        "group_needs",
        "budget.amount",
    ]
