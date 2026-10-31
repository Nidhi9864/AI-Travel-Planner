"""Domain exceptions and the handlers that turn every error into the §6.3 envelope.

Each exception carries its `code` and HTTP status. FastAPI's RequestValidationError becomes 422
VALIDATION_ERROR with `details`; Starlette's HTTP errors (an unknown route) keep their status; any
other exception becomes 500 INTERNAL, logged with the request ID and never returned with a trace.
"""

# The exception names are the ones of the IMP-103 card (NotFound, Conflict, ...), not *Error.
# ruff: noqa: N818

import logging
from collections.abc import Mapping, Sequence
from typing import Any, ClassVar, cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_id import REQUEST_ID_HEADER, current_request_id, new_request_id
from app.schemas.common import ErrorBody, ErrorCode, ErrorDetail, ErrorEnvelope

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Base of the domain exceptions; `message` is shown to the user, so it must be safe."""

    status_code: ClassVar[int] = 500
    code: ClassVar[ErrorCode] = ErrorCode.INTERNAL
    default_message: ClassVar[str] = "Something went wrong. Please try again."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Sequence[ErrorDetail] = (),
        retry_after_s: int | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = list(details)
        self.retry_after_s = retry_after_s
        super().__init__(self.message)


class Unauthenticated(DomainError):
    status_code = 401
    code = ErrorCode.UNAUTHENTICATED
    default_message = "Please sign in again."


class NotFound(DomainError):
    status_code = 404
    code = ErrorCode.NOT_FOUND
    default_message = "Not found."


class StalePlan(DomainError):
    status_code = 409
    code = ErrorCode.STALE_PLAN
    default_message = "The plan has changed since you loaded it. Reload and try again."


class GenerationInProgress(DomainError):
    status_code = 409
    code = ErrorCode.GENERATION_IN_PROGRESS
    default_message = "A plan is being generated for this trip. Try again when it finishes."


class Conflict(DomainError):
    status_code = 409
    code = ErrorCode.CONFLICT
    default_message = "This change conflicts with the current state."


class ValidationFailed(DomainError):
    status_code = 422
    code = ErrorCode.VALIDATION_ERROR
    default_message = "Some fields need attention."


class InvalidEdit(DomainError):
    status_code = 422
    code = ErrorCode.INVALID_EDIT
    default_message = "This edit is not possible."


class RateLimited(DomainError):
    status_code = 429
    code = ErrorCode.RATE_LIMITED
    default_message = "Too many requests. Please wait and try again."


class QuotaReached(DomainError):
    status_code = 429
    code = ErrorCode.AI_QUOTA_REACHED
    default_message = "The daily AI limit has been reached."


class Internal(DomainError):
    status_code = 500
    code = ErrorCode.INTERNAL


class EndpointNotImplemented(DomainError):
    status_code = 501
    code = ErrorCode.NOT_IMPLEMENTED
    default_message = "This feature is not available yet."


class ServiceUnavailable(DomainError):
    status_code = 503
    code = ErrorCode.SERVICE_UNAVAILABLE
    default_message = "The service is temporarily unavailable. Please try again."


DOMAIN_ERRORS: tuple[type[DomainError], ...] = (
    Unauthenticated,
    NotFound,
    StalePlan,
    GenerationInProgress,
    Conflict,
    ValidationFailed,
    InvalidEdit,
    RateLimited,
    QuotaReached,
    Internal,
    EndpointNotImplemented,
    ServiceUnavailable,
)

# Starlette raises HTTPException for routing failures. 405 has no §6.3 code; it keeps its status
# (and Allow header) with NOT_FOUND, because the route does not exist for that method.
_HTTP_STATUS_CODES: dict[int, ErrorCode] = {
    401: ErrorCode.UNAUTHENTICATED,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.NOT_FOUND,
    409: ErrorCode.CONFLICT,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
    501: ErrorCode.NOT_IMPLEMENTED,
    503: ErrorCode.SERVICE_UNAVAILABLE,
}
_HTTP_STATUS_MESSAGES: dict[int, str] = {
    401: Unauthenticated.default_message,
    404: NotFound.default_message,
    405: NotFound.default_message,
}


def _request_id(request: Request) -> str:
    # Set by RequestIdMiddleware; generated here only when the middleware did not run.
    request_id: str = (
        getattr(request.state, "request_id", None) or current_request_id() or new_request_id()
    )
    request.state.request_id = request_id
    return request_id


def error_response(
    request: Request,
    status_code: int,
    code: ErrorCode,
    message: str,
    *,
    details: Sequence[ErrorDetail] = (),
    retry_after_s: int | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    request_id = _request_id(request)
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code=code,
            message=message,
            request_id=request_id,
            details=list(details),
            retry_after_s=retry_after_s,
        )
    )
    response_headers = {**(headers or {}), REQUEST_ID_HEADER: request_id}
    if retry_after_s is not None:
        response_headers["Retry-After"] = str(retry_after_s)
    return JSONResponse(envelope.model_dump(mode="json"), status_code, headers=response_headers)


async def handle_domain_error(request: Request, exc: Exception) -> JSONResponse:
    error = cast(DomainError, exc)  # registered only for the DomainError classes
    return error_response(
        request,
        error.status_code,
        error.code,
        error.message,
        details=error.details,
        retry_after_s=error.retry_after_s,
    )


def _field_name(loc: Sequence[Any]) -> str:
    # ("body", "end_date") -> "end_date"; ("query", "limit") -> "limit"; nested keeps the path.
    parts = list(loc)
    if parts and parts[0] in ("body", "query", "path", "header", "cookie"):
        parts = parts[1:]
    return ".".join(str(part) for part in parts) or str(loc[0] if loc else "request")


async def handle_request_validation_error(request: Request, exc: Exception) -> JSONResponse:
    errors = cast(RequestValidationError, exc).errors()
    # Only the location and pydantic's message are returned, never the rejected input.
    details = [ErrorDetail(field=_field_name(err["loc"]), message=err["msg"]) for err in errors]
    return error_response(
        request,
        ValidationFailed.status_code,
        ValidationFailed.code,
        ValidationFailed.default_message,
        details=details,
    )


async def handle_http_exception(request: Request, exc: Exception) -> JSONResponse:
    http_error = cast(StarletteHTTPException, exc)
    status_code = http_error.status_code
    code = _HTTP_STATUS_CODES.get(status_code)
    if code is None:
        code = ErrorCode.INTERNAL if status_code >= 500 else ErrorCode.VALIDATION_ERROR
    message = _HTTP_STATUS_MESSAGES.get(status_code, "The request could not be processed.")
    return error_response(request, status_code, code, message, headers=http_error.headers)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    request_id = _request_id(request)
    logger.exception("unhandled error", extra={"request_id": request_id})
    return error_response(request, Internal.status_code, Internal.code, Internal.default_message)


def register_error_handlers(app: FastAPI) -> None:
    for error_class in DOMAIN_ERRORS:
        app.add_exception_handler(error_class, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
