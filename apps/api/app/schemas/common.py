"""Common API types: the error envelope of specification §6.3 and the shared Money, Page and
timestamp types of §6.1 and §6.5."""

from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, PlainSerializer

TWO_PLACES = Decimal("0.01")


def _two_decimals(value: Decimal) -> str:
    return str(value.quantize(TWO_PLACES))


# IMD-05: a money value travels as a string with exactly two decimals ("1230.00"); numeric(12,2)
# in the database bounds it to 12 digits, 2 after the point.
MoneyAmount = Annotated[
    Decimal,
    Field(max_digits=12, decimal_places=2),
    PlainSerializer(_two_decimals, return_type=str),
]


def _as_utc(value: datetime) -> datetime:
    # §6.1: timestamps are ISO 8601 UTC with Z; the database session may use another time zone.
    return value.astimezone(UTC) if value.tzinfo is not None else value.replace(tzinfo=UTC)


UtcTimestamp = Annotated[datetime, AfterValidator(_as_utc)]


class Money(BaseModel):
    """A money value next to its ISO 4217 currency code (§6.1, IMD-05)."""

    model_config = ConfigDict(extra="forbid")

    amount: MoneyAmount
    currency: str = Field(description="ISO 4217 code, three upper-case letters")


class Page[T](BaseModel):
    """One page of a paginated list (§6.1: API-08 and API-16 only)."""

    items: list[T]
    total: int
    limit: int
    offset: int


class ErrorCode(StrEnum):
    """Every error code of §6.3; the HTTP status of each is set by its exception in core.errors."""

    UNAUTHENTICATED = "UNAUTHENTICATED"
    NOT_FOUND = "NOT_FOUND"
    STALE_PLAN = "STALE_PLAN"
    GENERATION_IN_PROGRESS = "GENERATION_IN_PROGRESS"
    CONFLICT = "CONFLICT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_EDIT = "INVALID_EDIT"
    RATE_LIMITED = "RATE_LIMITED"
    AI_QUOTA_REACHED = "AI_QUOTA_REACHED"
    INTERNAL = "INTERNAL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class ErrorDetail(BaseModel):
    """One field problem; `message` is safe to show."""

    field: str
    message: str


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    request_id: str
    details: list[ErrorDetail] = []
    retry_after_s: int | None = None


class ErrorEnvelope(BaseModel):
    """The body of every non-2xx response; nothing else (no stack trace, SQL, key or prompt)."""

    error: ErrorBody
