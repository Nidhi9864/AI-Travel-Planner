"""Cost shapes of app/budget/schemas.py (§6.5 CostSummaryOut, §6.6.6 API-34).

Pure: no database. BudgetSettingsPatch is the API-34 request body; the other shapes are
responses built by the budget engine.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.budget.schemas import AmountRange, BudgetSettingsPatch, BudgetStatus


def test_empty_patch_is_allowed() -> None:
    patch = BudgetSettingsPatch()
    assert patch.model_dump(exclude_unset=True) == {}


def test_patch_accepts_valid_values() -> None:
    patch = BudgetSettingsPatch(
        transport_allowance_per_day="300", stay_budget_per_night="1500.50", contingency_pct=10
    )
    assert patch.transport_allowance_per_day == Decimal("300")
    assert patch.model_dump(mode="json")["stay_budget_per_night"] == "1500.50"


def test_patch_null_clears_an_amount() -> None:
    patch = BudgetSettingsPatch.model_validate({"stay_budget_per_night": None})
    assert patch.model_dump(exclude_unset=True) == {"stay_budget_per_night": None}


@pytest.mark.parametrize("field", ["transport_allowance_per_day", "stay_budget_per_night"])
def test_patch_rejects_negative_amounts(field: str) -> None:
    with pytest.raises(ValidationError):
        BudgetSettingsPatch.model_validate({field: "-1.00"})


@pytest.mark.parametrize("pct", [0, 25, 50])
def test_patch_contingency_bounds_pass(pct: int) -> None:
    assert BudgetSettingsPatch(contingency_pct=pct).contingency_pct == pct


@pytest.mark.parametrize("pct", [-1, 51, 100])
def test_patch_contingency_out_of_bounds_raises(pct: int) -> None:
    with pytest.raises(ValidationError):
        BudgetSettingsPatch(contingency_pct=pct)


def test_patch_forbids_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        BudgetSettingsPatch.model_validate({"currency": "INR"})


def test_patch_rejects_three_decimal_amount() -> None:
    with pytest.raises(ValidationError):
        BudgetSettingsPatch(transport_allowance_per_day="10.005")


def test_amount_range_serialises_strings() -> None:
    assert AmountRange(min="100", max="250.5").model_dump(mode="json") == {
        "min": "100.00",
        "max": "250.50",
    }


@pytest.mark.xfail(
    strict=True, reason="F-2 in UNIT_TEST_REPORT.md: AmountRange has no min <= max check"
)
def test_amount_range_rejects_min_above_max() -> None:
    # An estimate range whose minimum is above its maximum is meaningless (§9.3.1).
    with pytest.raises(ValidationError):
        AmountRange(min="500", max="100")


@pytest.mark.xfail(
    strict=True, reason="F-3 in UNIT_TEST_REPORT.md: BudgetStatus does not enforce the excess rule"
)
def test_budget_status_excess_only_when_exceeded() -> None:
    # The field description says excess is null unless the status is exceeded.
    BudgetStatus(amount="1000", status="exceeded", ratio_pct=120, excess="200")
    with pytest.raises(ValidationError):
        BudgetStatus(amount="1000", status="near", ratio_pct=90, excess="200")


@pytest.mark.parametrize("status", ["over", "EXCEEDED", ""])
def test_budget_status_rejects_unknown_status(status: str) -> None:
    with pytest.raises(ValidationError):
        BudgetStatus(amount=None, status=status, ratio_pct=None, excess=None)  # type: ignore[arg-type]  # deliberately invalid
