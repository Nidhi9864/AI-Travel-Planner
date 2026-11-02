"""Trip request and response shapes (specification §6.5 TripIn / TripOut, §6.6.2 API-07, 08, 10).

API names map to trips columns: title -> title, adults/children -> adults/children,
budget {amount, currency} -> budget_amount/budget_currency. The field rules live in
trips/domain.py; these models fix the types and forbid unknown fields (IMD-45).
"""

from datetime import date
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money, UtcTimestamp
from app.trips.domain import GroupNeed


class TripStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    ARCHIVED = "archived"


class TripIn(BaseModel):
    """API-07 body. A field naming a user (user_id) is rejected with 422 (IMD-45)."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(description="1 to 120 characters, trimmed")
    destination_id: UUID = Field(description="An active destination (API-06)")
    start_date: date
    end_date: date = Field(description="On or after start_date; 1 to 14 days in total")
    adults: int = Field(1, description="1 to 20")
    children: int = Field(0, description="0 to 20")
    group_needs: list[GroupNeed] = Field(default_factory=list)
    budget: Money | None = Field(
        None, description="Group total; amount greater than 0 with an ISO 4217 currency"
    )


class TripDestination(BaseModel):
    id: UUID
    name: str
    timezone: str
    currency: str
    is_sample: bool


class TripOut(BaseModel):
    id: UUID
    title: str
    destination_id: UUID
    start_date: date
    end_date: date
    num_days: int
    adults: int
    children: int
    group_needs: list[GroupNeed]
    budget: Money | None
    status: TripStatus
    plan_revision: int
    plan_stale: bool
    has_itinerary: bool
    destination: TripDestination
    created_at: UtcTimestamp
    updated_at: UtcTimestamp
