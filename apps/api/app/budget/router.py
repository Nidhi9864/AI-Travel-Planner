"""Cost routes API-33 and API-34 (specification §6.6.6; FR-071 to FR-075).

Declared with their final shapes; each answers 501 NOT_IMPLEMENTED until IMP-308 (API-33) and
IMP-411 (API-34) build it (IMD-37).
"""

from uuid import UUID

from fastapi import APIRouter

from app.budget.schemas import BudgetSettingsPatch, CostSummaryOut
from app.core.errors import EndpointNotImplemented

router = APIRouter(prefix="/trips/{trip_id}", tags=["costs"])


@router.get("/costs", response_model=CostSummaryOut, summary="API-33 Read my trip's costs")
async def get_costs(trip_id: UUID) -> CostSummaryOut:
    raise EndpointNotImplemented()


@router.patch(
    "/budget-settings",
    response_model=CostSummaryOut,
    summary="API-34 Update my trip's budget settings",
)
async def update_budget_settings(trip_id: UUID, body: BudgetSettingsPatch) -> CostSummaryOut:
    raise EndpointNotImplemented()
