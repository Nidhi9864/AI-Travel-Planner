"""gr-1, io-1 and the provider boundary (§8.3, §8.6, §8.7; IMP-110: TC-156, TC-157)."""

import ast
import asyncio
import copy
import json
from pathlib import Path
from typing import Any

import pytest
from fixtures.ai import (
    FORT,
    MARKET,
    SAMPLE_OUTPUT,
    THALI,
    DoubleProvider,
    sample_request,
    sample_request_data,
)
from pydantic import ValidationError

from app.ai.errors import ProviderBadRequest, ProviderConfigError, ProviderTimeout
from app.ai.providers.base import ModelProvider
from app.ai.providers.finetuned import NOT_ENABLED, FineTunedProvider
from app.schemas import ai_export
from app.schemas.ai import GenerationRequest, ItineraryOutput

API_DIR = Path(__file__).resolve().parents[3]
REPO_ROOT = API_DIR.parents[1]
CONTRACTS_AI = REPO_ROOT / "contracts" / "ai"


def output_data() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE_OUTPUT)


def item(**overrides: Any) -> dict[str, Any]:
    return {
        "place_id": FORT,
        "start_time": "09:00",
        "duration_min": 60,
        "slot_type": "activity",
        "note": "",
        **overrides,
    }


# ---------- io-1 ----------


def test_the_section_8_7_example_is_valid_io_1() -> None:
    output = ItineraryOutput.model_validate(output_data())
    assert output.place_ids() == [FORT, THALI]
    assert list(ItineraryOutput.model_fields) == ["days", "summary", "assumptions"]


@pytest.mark.parametrize(
    "path",
    [(), ("days", 0), ("days", 0, "items", 0)],
    ids=["output", "day", "item"],
)
@pytest.mark.parametrize("extra", ["price", "travel_minutes", "opening_hours", "total"])
def test_io_1_rejects_any_extra_field(path: tuple[Any, ...], extra: str) -> None:
    data = output_data()
    target: Any = data
    for key in path:
        target = target[key]
    target[extra] = "12.00"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ItineraryOutput.model_validate(data)


def test_io_1_has_no_price_hour_travel_or_total_field() -> None:
    names: set[str] = set()

    def collect(schema: Any) -> None:
        if isinstance(schema, dict):
            names.update(schema.get("properties", {}))
            for value in schema.values():
                collect(value)
        elif isinstance(schema, list):
            for value in schema:
                collect(value)

    collect(ItineraryOutput.model_json_schema())
    assert names == {
        "days",
        "summary",
        "assumptions",
        "day_number",
        "theme",
        "items",
        "place_id",
        "start_time",
        "duration_min",
        "slot_type",
        "note",
    }


def test_io_1_requires_place_id() -> None:
    data = output_data()
    del data["days"][0]["items"][0]["place_id"]
    with pytest.raises(ValidationError, match=r"days\.0\.items\.0\.place_id"):
        ItineraryOutput.model_validate(data)


def test_io_1_accepts_14_days_and_rejects_15() -> None:
    days = [{"day_number": n, "theme": "", "items": [item()]} for n in range(1, 15)]
    ItineraryOutput.model_validate({"days": days, "assumptions": []})
    days.append({"day_number": 14, "theme": "", "items": [item()]})
    with pytest.raises(ValidationError, match="at most 14 items"):
        ItineraryOutput.model_validate({"days": days, "assumptions": []})


def test_io_1_accepts_12_items_and_rejects_13_or_none() -> None:
    def output(count: int) -> dict[str, Any]:
        return {
            "days": [{"day_number": 1, "theme": "", "items": [item() for _ in range(count)]}],
            "assumptions": [],
        }

    ItineraryOutput.model_validate(output(12))
    with pytest.raises(ValidationError, match="at most 12 items"):
        ItineraryOutput.model_validate(output(13))
    with pytest.raises(ValidationError, match="at least 1 item"):
        ItineraryOutput.model_validate(output(0))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("duration_min", 14),
        ("duration_min", 481),
        ("start_time", "9:30"),
        ("start_time", "24:00"),
        ("start_time", "09:30:00"),
        ("slot_type", "transfer"),
        ("note", "x" * 201),
    ],
)
def test_io_1_item_limits(field: str, value: Any) -> None:
    data = {"days": [{"day_number": 1, "theme": "", "items": [item(**{field: value})]}]}
    data["assumptions"] = []
    with pytest.raises(ValidationError):
        ItineraryOutput.model_validate(data)


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d["days"][0].update(day_number=0),
        lambda d: d["days"][0].update(day_number=15),
        lambda d: d["days"][0].update(theme="x" * 81),
        lambda d: d.update(summary="x" * 501),
        lambda d: d.update(assumptions=["a"] * 21),
        lambda d: d.pop("assumptions"),
    ],
    ids=["day 0", "day 15", "theme", "summary", "assumptions", "no assumptions"],
)
def test_io_1_day_and_output_limits(change: Any) -> None:
    data = output_data()
    change(data)
    with pytest.raises(ValidationError):
        ItineraryOutput.model_validate(data)


def test_unknown_place_ids_are_reported_against_the_shortlist() -> None:
    data = output_data()
    data["days"][0]["items"].append(item(place_id="00000000-0000-4000-8000-000000009999"))
    output = ItineraryOutput.model_validate(data)
    assert output.unknown_place_ids(sample_request()) == ["00000000-0000-4000-8000-000000009999"]


