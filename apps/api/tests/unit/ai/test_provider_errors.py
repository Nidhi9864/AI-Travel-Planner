"""Provider error types (§8.3): retry flags and failure reasons (TC-005; IMP-110)."""

import re
from pathlib import Path

import pytest

from app.ai.errors import (
    ALL_PROVIDER_ERRORS,
    ProviderAuthError,
    ProviderBadRequest,
    ProviderConfigError,
    ProviderError,
    ProviderInvalidOutput,
    ProviderQuotaExhausted,
    ProviderRateLimited,
    ProviderTimeout,
    ProviderUnavailable,
)

MIGRATION_0004 = Path(__file__).resolve().parents[3] / "migrations" / "sql" / "0004_ai_and_plan.sql"


def failure_reason_check_list() -> set[str]:
    """The values allowed by the ai_generations.failure_reason CHECK of migration 0004."""
    sql = MIGRATION_0004.read_text(encoding="utf-8")
    match = re.search(
        r"failure_reason\s+text\s+check\s*\(\s*failure_reason\s+in\s*\(([^)]*)\)", sql
    )
    assert match, "failure_reason CHECK not found in migration 0004"
    return set(re.findall(r"'([a-z_]+)'", match.group(1)))


def test_check_list_is_read_from_the_migration() -> None:
    assert failure_reason_check_list() == {
        "provider_timeout",
        "provider_rate_limited",
        "provider_quota_exhausted",
        "provider_unavailable",
        "invalid_output",
        "unresolved_validation",
        "config_error",
        "internal",
    }


@pytest.mark.parametrize("error_type", ALL_PROVIDER_ERRORS, ids=lambda t: t.__name__)
def test_every_provider_error_has_a_failure_reason_in_the_check_list(
    error_type: type[ProviderError],
) -> None:
    # TC-005: a recorded reason that the database would reject could never be saved.
    assert error_type.failure_reason in failure_reason_check_list()


def test_every_provider_error_subclass_is_listed() -> None:
    def subclasses(cls: type[ProviderError]) -> set[type[ProviderError]]:
        found = set(cls.__subclasses__())
        for sub in list(found):
            found |= subclasses(sub)
        return found

    assert subclasses(ProviderError) | {ProviderError} == set(ALL_PROVIDER_ERRORS)


@pytest.mark.parametrize(
    ("error", "retryable", "failure_reason"),
    [
        (ProviderTimeout(), True, "provider_timeout"),
        (ProviderRateLimited(retry_after_s=1), True, "provider_rate_limited"),
        (ProviderUnavailable(), True, "provider_unavailable"),
        (ProviderQuotaExhausted(), False, "provider_quota_exhausted"),
        (ProviderInvalidOutput("malformed_json"), False, "invalid_output"),
        (ProviderConfigError(), False, "config_error"),
        (ProviderAuthError(), False, "config_error"),
        (ProviderBadRequest("not enabled"), False, "config_error"),
    ],
    ids=lambda value: type(value).__name__ if isinstance(value, ProviderError) else None,
)
def test_retry_flags_and_reasons_follow_the_section_8_3_table(
    error: ProviderError, retryable: bool, failure_reason: str
) -> None:
    assert isinstance(error, ProviderError)
    assert error.retryable is retryable
    assert error.failure_reason == failure_reason


def test_configuration_errors_share_one_base() -> None:
    # The card names ProviderConfigError; §8.3 names ProviderAuthError and ProviderBadRequest.
    assert issubclass(ProviderAuthError, ProviderConfigError)
    assert issubclass(ProviderBadRequest, ProviderConfigError)


def test_error_details() -> None:
    assert ProviderRateLimited(retry_after_s=2.5).retry_after_s == 2.5
    assert ProviderRateLimited().retry_after_s is None
    error = ProviderInvalidOutput("truncated")
    assert error.kind == "truncated"
    assert str(error) == "invalid output: truncated"
    assert str(ProviderTimeout()) == "ProviderTimeout"
