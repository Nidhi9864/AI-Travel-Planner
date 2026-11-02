"""Generation record rules: the status machine and the column helpers of ai_generations.

Specification §5 (migration 0004), §8.2 (statuses), §8.16 (columns per moment), FR-038, NFR-042;
IMD-17, IMD-22, IMD-91. Pure: no I/O and no framework imports. ``generation/repository.py`` applies
these rules before it writes a row.

- Statuses, outcomes, scopes and failure reasons are the CHECK lists of migration 0004.
- ``TRANSITIONS`` is the one table of allowed status changes; a change outside it raises
  ``IllegalTransitionError`` before anything is written.
- ``request_hash`` is the SHA-256 of the canonical request JSON; the content is never stored.
- ``generation_settings`` holds parameter names and values only (§8.4 settings record).
- Usage maps to the three token columns exactly; a count the provider did not report stays null.
"""

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any, Final, Literal, Protocol, get_args

GenerationStatus = Literal["queued", "running", "validating", "repairing", "completed", "failed"]
CompletedOutcome = Literal["model", "model_repaired", "fallback_rule_based"]
GenerationScope = Literal["full", "day", "edit"]
# Migration 0004: the provider error reasons of app.ai.errors plus unresolved_validation.
FailureReason = Literal[
    "provider_timeout",
    "provider_rate_limited",
    "provider_quota_exhausted",
    "provider_unavailable",
    "invalid_output",
    "unresolved_validation",
    "config_error",
    "internal",
]

ACTIVE_STATUSES: Final[frozenset[GenerationStatus]] = frozenset(
    {"queued", "running", "validating", "repairing"}
)
COMPLETED_OUTCOMES: Final[frozenset[str]] = frozenset(get_args(CompletedOutcome))
FAILURE_REASONS: Final[frozenset[str]] = frozenset(get_args(FailureReason))

# §8.2: queued -> running (step 1); running -> validating (steps 8, 9); validating -> repairing
# (step 10); repairing -> validating (the repaired plan is checked again); validating or
# repairing -> completed (step 11); any active status -> failed (config or quota error, the
# reaper, an unresolved plan). completed and failed are final.
TRANSITIONS: Final[Mapping[str, frozenset[GenerationStatus]]] = {
    "queued": frozenset({"running", "failed"}),
    "running": frozenset({"validating", "failed"}),
    "validating": frozenset({"repairing", "completed", "failed"}),
    "repairing": frozenset({"validating", "completed", "failed"}),
    "completed": frozenset(),
    "failed": frozenset(),
}

MIN_SCOPE_DAY: Final = 1
MAX_SCOPE_DAY: Final = 14

# §8.4 settings record: the allow-listed parameter names; values are scalars of at most 64
# characters. A key that names prompt or text is refused outright; other unknown keys are dropped.
SETTINGS_KEYS: Final[frozenset[str]] = frozenset(
    {
        "api_style",
        "temperature",
        "max_output_tokens",
        "thinking_level",
        "structured_output",
        "timeout_s",
    }
)
SETTINGS_VALUE_MAX: Final = 64
_FORBIDDEN_KEY = re.compile(r"prompt|text", re.IGNORECASE)
_SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")


class IllegalTransitionError(Exception):
    """A status change outside ``TRANSITIONS``; raised before the row is touched."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"illegal generation status change {current} -> {target}")
        self.current = current
        self.target = target


class InvalidGenerationRecordError(ValueError):
    """A value that ai_generations must not hold (scope, outcome, hash or settings)."""


class TokenUsage(Protocol):
    """The token counts of ``app.schemas.ai.UsageMetadata`` that are stored."""

    @property
    def input_tokens(self) -> int | None: ...
    @property
    def output_tokens(self) -> int | None: ...
    @property
    def thinking_tokens(self) -> int | None: ...


def check_transition(current: str, target: GenerationStatus) -> None:
    if target not in TRANSITIONS.get(current, frozenset()):
        raise IllegalTransitionError(current, target)


def check_scope(scope: GenerationScope, scope_day_number: int | None) -> None:
    """IMD-17: a day scope needs its day number 1 to 14; the other scopes have none."""
    if scope not in get_args(GenerationScope):
        raise InvalidGenerationRecordError(f"unknown scope {scope!r}")
    if scope == "day":
        if scope_day_number is None or not MIN_SCOPE_DAY <= scope_day_number <= MAX_SCOPE_DAY:
            raise InvalidGenerationRecordError("scope day needs scope_day_number 1 to 14")
    elif scope_day_number is not None:
        raise InvalidGenerationRecordError("scope_day_number is set only for scope day")


def check_outcome(outcome: str) -> None:
    if outcome not in COMPLETED_OUTCOMES:
        raise InvalidGenerationRecordError(f"outcome {outcome!r} cannot complete a generation")


def check_failure_reason(reason: str) -> None:
    if reason not in FAILURE_REASONS:
        raise InvalidGenerationRecordError(f"unknown failure_reason {reason!r}")


def canonical_json(request: Mapping[str, Any]) -> str:
    """The request as JSON with sorted keys and no whitespace, so equal requests hash alike."""
    return json.dumps(
        request, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str
    )


def request_hash(request: Mapping[str, Any]) -> str:
    """SHA-256 (hex) of the canonical request JSON; the hash is stored, never the content."""
    return hashlib.sha256(canonical_json(request).encode("utf-8")).hexdigest()


def check_request_hash(value: str) -> None:
    if not _SHA256_HEX.fullmatch(value):
        raise InvalidGenerationRecordError("request_hash must be a SHA-256 hex digest")


def clean_generation_settings(settings: Mapping[str, Any] | None) -> dict[str, Any]:
    """Parameter names and values only: refuses prompt or text keys and non-scalar values."""
    cleaned: dict[str, Any] = {}
    for key, value in (settings or {}).items():
        if _FORBIDDEN_KEY.search(key):
            raise InvalidGenerationRecordError(f"generation_settings must not hold {key!r}")
        if key not in SETTINGS_KEYS:
            continue
        if value is not None and not isinstance(value, bool | int | float | str):
            raise InvalidGenerationRecordError(f"generation_settings {key!r} must be a scalar")
        if isinstance(value, str) and len(value) > SETTINGS_VALUE_MAX:
            raise InvalidGenerationRecordError(f"generation_settings {key!r} is too long")
        cleaned[key] = value
    return cleaned


def usage_columns(usage: TokenUsage | None) -> dict[str, int | None]:
    """FR-038 AC2: the reported counts, or null; never estimated. total_tokens is not stored."""
    return {
        "input_tokens": usage.input_tokens if usage else None,
        "output_tokens": usage.output_tokens if usage else None,
        "thinking_tokens": usage.thinking_tokens if usage else None,
    }
