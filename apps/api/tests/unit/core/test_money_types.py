"""Shared Money, MoneyAmount and UtcTimestamp types of app/schemas/common.py (§6.1, IMD-05).

Money travels as a string with exactly two decimals and an ISO 4217 code of three upper-case
letters; timestamps are UTC. Pure: no database.
"""

from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import BaseModel, ValidationError

from app.schemas.common import Money, Page, UtcTimestamp


class _Stamped(BaseModel):
    at: UtcTimestamp


@pytest.mark.parametrize(
    ("amount", "expected"),
    [("1230", "1230.00"), ("0", "0.00"), ("12.5", "12.50"), ("99.99", "99.99"), (7, "7.00")],
)
def test_money_serialises_with_two_decimals(amount: str | int, expected: str) -> None:
    dumped = Money(amount=amount, currency="INR").model_dump(mode="json")
    assert dumped == {"amount": expected, "currency": "INR"}


def test_money_rejects_more_than_two_decimals() -> None:
    with pytest.raises(ValidationError):
        Money(amount=Decimal("1.005"), currency="INR")


def test_money_rejects_more_than_twelve_digits() -> None:
    Money(amount=Decimal("9999999999.99"), currency="INR")  # 12 digits fits numeric(12,2)
    with pytest.raises(ValidationError):
        Money(amount=Decimal("99999999999.99"), currency="INR")


def test_money_forbids_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Money(amount="1", currency="INR", note="x")  # type: ignore[call-arg]  # deliberately invalid


def test_money_round_trips_from_json() -> None:
    money = Money.model_validate_json('{"amount": "450.00", "currency": "EUR"}')
    assert money.amount == Decimal("450.00")


@pytest.mark.xfail(
    strict=True, reason="F-1 in UNIT_TEST_REPORT.md: Money.currency has no pattern check"
)
@pytest.mark.parametrize("currency", ["inr", "IN", "INRR", "12A", ""])
def test_money_rejects_currency_that_is_not_three_upper_case_letters(currency: str) -> None:
    # The field description and migration 0002 (char(3) ~ '^[A-Z]{3}$') both require this.
    with pytest.raises(ValidationError):
        Money(amount="1.00", currency=currency)


def test_naive_timestamp_is_taken_as_utc() -> None:
    stamped = _Stamped(at=datetime(2026, 11, 3, 10, 30))
    assert stamped.at == datetime(2026, 11, 3, 10, 30, tzinfo=UTC)


def test_aware_timestamp_is_converted_to_utc() -> None:
    ist = timezone(timedelta(hours=5, minutes=30))
    stamped = _Stamped(at=datetime(2026, 11, 3, 16, 0, tzinfo=ist))
    assert stamped.at == datetime(2026, 11, 3, 10, 30, tzinfo=UTC)
    assert stamped.at.utcoffset() == timedelta(0)


def test_page_holds_typed_items() -> None:
    page = Page[Money](items=[Money(amount="1", currency="INR")], total=1, limit=20, offset=0)
    assert page.model_dump(mode="json")["items"] == [{"amount": "1.00", "currency": "INR"}]
