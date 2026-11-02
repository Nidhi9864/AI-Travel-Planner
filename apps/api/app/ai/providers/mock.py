"""Mock adapter (specification §8.4, FR-042, IMD-27; SAMPLE output, never a real plan).

The default provider in ``local`` and ``test``. It makes no network call and imports no HTTP
client or vendor SDK. ``generate_itinerary`` builds io-1 only from the gr-1 request:

- the candidates (``shortlist``) in their given order are spread over the requested days
  (``trip.num_days``, or the one day of a ``day`` scope), at most ``limits.max_items_per_day``
  per day, filling the first days first;
- the first item of a day starts at 09:00 and each next one at the previous start +
  ``typical_duration_min`` + 30 minutes; ``duration_min`` is the candidate's typical duration;
- themes and notes are written into io-1's model-text fields and start with ``SAMPLE``.

The same request gives an identical output. Scenarios (IMD-27) come from the constructor in tests
or from ``MOCK_PROVIDER_SCENARIO`` (validated by ``app.core.config``); they are honoured when
``APP_ENV`` is local, test or staging and ignored (treated as ``ok``) in production. Unit tests may
pass ``raise_error=<ProviderError>`` to reach the other error kinds.
"""

import time
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, Literal, get_args

from app.ai.errors import (
    ProviderBadRequest,
    ProviderConfigError,
    ProviderError,
    ProviderInvalidOutput,
    ProviderQuotaExhausted,
    ProviderRateLimited,
    ProviderTimeout,
)
from app.core.config import AppEnv, MockScenario, get_settings
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
    ShortlistPlace,
    UsageMetadata,
)

MODEL_ID: Final = "mock-v1"
ADAPTER_VERSION: Final = "mock-1"
SCENARIOS: Final[tuple[MockScenario, ...]] = get_args(MockScenario)
SCENARIO_ENVIRONMENTS: Final[frozenset[AppEnv]] = frozenset({"local", "test", "staging"})

DAY_START_MIN: Final = 9 * 60
GAP_MIN: Final = 30
LAST_START_MIN: Final = 23 * 60 + 59
THEME_MAX: Final = 80
# Namespace of the deterministic out-of-shortlist ID of the unknown_place scenario.
_UNKNOWN_PLACE_NAMESPACE: Final = uuid.UUID("5a3e1c00-0000-4000-8000-00000000a207")


def _hhmm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _minutes(hhmm: str) -> int:
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _day_numbers(request: GenerationRequest) -> list[int]:
    if request.scope.kind == "day" and request.scope.day_number is not None:
        return [request.scope.day_number]
    return list(range(1, request.trip.num_days + 1))


def _build_days(
    request: GenerationRequest, candidates: list[ShortlistPlace]
) -> list[ItineraryDayOutput]:
    """Candidates in order over the days, at most the pace item limit per day (§8.4 timing)."""
    per_day = request.limits.max_items_per_day
    remaining = list(candidates)
    days: list[ItineraryDayOutput] = []
    for day_number in _day_numbers(request):
        items: list[ItineraryItemOutput] = []
        start = DAY_START_MIN
        while remaining and len(items) < per_day and start <= LAST_START_MIN:
            place = remaining.pop(0)
            items.append(
                ItineraryItemOutput(
                    place_id=str(place.place_id),
                    start_time=_hhmm(start),
                    duration_min=place.typical_duration_min,
                    slot_type="meal" if place.category == "food" else "activity",
                    note=f"SAMPLE note from the mock provider: visit {place.name}."[:200],
                )
            )
            start += place.typical_duration_min + GAP_MIN
        if items:
            first = next(p.name for p in candidates if str(p.place_id) == items[0].place_id)
            theme = f"SAMPLE day {day_number}: {first}"[:THEME_MAX]
            days.append(ItineraryDayOutput(day_number=day_number, theme=theme, items=items))
    return days


def _output(days: list[ItineraryDayOutput]) -> ItineraryOutput:
    if not days:
        # io-1 needs at least one day with one item; an empty shortlist cannot give one.
        raise ProviderInvalidOutput("empty", "mock provider: the request has no candidates")
    return ItineraryOutput(
        days=days,
        summary="SAMPLE plan from the mock provider.",
        assumptions=["SAMPLE: travel times, prices and hours are calculated by the application."],
    )


