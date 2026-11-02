"""Generation record rules of app/generation/records.py (§8.2 statuses, §8.16 columns; IMD-17).

Pure: no database. The API suite tests/api/test_generation_records.py covers the same rules
through the repository against PostgreSQL; these cases check the rules alone.
"""

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

from app.generation import records
from app.generation.records import IllegalTransitionError, InvalidGenerationRecordError

MIGRATION_0004 = Path(__file__).parents[3] / "migrations" / "sql" / "0004_ai_and_plan.sql"


def _check_list(column: str) -> set[str]:
    """The values of `column in (...)` in migration 0004."""
    sql = MIGRATION_0004.read_text(encoding="utf-8")
    match = re.search(rf"{column}\s+in\s*\(([^)]*)\)", sql)
    assert match, f"no CHECK list for {column}"
    return set(re.findall(r"'([^']+)'", match.group(1)))


# --- status machine ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("queued", "running"),
        ("running", "validating"),
        ("validating", "repairing"),
        ("repairing", "validating"),
        ("validating", "completed"),
        ("repairing", "completed"),
        ("queued", "failed"),
        ("running", "failed"),
        ("validating", "failed"),
        ("repairing", "failed"),
    ],
)
def test_allowed_transitions_pass(current: str, target: records.GenerationStatus) -> None:
    records.check_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("queued", "completed"),  # cannot skip running and validating
        ("queued", "validating"),
        ("running", "completed"),
        ("running", "repairing"),
        ("completed", "failed"),  # final
        ("completed", "running"),
        ("failed", "queued"),  # final
        ("failed", "completed"),
        ("unknown", "running"),
    ],
)
def test_illegal_transitions_raise(current: str, target: records.GenerationStatus) -> None:
    with pytest.raises(IllegalTransitionError) as caught:
        records.check_transition(current, target)
    assert caught.value.current == current
    assert caught.value.target == target


def test_every_status_has_a_transition_row() -> None:
    assert set(records.TRANSITIONS) == _check_list("status")


def test_active_statuses_are_the_non_final_ones() -> None:
    final = {status for status, targets in records.TRANSITIONS.items() if not targets}
    assert final == {"completed", "failed"}
    assert set(records.TRANSITIONS) - final == records.ACTIVE_STATUSES


# --- scope ---------------------------------------------------------------------------------


@pytest.mark.parametrize("day", [1, 7, 14])
def test_day_scope_accepts_days_1_to_14(day: int) -> None:
    records.check_scope("day", day)


@pytest.mark.parametrize("day", [None, 0, 15, -1])
def test_day_scope_rejects_missing_or_out_of_range_day(day: int | None) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.check_scope("day", day)


@pytest.mark.parametrize("scope", ["full", "edit"])
def test_other_scopes_take_no_day(scope: records.GenerationScope) -> None:
    records.check_scope(scope, None)
    with pytest.raises(InvalidGenerationRecordError):
        records.check_scope(scope, 3)


def test_unknown_scope_is_rejected() -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.check_scope("week", None)  # type: ignore[arg-type]  # deliberately invalid value


# --- outcome and failure reason ------------------------------------------------------------


@pytest.mark.parametrize("outcome", ["model", "model_repaired", "fallback_rule_based"])
def test_completed_outcomes_pass(outcome: str) -> None:
    records.check_outcome(outcome)


@pytest.mark.parametrize("outcome", ["failed", "", "MODEL"])
def test_non_completing_outcomes_raise(outcome: str) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.check_outcome(outcome)


def test_completed_outcomes_are_the_migration_list_without_failed() -> None:
    assert _check_list("outcome") - {"failed"} == records.COMPLETED_OUTCOMES


def test_failure_reasons_equal_the_migration_list() -> None:
    assert _check_list("failure_reason") == records.FAILURE_REASONS


@pytest.mark.parametrize("reason", ["timeout", "PROVIDER_TIMEOUT", ""])
def test_unknown_failure_reason_raises(reason: str) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.check_failure_reason(reason)


# --- request hash --------------------------------------------------------------------------


def test_request_hash_ignores_key_order() -> None:
    a = {"trip_id": "t1", "days": 3, "prefs": {"pace": "relaxed", "budget": 100}}
    b = {"prefs": {"budget": 100, "pace": "relaxed"}, "days": 3, "trip_id": "t1"}
    assert records.request_hash(a) == records.request_hash(b)


def test_request_hash_changes_with_content() -> None:
    assert records.request_hash({"days": 3}) != records.request_hash({"days": 4})


def test_request_hash_is_a_valid_sha256_digest() -> None:
    digest = records.request_hash({"destination": "Pune ₹"})
    records.check_request_hash(digest)
    assert len(digest) == 64


def test_canonical_json_has_no_whitespace() -> None:
    assert records.canonical_json({"b": 1, "a": [1, 2]}) == '{"a":[1,2],"b":1}'


@pytest.mark.parametrize("value", ["", "abc", "A" * 64, "g" * 64, "0" * 63, "0" * 65])
def test_check_request_hash_rejects_non_digests(value: str) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.check_request_hash(value)


# --- generation settings -------------------------------------------------------------------


def test_settings_keep_allowed_keys_and_drop_unknown_ones() -> None:
    cleaned = records.clean_generation_settings(
        {"temperature": 0.4, "max_output_tokens": 2048, "seed": 7, "structured_output": True}
    )
    assert cleaned == {"temperature": 0.4, "max_output_tokens": 2048, "structured_output": True}


def test_settings_none_gives_empty_dict() -> None:
    assert records.clean_generation_settings(None) == {}


@pytest.mark.parametrize("key", ["prompt", "system_prompt", "Prompt_Text", "input_text"])
def test_settings_refuse_prompt_or_text_keys(key: str) -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.clean_generation_settings({key: "x"})


def test_settings_refuse_non_scalar_values() -> None:
    with pytest.raises(InvalidGenerationRecordError):
        records.clean_generation_settings({"temperature": [0.1, 0.2]})


def test_settings_value_length_limit() -> None:
    records.clean_generation_settings({"api_style": "x" * records.SETTINGS_VALUE_MAX})
    with pytest.raises(InvalidGenerationRecordError):
        records.clean_generation_settings({"api_style": "x" * (records.SETTINGS_VALUE_MAX + 1)})


# --- usage ---------------------------------------------------------------------------------


@dataclass
class _Usage:
    input_tokens: int | None
    output_tokens: int | None
    thinking_tokens: int | None


def test_usage_columns_copy_reported_counts() -> None:
    assert records.usage_columns(_Usage(120, 45, None)) == {
        "input_tokens": 120,
        "output_tokens": 45,
        "thinking_tokens": None,
    }


def test_usage_columns_without_usage_are_null() -> None:
    assert records.usage_columns(None) == {
        "input_tokens": None,
        "output_tokens": None,
        "thinking_tokens": None,
    }
