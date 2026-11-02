"""Contract v1: the 36 MVP endpoints and nothing else (IMP-214; TC-336; US-007, NFR-033, IMD-37).

The committed ``contracts/openapi.v1.json`` is compared with what the app generates, every MVP API
id of §6.6 must map to exactly one path and method, no T1, R2 or extension path is exposed, and
the A1 fields (SourceRef, Item.sources, the GenerationOut retrieval fields, IMD-116) are declared.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from app.openapi_export import CONTRACT_FILE, openapi_document, render

CONTRACTS = Path(__file__).resolve().parents[4] / "contracts"
V1 = "/api/v1"

# §6.6: API-01 to API-04, API-06 to API-17, API-19 to API-38 (§6.8 lists the ids never built).
MVP_ENDPOINTS: dict[str, tuple[str, str]] = {
    "API-01": ("GET", "/health"),
    "API-02": ("GET", "/health/ready"),
    "API-03": ("GET", f"{V1}/me"),
    "API-04": ("PATCH", f"{V1}/me"),
    "API-06": ("GET", f"{V1}/destinations"),
    "API-07": ("POST", f"{V1}/trips"),
    "API-08": ("GET", f"{V1}/trips"),
    "API-09": ("GET", f"{V1}/itineraries/latest"),
    "API-10": ("GET", f"{V1}/trips/{{trip_id}}"),
    "API-11": ("PATCH", f"{V1}/trips/{{trip_id}}"),
    "API-12": ("DELETE", f"{V1}/trips/{{trip_id}}"),
    "API-13": ("POST", f"{V1}/trips/{{trip_id}}/duplicate"),
    "API-14": ("PUT", f"{V1}/trips/{{trip_id}}/preferences"),
    "API-15": ("GET", f"{V1}/trips/{{trip_id}}/preferences"),
    "API-16": ("GET", f"{V1}/places"),
    "API-17": ("GET", f"{V1}/places/{{place_id}}"),
    "API-19": ("PUT", f"{V1}/trips/{{trip_id}}/saved-places/{{place_id}}"),
    "API-20": ("DELETE", f"{V1}/trips/{{trip_id}}/saved-places/{{place_id}}"),
    "API-21": ("GET", f"{V1}/trips/{{trip_id}}/saved-places"),
    "API-22": ("POST", f"{V1}/trips/{{trip_id}}/generations"),
    "API-23": ("GET", f"{V1}/generations/{{generation_id}}"),
    "API-24": ("GET", f"{V1}/trips/{{trip_id}}/itinerary"),
    "API-25": ("POST", f"{V1}/trips/{{trip_id}}/itinerary/items"),
    "API-26": ("PATCH", f"{V1}/itinerary/items/{{item_id}}"),
    "API-27": ("DELETE", f"{V1}/itinerary/items/{{item_id}}"),
    "API-28": ("GET", f"{V1}/itinerary/items/{{item_id}}/alternatives"),
    "API-29": ("POST", f"{V1}/itinerary/items/{{item_id}}/replace"),
    "API-30": ("POST", f"{V1}/trips/{{trip_id}}/itinerary/days/{{day_number}}/regenerate"),
    "API-31": ("POST", f"{V1}/trips/{{trip_id}}/itinerary/regenerate"),
    "API-32": ("POST", f"{V1}/trips/{{trip_id}}/itinerary/validate"),
    "API-33": ("GET", f"{V1}/trips/{{trip_id}}/costs"),
    "API-34": ("PATCH", f"{V1}/trips/{{trip_id}}/budget-settings"),
    "API-35": ("GET", f"{V1}/trips/{{trip_id}}/summary"),
    "API-36": ("GET", f"{V1}/trips/{{trip_id}}/versions"),
    "API-37": ("POST", f"{V1}/trips/{{trip_id}}/versions"),
    "API-38": ("POST", f"{V1}/trips/{{trip_id}}/versions/{{version_id}}/restore"),
}
HTTP_METHODS = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}


@pytest.fixture(scope="module")
def document() -> dict[str, Any]:
    return openapi_document()


def _operations(document: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    return [
        (method.upper(), path, operation)
        for path, item in document["paths"].items()
        for method, operation in item.items()
        if method in HTTP_METHODS
    ]


def test_committed_contract_is_current() -> None:
    committed = (CONTRACTS / CONTRACT_FILE).read_text(encoding="utf-8")
    assert committed == render(), "contracts/openapi.v1.json is stale; run make openapi"


def test_every_mvp_endpoint_maps_to_exactly_one_operation(document: dict[str, Any]) -> None:
    assert len(MVP_ENDPOINTS) == 36
    by_id: dict[str, list[tuple[str, str]]] = {}
    for method, path, operation in _operations(document):
        match = re.match(r"API-\d{2}\b", operation.get("summary", ""))
        assert match, f"{method} {path} has no API id in its summary"
        by_id.setdefault(match.group(), []).append((method, path))
    assert by_id == {api_id: [endpoint] for api_id, endpoint in MVP_ENDPOINTS.items()}


def test_no_path_outside_the_mvp_set(document: dict[str, Any]) -> None:
    exposed = {(method, path) for method, path, _ in _operations(document)}
    assert exposed == set(MVP_ENDPOINTS.values())
    # §6.8 never-built routes and the extension routes of §6.6.7 (declared by their own cards).
    for path in document["paths"]:
        assert not re.search(
            r"share|feedback|receipt|expense|proposal|transport-options|compare|packing|"
            r"trip-intake|weather|today|budget-fit|context|optimise|explanation|/why",
            path,
        ), path


def test_every_error_answer_is_the_envelope(document: dict[str, Any]) -> None:
    assert "HTTPValidationError" not in document["components"]["schemas"]
    for method, path, operation in _operations(document):
        default = operation["responses"]["default"]["content"]["application/json"]["schema"]
        assert default == {"$ref": "#/components/schemas/ErrorEnvelope"}, f"{method} {path}"


def test_a1_source_ref_and_retrieval_fields(document: dict[str, Any]) -> None:
    schemas = document["components"]["schemas"]
    source_ref = schemas["SourceRef"]
    assert set(source_ref["properties"]) == {
        "chunk_id",
        "kind",
        "title",
        "source_name",
        "licence",
        "attribution_text",
        "url",
        "retrieved_on",
    }
    assert source_ref["properties"]["kind"]["enum"] == ["place", "guide"]

    item = schemas["Item"]
    assert "sources" in item["required"]
    assert item["properties"]["sources"]["items"] == {"$ref": "#/components/schemas/SourceRef"}
    # Item is the one shape of ItineraryOut, EditResultOut and the version reads.
    day_items = schemas["Day"]["properties"]["items"]["items"]
    assert day_items == {"$ref": "#/components/schemas/Item"}

    generation = schemas["GenerationOut"]
    for field in ("retrieval_mode", "embedding_model_id", "retrieval_ms"):
        assert field in generation["required"]
        assert {"type": "null"} in generation["properties"][field]["anyOf"]
    mode = generation["properties"]["retrieval_mode"]["anyOf"][0]
    assert mode["enum"] == ["vector", "lexical_fallback"]


def test_ai_schemas_are_exported_with_the_contract() -> None:
    for version in ("gr-1", "io-1"):
        schema = json.loads((CONTRACTS / "ai" / f"{version}.schema.json").read_text())
        assert schema["$id"].endswith(version)


def test_declared_route_answers_501_with_the_envelope(
    clean_settings_env: pytest.MonkeyPatch,
) -> None:
    # API-02 is public, so it shows the IMD-37 stub without a token or a database.
    settings = Settings(
        app_env="test", ai_provider="MOCK", database_url="postgresql+psycopg://t@db.invalid/t"
    )
    response = TestClient(create_app(settings)).get("/health/ready")
    assert response.status_code == 501
    assert response.json()["error"]["code"] == "NOT_IMPLEMENTED"
