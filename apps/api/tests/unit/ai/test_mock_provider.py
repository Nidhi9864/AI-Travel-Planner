"""Mock adapter (app/ai/providers/mock.py; §8.4, FR-042, IMD-27, IMD-28: TC-033 to TC-036).

No database and no network: every request here is SAMPLE data built from tests/fixtures/ai.py.
"""

import ast
import asyncio
import inspect
import json
import re
import socket
from pathlib import Path
from typing import Any, get_args

import pytest
from fixtures.ai import FORT, MARKET, THALI, sample_request, sample_request_data

from app.ai.errors import (
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
from app.ai.providers import mock
from app.ai.providers.mock import MockProvider
from app.core.config import ConfigError, MockScenario, load_settings
from app.schemas.ai import GenerationRequest, ItineraryOutput, ModificationRequest

IO_1_SCHEMA = json.loads(
    (Path(__file__).resolve().parents[5] / "contracts" / "ai" / "io-1.schema.json").read_text(
        encoding="utf-8"
    )
)
TYPES: dict[str, type | tuple[type, ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "boolean": bool,
    "null": type(None),
}


def schema_errors(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Check a value against the JSON Schema keywords the committed io-1 schema uses."""
    if "$ref" in schema:
        schema = IO_1_SCHEMA["$defs"][schema["$ref"].rsplit("/", 1)[-1]]
    if "anyOf" in schema:
        if all(schema_errors(value, option, path) for option in schema["anyOf"]):
            return [f"{path}: matches no anyOf option"]
        return []
    errors: list[str] = []
    if "type" in schema and not isinstance(value, TYPES[schema["type"]]):
        return [f"{path}: not {schema['type']}"]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: not in enum")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0) or len(value) > schema.get("maxLength", 1e9):
            errors.append(f"{path}: length")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: pattern")
    is_number = isinstance(value, int) and not isinstance(value, bool)
    if is_number and not schema.get("minimum", -1e18) <= value <= schema.get("maximum", 1e18):
        errors.append(f"{path}: range")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", 1e9):
            errors.append(f"{path}: item count")
        for index, element in enumerate(value):
            errors += schema_errors(element, schema.get("items", {}), f"{path}[{index}]")
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        errors += [
            f"{path}.{key}: missing" for key in schema.get("required", []) if key not in value
        ]
        if schema.get("additionalProperties") is False:
            errors += [f"{path}.{key}: not allowed" for key in value if key not in properties]
        for key, element in value.items():
            if key in properties:
                errors += schema_errors(element, properties[key], f"{path}.{key}")
    return errors


def generate(provider: MockProvider, request: GenerationRequest | None = None) -> ItineraryOutput:
    return asyncio.run(provider.generate_itinerary(request or sample_request())).output


def ok(**overrides: Any) -> MockProvider:
    return MockProvider(overrides.pop("scenario", "ok"), app_env="test", **overrides)


def request_with(**changes: Any) -> GenerationRequest:
    data = sample_request_data()
    for path, value in changes.items():
        target = data
        *parents, leaf = path.split("__")
        for key in parents:
            target = target[key]
        target[leaf] = value
    return GenerationRequest.model_validate(data)


def assert_valid_io_1(output: ItineraryOutput) -> None:
    data = json.loads(output.model_dump_json())
    assert ItineraryOutput.model_validate(data) == output
    assert schema_errors(data, IO_1_SCHEMA) == []
    for item in (item for day in output.days for item in day.items):
        assert 15 <= item.duration_min <= 480  # IMD-28


# ---------- TC-033, TC-036: deterministic, schema-valid io-1 built from the candidates ----------


def test_tc_033_the_same_request_gives_an_identical_output() -> None:
    first = generate(ok())
    second = generate(ok())
    assert first == second
    assert first.model_dump_json() == second.model_dump_json()


def test_tc_036_the_output_passes_the_io_1_model_and_the_committed_schema() -> None:
    assert_valid_io_1(generate(ok()))


def test_the_schema_check_rejects_an_invalid_output() -> None:
    data = json.loads(generate(ok()).model_dump_json())
    data["days"][0]["items"][0]["duration_min"] = 481
    data["days"][0]["price"] = "1.00"
    assert len(schema_errors(data, IO_1_SCHEMA)) == 2


def test_candidates_keep_their_order_and_follow_the_timing_rule() -> None:
    output = generate(ok(), request_with(limits__max_items_per_day=2))
    # Shortlist order FORT (120), MARKET (60), THALI (60); two items per day.
    assert [[item.place_id for item in day.items] for day in output.days] == [
        [FORT, MARKET],
        [THALI],
    ]
    day_1 = output.days[0].items
    assert [(item.start_time, item.duration_min) for item in day_1] == [
        ("09:00", 120),
        ("11:30", 60),
    ]
    assert output.days[1].items[0].start_time == "09:00"
    assert output.unknown_place_ids(sample_request()) == []


def test_the_pace_item_limit_and_the_day_count_bound_the_plan() -> None:
    one_per_day = generate(ok(), request_with(limits__max_items_per_day=1))
    assert [day.day_number for day in one_per_day.days] == [1, 2]
    assert all(len(day.items) == 1 for day in one_per_day.days)
    # Two days of one item: the third candidate does not fit and is left out.
    assert one_per_day.place_ids() == [FORT, MARKET]

    all_in_one = generate(ok())  # five items per day: every candidate fits on day 1
    assert [day.day_number for day in all_in_one.days] == [1]
    assert all_in_one.place_ids() == [FORT, MARKET, THALI]


def test_a_day_scope_plans_only_that_day() -> None:
    output = generate(ok(), request_with(scope={"kind": "day", "day_number": 2}))
    assert [day.day_number for day in output.days] == [2]


def test_food_places_are_meals_and_text_fields_are_marked_sample() -> None:
    output = generate(ok())
    slots = {item.place_id: item.slot_type for item in output.days[0].items}
    assert slots == {FORT: "activity", MARKET: "activity", THALI: "meal"}
    assert output.days[0].theme.startswith("SAMPLE")
    assert all(item.note.startswith("SAMPLE") for item in output.days[0].items)
    assert output.summary is not None
    assert output.summary.startswith("SAMPLE")


def test_an_empty_shortlist_is_an_empty_answer() -> None:
    with pytest.raises(ProviderInvalidOutput) as raised:
        generate(ok(), request_with(shortlist=[], day_hints=[], must_visit_place_ids=[]))
    assert raised.value.kind == "empty"


# ---------- ProviderResult, health and metadata ----------


def test_the_result_has_null_usage_a_measured_latency_and_finish_reason_stop() -> None:
    result = asyncio.run(ok().generate_itinerary(sample_request()))
    assert all(count is None for count in result.usage.model_dump().values())
    assert result.latency_ms >= 0
    assert result.finish_reason == "stop"
    assert result.provider_request_id is None


def test_health_is_ok_and_metadata_names_mock_v1() -> None:
    provider = ok()
    assert asyncio.run(provider.health_check()).status == "ok"
    metadata = provider.get_model_metadata()
    assert (metadata.provider, metadata.model_id) == ("MOCK", "mock-v1")
    assert metadata.adapter_version == mock.ADAPTER_VERSION
    assert metadata.supports_structured_output is True


def test_modify_itinerary_is_not_enabled() -> None:
    with pytest.raises(ProviderBadRequest):
        asyncio.run(ok().modify_itinerary(ModificationRequest()))


# ---------- TC-034: scenarios raise the matching shared error ----------


@pytest.mark.parametrize(
    ("scenario", "expected", "reason"),
    [
        ("timeout", ProviderTimeout, "provider_timeout"),
        ("rate_limited", ProviderRateLimited, "provider_rate_limited"),
        ("quota", ProviderQuotaExhausted, "provider_quota_exhausted"),
        ("invalid_json", ProviderInvalidOutput, "invalid_output"),
    ],
)
def test_tc_034_each_failure_scenario_raises_the_shared_error(
    scenario: MockScenario, expected: type[ProviderError], reason: str
) -> None:
    with pytest.raises(expected) as raised:
        generate(ok(scenario=scenario))
    assert type(raised.value) is expected
    assert raised.value.failure_reason == reason


def test_scenario_details_match_section_8_4() -> None:
    with pytest.raises(ProviderRateLimited) as rate:
        generate(ok(scenario="rate_limited"))
    assert rate.value.retry_after_s == 1
    with pytest.raises(ProviderInvalidOutput) as invalid:
        generate(ok(scenario="invalid_json"))
    assert invalid.value.kind == "malformed_json"


@pytest.mark.parametrize(
    "error",
    [ProviderInvalidOutput("blocked"), ProviderAuthError(), ProviderUnavailable()],
    ids=lambda error: type(error).__name__,
)
def test_raise_error_covers_the_other_error_kinds(error: ProviderError) -> None:
    with pytest.raises(type(error)) as raised:
        generate(ok(raise_error=error))
    assert raised.value is error


def test_flawed_is_schema_valid_with_one_overlap_and_one_missing_must_visit() -> None:
    request = sample_request()
    output = generate(ok(scenario="flawed"), request)
    assert_valid_io_1(output)
    assert output.unknown_place_ids(request) == []
    # The must-visit FORT is left out (derived from the request, not hard-coded in the mock).
    assert FORT not in output.place_ids()
    assert set(output.place_ids()) == {MARKET, THALI}
    day_1 = output.days[0].items
    first_end = (
        int(day_1[0].start_time[:2]) * 60 + int(day_1[0].start_time[3:]) + day_1[0].duration_min
    )
    second_start = int(day_1[1].start_time[:2]) * 60 + int(day_1[1].start_time[3:])
    assert second_start < first_end
    assert generate(ok(scenario="flawed"), request) == output


def test_flawed_follows_the_request_must_visit_place() -> None:
    output = generate(ok(scenario="flawed"), request_with(must_visit_place_ids=[THALI]))
    assert THALI not in output.place_ids()
    assert output.place_ids() == [FORT, MARKET]


def test_unknown_place_returns_exactly_one_id_outside_the_candidates() -> None:
    request = sample_request()
    output = generate(ok(scenario="unknown_place"), request)
    assert_valid_io_1(output)
    unknown = output.unknown_place_ids(request)
    assert len(unknown) == 1
    assert unknown[0] not in request.shortlist_ids()
    assert generate(ok(scenario="unknown_place"), request) == output


# ---------- MOCK_PROVIDER_SCENARIO and APP_ENV (IMD-27) ----------


def test_the_scenario_values_are_exactly_the_seven_of_imd_27() -> None:
    assert set(get_args(MockScenario)) == {
        "ok",
        "flawed",
        "timeout",
        "rate_limited",
        "quota",
        "invalid_json",
        "unknown_place",
    }
    assert set(mock.SCENARIOS) == set(get_args(MockScenario))


def test_an_unknown_scenario_is_refused_by_the_settings(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    clean_settings_env.setenv("MOCK_PROVIDER_SCENARIO", "slow")
    with pytest.raises(ConfigError) as raised:
        load_settings()
    assert "MOCK_PROVIDER_SCENARIO" in str(raised.value)
    assert "slow" not in str(raised.value)


def test_an_unknown_scenario_passed_to_the_constructor_is_a_config_error() -> None:
    with pytest.raises(ProviderConfigError):
        MockProvider("slow", app_env="test")  # type: ignore[arg-type]  # deliberately invalid


@pytest.mark.parametrize("app_env", ["local", "test", "staging"])
def test_scenarios_are_honoured_in_local_test_and_staging(
    clean_settings_env: pytest.MonkeyPatch, app_env: str
) -> None:
    clean_settings_env.setenv("APP_ENV", app_env)
    clean_settings_env.setenv("MOCK_PROVIDER_SCENARIO", "quota")
    provider = MockProvider()
    assert provider.scenario == "quota"
    with pytest.raises(ProviderQuotaExhausted):
        generate(provider)


def test_scenarios_are_ignored_in_production() -> None:
    for scenario in get_args(MockScenario):
        provider = MockProvider(scenario, app_env="production")
        assert provider.scenario == "ok"
        assert generate(provider) == generate(ok())


def test_the_default_scenario_is_ok(clean_settings_env: pytest.MonkeyPatch) -> None:
    assert MockProvider().scenario == "ok"
    assert generate(MockProvider()) == generate(ok())


# ---------- TC-035: no network ----------


def test_tc_035_generate_runs_with_socket_connect_patched_to_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("the mock provider opened a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    for scenario in ("ok", "flawed", "unknown_place"):
        assert_valid_io_1(generate(ok(scenario=scenario)))
    assert asyncio.run(ok().health_check()).status == "ok"


def test_the_mock_imports_no_http_client_vendor_sdk_or_planning_module() -> None:
    tree = ast.parse(inspect.getsource(mock))
    imported = {
        (node.module or "") if isinstance(node, ast.ImportFrom) else alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    }
    forbidden = ("httpx", "requests", "google", "app.trips", "app.generation", "app.places")
    assert not [name for name in imported if name.startswith(forbidden)]