# ---------- gr-1 ----------


def test_a_valid_gr_1_request_parses() -> None:
    request = sample_request()
    assert request.input_schema_version == "gr-1"
    assert request.shortlist_ids() == {FORT, MARKET, THALI}


@pytest.mark.parametrize(
    "path",
    [(), ("trip",), ("preferences",), ("shortlist", 0), ("limits",), ("scope",)],
)
def test_gr_1_rejects_extra_fields(path: tuple[Any, ...]) -> None:
    data = sample_request_data()
    target: Any = data
    for key in path:
        target = target[key]
    target["user_email"] = "someone@example.test"
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        GenerationRequest.model_validate(data)


@pytest.mark.parametrize(
    "change",
    [
        lambda d: d["trip"].update(num_days=3),
        lambda d: d["trip"].update(num_days=15, end_date="2027-01-26"),
        lambda d: d["trip"]["budget"].update(amount=12000.5),
        lambda d: d["trip"]["budget"].update(currency="inr"),
        lambda d: d["preferences"].update(interests=["stay"]),
        lambda d: d["preferences"].update(pace="fast"),
        lambda d: d["preferences"].update(notes_quoted="x" * 501),
        lambda d: d.update(must_visit_place_ids=[FORT] * 11),
        lambda d: d["shortlist"][0].update(price_max=300),
        lambda d: d["limits"].update(max_items_per_day=13),
        lambda d: d.update(scope={"kind": "day", "day_number": None}),
        lambda d: d.update(scope={"kind": "full", "day_number": 1}),
        lambda d: d.update(input_schema_version="gr-2"),
    ],
    ids=[
        "num_days mismatch",
        "15 days",
        "amount not a decimal string",
        "currency",
        "interest stay",
        "pace",
        "notes over 500",
        "11 must-visit",
        "price not a string",
        "13 items per day",
        "day scope without day",
        "full scope with day",
        "schema version",
    ],
)
def test_gr_1_rules(change: Any) -> None:
    data = sample_request_data()
    change(data)
    with pytest.raises(ValidationError):
        GenerationRequest.model_validate(data)


def test_day_scope_with_a_day_number_is_valid() -> None:
    data = sample_request_data()
    data["scope"] = {"kind": "day", "day_number": 2}
    assert GenerationRequest.model_validate(data).scope.day_number == 2


# ---------- contracts/ai ----------


@pytest.mark.parametrize("version", ["gr-1", "io-1"])
def test_committed_json_schemas_are_in_sync_with_the_models(version: str) -> None:
    committed = (CONTRACTS_AI / f"{version}.schema.json").read_text(encoding="utf-8")
    assert committed == ai_export.render(version, ai_export.AI_SCHEMAS[version])
    document = json.loads(committed)
    assert document["$schema"] == ai_export.JSON_SCHEMA_DIALECT
    assert document["additionalProperties"] is False


def test_export_check_flags_a_stale_file(tmp_path: Path) -> None:
    ai_export.export(tmp_path)
    assert ai_export.main(["--out", str(tmp_path), "--check"]) == 0
    (tmp_path / "io-1.schema.json").write_text("{}\n", encoding="utf-8")
    assert ai_export.main(["--out", str(tmp_path), "--check"]) == 1


# ---------- provider boundary ----------


def vendor_imports() -> list[str]:
    """`google` imports in app/, outside the one module allowed to have them."""
    found = []
    for path in sorted((API_DIR / "app").rglob("*.py")):
        relative = path.relative_to(API_DIR).as_posix()
        if relative == "app/ai/providers/gemini.py":
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module]
            found += [f"{relative}: {n}" for n in names if n.split(".")[0] == "google"]
    return found


def test_tc_156_no_vendor_sdk_import_outside_the_gemini_adapter() -> None:
    # make imports (import-linter) enforces the same rule on the import graph (TC-002).
    assert vendor_imports() == []


async def stub_generation_service(provider: ModelProvider) -> list[str]:
    """A caller written against the interface only, as generation/service.py will be."""
    health = await provider.health_check()
    metadata = provider.get_model_metadata()
    result = await provider.generate_itinerary(sample_request())
    output = ItineraryOutput.model_validate(result.output.model_dump())
    return [health.status, metadata.provider, *output.place_ids()]


def test_tc_157_a_test_double_runs_through_a_stub_service_unchanged() -> None:
    double = DoubleProvider()
    assert isinstance(double, ModelProvider)

    assert asyncio.run(stub_generation_service(double)) == ["ok", "MOCK", FORT, THALI, MARKET]
    assert double.calls == ["health_check", "get_model_metadata", "generate_itinerary"]

    # The same caller sees a provider error as the shared type, not a vendor error.
    with pytest.raises(ProviderTimeout):
        asyncio.run(stub_generation_service(DoubleProvider(raise_error=ProviderTimeout())))


def test_the_fine_tuned_adapter_is_not_enabled_in_stage_1() -> None:
    with pytest.raises(ProviderConfigError, match=NOT_ENABLED) as raised:
        FineTunedProvider()
    assert isinstance(raised.value, ProviderBadRequest)

    # Every operation refuses too, should an instance ever exist.
    stub = object.__new__(FineTunedProvider)
    assert isinstance(stub, ModelProvider)
    with pytest.raises(ProviderBadRequest):
        asyncio.run(stub.generate_itinerary(sample_request()))
    with pytest.raises(ProviderBadRequest):
        stub.get_model_metadata()
