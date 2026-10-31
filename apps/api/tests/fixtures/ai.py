"""AI test data and a ModelProvider test double (IMP-110; SAMPLE data, never real places).

``sample_request()`` is a valid gr-1 request and ``SAMPLE_OUTPUT`` is the io-1 example of §8.7.
``DoubleProvider`` implements the ModelProvider interface without any vendor SDK or network: it
builds io-1 from the request's day hints, or raises the error it was given. It stands in for the
MOCK adapter until IMP-207 adds it.
"""

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from app.ai.errors import ProviderBadRequest, ProviderError
from app.schemas.ai import (
    EditOperations,
    GenerationRequest,
    HealthStatus,
    ItineraryDayOutput,
    ItineraryItemOutput,
    ItineraryOutput,
    ModelMetadata,
    ModificationRequest,
    ProviderResult,
    UsageMetadata,
)

FORT = "00000000-0000-4000-8000-000000000001"
MARKET = "00000000-0000-4000-8000-000000000004"
THALI = "00000000-0000-4000-8000-000000000005"

# The io-1 example of §8.7 (SAMPLE).
SAMPLE_OUTPUT: dict[str, Any] = {
    "days": [
        {
            "day_number": 1,
            "theme": "Old city, fort and market",
            "items": [
                {
                    "place_id": FORT,
                    "start_time": "09:30",
                    "duration_min": 120,
                    "slot_type": "activity",
                    "note": "Start at the fort while it is cool.",
                },
                {
                    "place_id": THALI,
                    "start_time": "12:00",
                    "duration_min": 60,
                    "slot_type": "meal",
                    "note": "Local thali for lunch.",
                },
            ],
        }
    ],
    "summary": "A relaxed day mixing history and food.",
    "assumptions": ["Travel times are calculated by the application."],
}


def _place(place_id: str, name: str, category: str, duration: int) -> dict[str, Any]:
    return {
        "place_id": place_id,
        "name": name,
        "category": category,
        "tags": ["sample"],
        "lat": 12.305,
        "lon": 76.655,
        "typical_duration_min": duration,
        "price_min": "0.00",
        "price_max": "300.00",
        "price_label": "estimate",
        "hours_summary": "Tue 09:00-17:00; Wed 09:00-17:00",
        "suitability": {"step_free": True, "child_friendly": None},
    }


def sample_request_data() -> dict[str, Any]:
    """A valid gr-1 request (§8.6; the §8.18 excerpt with day hints and category interests)."""
    return {
        "input_schema_version": "gr-1",
        "request_id": str(uuid.UUID("6b0e0000-0000-4000-8000-000000000001")),
        "trip": {
            "destination_id": "00000000-0000-4000-8000-0000000000d1",
            "start_date": "2027-01-12",
            "end_date": "2027-01-13",
            "num_days": 2,
            "travellers": {"adults": 2, "children": 0},
            "group_needs": [],
            "budget": {"amount": "12000.00", "currency": "INR"},
            "contingency_pct": 10,
        },
        "preferences": {
            "interests": ["sight", "food"],
            "pace": "balanced",
            "budget_priority": "balanced",
            "transport_pref": "local_transport",
            "accommodation_type": "mid_range",
            "step_free_required": False,
            "notes_quoted": "We like old buildings and street food.",
        },
        "must_visit_place_ids": [FORT],
        "shortlist": [
            _place(FORT, "Example Fort", "sight", 120),
            _place(MARKET, "Example Market", "shopping", 60),
            _place(THALI, "Example Thali House", "food", 60),
        ],
        "day_hints": [
            {"day_number": 1, "place_ids": [FORT, THALI]},
            {"day_number": 2, "place_ids": [MARKET]},
        ],
        "limits": {
            "max_items_per_day": 5,
            "max_active_minutes_per_day": 480,
            "day_start": "09:00",
            "day_end": "19:00",
            "meal_slots": ["lunch"],
        },
        "locked_items": [],
        "scope": {"kind": "full", "day_number": None},
        "repair_context": None,
        "prompt_template_id": "itinerary_generate",
        "prompt_version": "v1",
    }


def sample_request() -> GenerationRequest:
    return GenerationRequest.model_validate(sample_request_data())


class DoubleProvider:
    """In-test ModelProvider: no SDK, no network, deterministic."""

    name: Literal["MOCK"] = "MOCK"

    def __init__(self, raise_error: ProviderError | None = None) -> None:
        self.raise_error = raise_error
        self.calls: list[str] = []

    async def generate_itinerary(
        self, request: GenerationRequest
    ) -> ProviderResult[ItineraryOutput]:
        self.calls.append("generate_itinerary")
        if self.raise_error is not None:
            raise self.raise_error
        days = [
            ItineraryDayOutput(
                day_number=hint.day_number,
                theme=f"Day {hint.day_number}",
                items=[
                    ItineraryItemOutput(
                        place_id=str(place_id),
                        start_time=f"{9 + 2 * index:02d}:00",
                        duration_min=60,
                        slot_type="activity",
                        note="",
                    )
                    for index, place_id in enumerate(hint.place_ids)
                ],
            )
            for hint in request.day_hints
            if hint.place_ids
        ]
        return ProviderResult[ItineraryOutput](
            output=ItineraryOutput(days=days, summary=None, assumptions=[]),
            usage=UsageMetadata(),
            finish_reason="stop",
            latency_ms=0,
            provider_request_id=None,
        )

    async def modify_itinerary(
        self, request: ModificationRequest
    ) -> ProviderResult[EditOperations]:
        self.calls.append("modify_itinerary")
        raise ProviderBadRequest("not enabled")

    async def health_check(self) -> HealthStatus:
        self.calls.append("health_check")
        return HealthStatus(status="ok", detail=None, checked_at=datetime.now(UTC))

    def get_model_metadata(self) -> ModelMetadata:
        self.calls.append("get_model_metadata")
        return ModelMetadata(
            provider=self.name,
            model_id="double-v1",
            adapter_version="test-double",
            supports_structured_output=True,
            max_input_tokens=None,
            max_output_tokens=None,
        )
