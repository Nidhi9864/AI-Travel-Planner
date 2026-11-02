"""Cost shapes (specification §6.5 CostSummaryOut; §6.6.6 API-33, API-34; §9.3.1 BF-07 to BF-12).

Every amount is computed by budget/engine.py in minor units and travels as an IMD-05 string.
"""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import MoneyAmount
from app.validation.schemas import Finding

NonNegativeMoney = Annotated[MoneyAmount, Field(ge=0)]


class AmountRange(BaseModel):
    min: MoneyAmount
    max: MoneyAmount


class Contingency(BaseModel):
    pct: int
    amount: MoneyAmount


class PerTraveller(BaseModel):
    travellers: int
    largest_share: MoneyAmount
    label: Literal["average"]


class BudgetStatus(BaseModel):
    amount: MoneyAmount | None
    status: Literal["none", "near", "exceeded"]
    ratio_pct: int | None
    excess: MoneyAmount | None = Field(description="Null unless the status is exceeded")


class DayCostLine(BaseModel):
    day_number: int
    min: MoneyAmount
    max: MoneyAmount
    contingency_share: MoneyAmount


class CategoryCostLine(BaseModel):
    category: Literal["activities", "food", "transport", "accommodation", "other", "contingency"]
    min: MoneyAmount
    max: MoneyAmount
    label: Literal["curated", "estimate", "unavailable", "traveller_input"]


class BudgetSettingsOut(BaseModel):
    transport_allowance_per_day: MoneyAmount | None
    stay_budget_per_night: MoneyAmount | None
    contingency_pct: int


class CostSummaryOut(BaseModel):
    currency: str
    estimate: AmountRange
    contingency: Contingency
    planning_total: MoneyAmount
    per_traveller: PerTraveller
    budget: BudgetStatus
    by_day: list[DayCostLine]
    by_category: list[CategoryCostLine]
    alerts: list[Finding] = Field(description="BUDGET_NEAR and BUDGET_EXCEEDED findings")
    complete: bool
    incomplete_items: list[UUID]
    settings: BudgetSettingsOut


class BudgetSettingsPatch(BaseModel):
    """API-34 body: any of the three settings; an amount may be null to clear it."""

    model_config = ConfigDict(extra="forbid")

    transport_allowance_per_day: NonNegativeMoney | None = None
    stay_budget_per_night: NonNegativeMoney | None = None
    contingency_pct: int | None = Field(None, ge=0, le=50)
