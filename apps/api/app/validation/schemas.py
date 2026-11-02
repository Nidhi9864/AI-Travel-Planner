"""Finding and validation-summary shapes (specification §6.5 Finding, §8 finding codes).

Shared by the itinerary, generation and budget responses, so it lives with the validator that
produces the findings (MOD-B07) and none of those modules imports another's schemas in a cycle.
"""

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.ai import FindingCode, Severity


class Finding(BaseModel):
    id: UUID
    code: FindingCode
    severity: Severity
    message: str
    day_number: int | None
    item_id: UUID | None
    place_id: UUID | None = Field(description="Set only for MUST_VISIT_MISSING (IMD-42)")
    suggested_fix: str | None


class ValidationSummary(BaseModel):
    """Counts of the findings by severity."""

    errors: int
    warnings: int
    infos: int
