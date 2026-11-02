"""Itinerary, edit and version shapes (specification §6.5 ItineraryOut, Day, Item, Totals,
EditResultOut, VersionOut; §6.6.5 API-09, API-24 to API-29, API-32, API-35 to API-38;
Amendment A1 §7.1 SourceRef, IMD-116).

Times are HH:MM in the destination time zone; every amount comes from the budget engine. Fields
marked ai_written carry model text only (FR-035).
"""

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.budget.schemas import AmountRange, CostSummaryOut
from app.places.schemas import PlaceSummary
from app.places.vocabulary import Category, SourceLabel
from app.routing.estimate import TravelMode, TravelSource
from app.schemas.ai import HHMM, DayNumber, DurationMin, SlotType
from app.schemas.common import MoneyAmount, UtcTimestamp
from app.trips.schemas import TripOut
from app.validation.schemas import Finding, ValidationSummary

GenerationOutcome = Literal["model", "model_repaired", "fallback_rule_based", "failed"]


class LatestItineraryOut(BaseModel):
    """API-09: trip_id is null when the caller has no itinerary (FR-014 AC2)."""

    trip_id: UUID | None
    plan_revision: int | None
    updated_at: UtcTimestamp | None


class SourceRef(BaseModel):
    """A retrieved source behind an item (A1 §7.1); filled by IMP-316."""

    chunk_id: UUID
    kind: Literal["place", "guide"]
    title: str
    source_name: str
    licence: str
    attribution_text: str | None
    url: str | None
    retrieved_on: date | None


class ItemPlace(BaseModel):
    id: UUID
    name: str
    category: Category
    lat: float
    lon: float
    hours_label: SourceLabel


class ItemCost(BaseModel):
    min: MoneyAmount
    max: MoneyAmount
    currency: str
    label: SourceLabel


class TravelLeg(BaseModel):
    minutes: int
    distance_m: int
    mode: TravelMode
    source: TravelSource


class Item(BaseModel):
    # `sources` has a default but is always present in the response schema (A1 §7.1).
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    id: UUID
    position: int
    place: ItemPlace
    slot_type: SlotType
    start_time: HHMM
    duration_min: int
    end_time: HHMM
    origin: Literal["model", "fallback_rule_based", "user"]
    is_locked: bool
    must_visit: bool
    note: str | None = Field(description="ai_written when note_origin is ai")
    note_origin: Literal["ai", "user", "none"]
    cost: ItemCost | None
    travel_from_previous: TravelLeg | None
    sources: list[SourceRef] = Field(
        default_factory=list, description="Empty until retrieval is built (IMP-316)"
    )


class DayCost(BaseModel):
    min: MoneyAmount
    max: MoneyAmount
    currency: str
    complete: bool


class Day(BaseModel):
    day_number: int
    date: date
    theme: str | None = Field(description="ai_written when theme_origin is ai")
    theme_origin: Literal["ai", "none"]
    items: list[Item]
    day_cost: DayCost


class ItinerarySource(BaseModel):
    generation_id: UUID
    provider: str
    outcome: GenerationOutcome


class Totals(BaseModel):
    currency: str
    estimate: AmountRange
    planning_total: MoneyAmount
    complete: bool
    incomplete_count: int


class ItineraryOut(BaseModel):
    trip_id: UUID
    plan_revision: int
    version_id: UUID | None
    is_current: bool
    plan_stale: bool
    source: ItinerarySource | None
    days: list[Day]
    findings: list[Finding]
    totals: Totals


class EditResultOut(BaseModel):
    plan_revision: int
    changed_days: list[Day]
    totals: Totals
    findings: list[Finding]


# ---------- Edit bodies (API-25 to API-29) ----------


class ItemAddIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_revision: int
    day_number: DayNumber
    place_id: UUID
    position: Annotated[int, Field(ge=1)] | None = None
    start_time: HHMM | None = None
    duration_min: DurationMin | None = None


class ItemPatchIn(BaseModel):
    """API-26: move, retime, lock or unlock; at least one change."""

    model_config = ConfigDict(extra="forbid")

    plan_revision: int
    day_number: DayNumber | None = None
    position: Annotated[int, Field(ge=1)] | None = None
    start_time: HHMM | None = None
    duration_min: DurationMin | None = None
    is_locked: bool | None = None


class Alternative(BaseModel):
    place: PlaceSummary
    cost_delta: AmountRange
    time_delta_min: int
    reason: str


class AlternativesOut(BaseModel):
    item_id: UUID
    alternatives: list[Alternative] = Field(max_length=3)
    message: str | None = Field(description="'No alternative fits' when the list is empty")


class ReplaceIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_revision: int
    place_id: UUID


class PlanRevisionIn(BaseModel):
    """API-32 and API-38 body."""

    model_config = ConfigDict(extra="forbid")

    plan_revision: int


class ValidateOut(BaseModel):
    plan_revision: int
    findings: list[Finding]
    validation_summary: ValidationSummary


class TripSummaryOut(BaseModel):
    """API-35: the print view (FR-094)."""

    trip: TripOut
    days: list[Day]
    unresolved_findings: list[Finding]
    costs: CostSummaryOut
    generated_at: UtcTimestamp


# ---------- Versions (API-36 to API-38) ----------


class VersionCreateIn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    plan_revision: int
    name: str = Field(min_length=1, max_length=60)


class VersionOut(BaseModel):
    id: UUID
    version_no: int
    name: str | None
    reason: Literal["generation", "regeneration", "edit", "restore", "fallback", "manual"]
    kind: Literal["named", "automatic"]
    plan_revision: int
    validation_summary: ValidationSummary
    generation_id: UUID | None
    created_at: UtcTimestamp
