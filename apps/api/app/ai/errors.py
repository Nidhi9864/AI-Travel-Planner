"""Provider error types shared by every adapter and the pipeline (specification §8.3, §8.14).

An adapter raises only these, mapped from its vendor's errors (§8.4). Each type states whether
step 7 may retry it and the ``ai_generations.failure_reason`` it stands for (the CHECK list of
migration 0004). A transient error that ends in the rule-based fallback is recorded on a completed
row in ``validation_summary.provider_failure`` with that value; quota and configuration errors end
the generation ``failed`` with it (IMD-22). Messages are written by the adapter and never contain
vendor error text, which can echo prompt content (NFR-024).

``ProviderConfigError`` (IMP-110 card) is the common base of the two configuration errors of §8.3,
``ProviderAuthError`` and ``ProviderBadRequest``; all three record ``config_error``.
"""

# The class names are the contract of §8.3 (ProviderTimeout, not ProviderTimeoutError).
# ruff: noqa: N818

from typing import ClassVar, Literal

# The values of ai_generations.failure_reason (migration 0004) that a provider error can produce.
ProviderFailureReason = Literal[
    "provider_timeout",
    "provider_rate_limited",
    "provider_quota_exhausted",
    "provider_unavailable",
    "invalid_output",
    "config_error",
    "internal",
]

InvalidOutputKind = Literal["malformed_json", "schema_violation", "blocked", "empty", "truncated"]


class ProviderError(Exception):
    """Base of every provider error. An unclassified one is an application fault (`internal`)."""

    retryable: ClassVar[bool] = False
    failure_reason: ClassVar[ProviderFailureReason] = "internal"

    def __init__(self, message: str = "") -> None:
        super().__init__(message or self.__class__.__name__)


class ProviderTimeout(ProviderError):
    """No answer within the attempt timeout."""

    retryable = True
    failure_reason = "provider_timeout"


class ProviderRateLimited(ProviderError):
    """Per-minute limit (429 rate); a retry honours `retry_after_s` inside the 70 s allowance."""

    retryable = True
    failure_reason = "provider_rate_limited"

    def __init__(self, message: str = "", *, retry_after_s: float | None = None) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s


class ProviderUnavailable(ProviderError):
    """500, 503 or overload."""

    retryable = True
    failure_reason = "provider_unavailable"


class ProviderQuotaExhausted(ProviderError):
    """Daily quota (429 quota) or empty prepaid balance (402): breaker opens, no fallback."""

    failure_reason = "provider_quota_exhausted"


class ProviderInvalidOutput(ProviderError):
    """The answer is unusable; step 10 decides between one repair call and the fallback."""

    failure_reason = "invalid_output"

    def __init__(self, kind: InvalidOutputKind, message: str = "") -> None:
        super().__init__(message or f"invalid output: {kind}")
        self.kind: InvalidOutputKind = kind


class ProviderConfigError(ProviderError):
    """The provider cannot be used as configured: no automatic fallback; the page offers rule_based."""

    failure_reason = "config_error"


class ProviderAuthError(ProviderConfigError):
    """Key missing, invalid or not permitted (403): breaker open until restart, health `down`."""


class ProviderBadRequest(ProviderConfigError):
    """Malformed request, unknown or retired model, schema rejected (400, 404), or not enabled."""


ALL_PROVIDER_ERRORS: tuple[type[ProviderError], ...] = (
    ProviderError,
    ProviderTimeout,
    ProviderRateLimited,
    ProviderUnavailable,
    ProviderQuotaExhausted,
    ProviderInvalidOutput,
    ProviderConfigError,
    ProviderAuthError,
    ProviderBadRequest,
)
