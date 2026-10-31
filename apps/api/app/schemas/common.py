"""Common API types: the error envelope of specification §6.3."""

from enum import StrEnum

from pydantic import BaseModel


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
