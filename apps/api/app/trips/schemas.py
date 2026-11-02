"""Trip and preference shapes (specification §6.5 TripIn / TripOut, PreferencesIn / PreferencesOut;
§6.6.2 API-07, 08, 10, 14, 15).

API names map to trips columns: title -> title, adults/children -> adults/children,
budget {amount, currency} -> budget_amount/budget_currency. The field rules live in
trips/domain.py; these models fix the types and forbid unknown fields (IMD-45).
"""

import re
from datetime import date
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

from app.places.vocabulary import OfferedCategory
from app.schemas.common import Money, UtcTimestamp
from app.trips.domain import GroupNeed
from app.trips.preference_mapping import (
    AccommodationType,
    BudgetPriority,
    Effect,
    Pace,
    TransportPref,
)


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


# ---------- Preferences (§6.5 PreferencesIn / PreferencesOut; API-14, API-15) ----------

MAX_MUST_VISIT = 10  # IMD-40
NOTES_MAX_CHARS = 1000
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _no_duplicates[T](values: list[T]) -> list[T]:
    if len(set(values)) != len(values):
        raise ValueError("each value can be listed only once")
    return values


def _clean_notes(value: str | None) -> str | None:
    # §6.5: control characters are removed (line breaks and tabs stay); the text is otherwise
    # stored as the traveller wrote it and reaches the model only as quoted data (§8.6).
    return None if value is None else _CONTROL_CHARACTERS.sub("", value)


class PreferencesIn(BaseModel):
    """API-14 body: a full replacement; omitted fields take the table defaults."""

    model_config = ConfigDict(extra="forbid")

    interests: Annotated[list[OfferedCategory], AfterValidator(_no_duplicates)] = Field(
        default_factory=list, description="Place categories except stay (IMD-40)"
    )
    pace: Pace = Pace.BALANCED
    budget_priority: BudgetPriority = BudgetPriority.BALANCED
    transport_pref: TransportPref = TransportPref.WALKING
    accommodation_type: AccommodationType = AccommodationType.ANY
    step_free_required: bool = False
    notes: Annotated[str | None, AfterValidator(_clean_notes)] = Field(
        None,
        max_length=NOTES_MAX_CHARS,
        description="Free text, at most 1,000 characters; do not enter personal details",
    )
    must_visit_place_ids: Annotated[list[UUID], AfterValidator(_no_duplicates)] = Field(
        default_factory=list,
        max_length=MAX_MUST_VISIT,
        description="At most 10 active places of the trip's destination (IMD-40)",
    )


class MustVisitPlace(BaseModel):
    id: UUID
    name: str


class PreferenceEffect(BaseModel):
    field: str
    effect: Effect


class PreferencesOut(BaseModel):
    interests: list[OfferedCategory]
    pace: Pace
    budget_priority: BudgetPriority
    transport_pref: TransportPref
    accommodation_type: AccommodationType
    step_free_required: bool
    notes: str | None
    must_visit_place_ids: list[UUID]
    must_visit_places: list[MustVisitPlace] = Field(
        description="The must-visit places that are active, with their names"
    )
    effects: list[PreferenceEffect] = Field(description="What each field does in planning (pm-1)")
    saved: bool = Field(description="False when no preferences were saved yet (defaults shown)")
