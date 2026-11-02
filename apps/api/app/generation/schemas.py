"""Generation shapes (specification §6.5 GenerationOut; §6.6.4 API-22, API-23; §6.6.5 API-30,
API-31; Amendment A1 §7.1 retrieval fields, IMD-116)."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.generation.records import FailureReason, GenerationStatus
from app.schemas.common import UtcTimestamp
from app.validation.schemas import ValidationSummary

GenerationMode = Literal["ai", "rule_based"]


class GenerationStartIn(BaseModel):
    """API-22 body; the scope is always full (IMD-21)."""

    model_config = ConfigDict(extra="forbid")

    mode: GenerationMode = "ai"


class RegenerateIn(BaseModel):
    """API-30 and API-31 body."""

    model_config = ConfigDict(extra="forbid")

    plan_revision: int
    mode: GenerationMode = "ai"


class GenerationOut(BaseModel):
    # Fields with a default still appear as required (nullable) in the response schema.
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    id: UUID
    trip_id: UUID
    scope: Literal["full", "day"]
    day_number: int | None
    mode: GenerationMode
    status: GenerationStatus
    outcome: Literal["model", "model_repaired", "fallback_rule_based", "failed"] | None
    failure_reason: FailureReason | None
    failure_message: str | None
    next_action: Literal["retry_rule_based", "edit_trip", "retry"] | None
    fallback_reason: FailureReason | None
    provider: str
    model_id: str
    prompt_version: str
    repair_attempts: int
    deterministic_repairs: int
    validation_summary: ValidationSummary
    latency_ms: int | None
    itinerary_version_id: UUID | None
    plan_revision: int | None
    created_at: UtcTimestamp
    completed_at: UtcTimestamp | None
    # A1 §7.1: declared in contract v1, null until IMP-316 fills them.
    retrieval_mode: Literal["vector", "lexical_fallback"] | None = Field(
        None, description="Null until retrieval is built (IMP-316)"
    )
    embedding_model_id: str | None = None
    retrieval_ms: int | None = None