def _flawed(request: GenerationRequest) -> ItineraryOutput:
    """Schema-valid io-1 with one must-visit place left out and one overlap on the first day.

    The left-out place is the first must-visit ID that is a candidate; the overlap moves the
    second item of the first day to start halfway through the first item. A request without a
    shortlisted must-visit place, or whose first day has one item, gets only the flaw it allows.
    """
    shortlisted = {str(place.place_id) for place in request.shortlist}
    missing = next((str(p) for p in request.must_visit_place_ids if str(p) in shortlisted), None)
    days = _build_days(request, [p for p in request.shortlist if str(p.place_id) != missing])
    if days and len(days[0].items) >= 2:
        first, second = days[0].items[0], days[0].items[1]
        overlap_start = _minutes(first.start_time) + first.duration_min // 2
        days[0].items[1] = second.model_copy(update={"start_time": _hhmm(overlap_start)})
    return _output(days)


def _unknown_place(request: GenerationRequest) -> ItineraryOutput:
    """The ok plan with its last item's place_id replaced by one outside the candidates."""
    output = _output(_build_days(request, list(request.shortlist)))
    shortlisted = request.shortlist_ids()
    unknown = uuid.uuid5(_UNKNOWN_PLACE_NAMESPACE, str(request.request_id))
    while str(unknown) in shortlisted:
        unknown = uuid.uuid5(_UNKNOWN_PLACE_NAMESPACE, str(unknown))
    last_day = output.days[-1]
    last_day.items[-1] = last_day.items[-1].model_copy(update={"place_id": str(unknown)})
    return output


class MockProvider:
    name: Literal["MOCK"] = "MOCK"

    def __init__(
        self,
        scenario: MockScenario | None = None,
        *,
        app_env: AppEnv | None = None,
        raise_error: ProviderError | None = None,
    ) -> None:
        """``scenario`` and ``app_env`` default to MOCK_PROVIDER_SCENARIO and APP_ENV."""
        if scenario is None or app_env is None:
            settings = get_settings()
            scenario = settings.mock_provider_scenario if scenario is None else scenario
            app_env = settings.app_env if app_env is None else app_env
        if scenario not in SCENARIOS:
            raise ProviderConfigError(
                f"mock provider: unknown scenario; allowed values are {', '.join(SCENARIOS)}"
            )
        self.requested_scenario: MockScenario = scenario
        self.app_env: AppEnv = app_env
        self.raise_error = raise_error

    @property
    def scenario(self) -> MockScenario:
        """The scenario in effect: the requested one outside production, else ``ok``."""
        return self.requested_scenario if self.app_env in SCENARIO_ENVIRONMENTS else "ok"

    async def generate_itinerary(
        self, request: GenerationRequest
    ) -> ProviderResult[ItineraryOutput]:
        started = time.perf_counter()
        if self.raise_error is not None:
            raise self.raise_error
        match self.scenario:
            case "timeout":
                raise ProviderTimeout("mock provider: timeout scenario")
            case "rate_limited":
                raise ProviderRateLimited("mock provider: rate_limited scenario", retry_after_s=1)
            case "quota":
                raise ProviderQuotaExhausted("mock provider: quota scenario")
            case "invalid_json":
                raise ProviderInvalidOutput(
                    "malformed_json", "mock provider: invalid_json scenario"
                )
            case "flawed":
                output = _flawed(request)
            case "unknown_place":
                output = _unknown_place(request)
            case _:
                output = _output(_build_days(request, list(request.shortlist)))
        return ProviderResult[ItineraryOutput](
            output=output,
            usage=UsageMetadata(),  # the mock reports no tokens: every count stays null
            finish_reason="stop",
            latency_ms=round((time.perf_counter() - started) * 1000),
            provider_request_id=None,
        )

    async def modify_itinerary(
        self, request: ModificationRequest
    ) -> ProviderResult[EditOperations]:
        raise ProviderBadRequest("modify_itinerary not enabled in the MVP")

    async def health_check(self) -> HealthStatus:
        return HealthStatus(status="ok", detail=None, checked_at=datetime.now(UTC))

    def get_model_metadata(self) -> ModelMetadata:
        return ModelMetadata(
            provider=self.name,
            model_id=MODEL_ID,
            adapter_version=ADAPTER_VERSION,
            supports_structured_output=True,
            max_input_tokens=None,
            max_output_tokens=None,
        )


if TYPE_CHECKING:
    from app.ai.providers.base import ModelProvider

    def _conforms_to_model_provider(provider: MockProvider) -> ModelProvider:
        # mypy (make typecheck) fails here if the mock stops matching the interface.
        return provider
