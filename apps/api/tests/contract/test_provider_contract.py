"""Provider contract suite (§8.19; IMP-110 skeleton: TC-001, TC-158; NFR-043).

Every adapter must pass the same tests. Each entry of ``ADAPTERS`` builds a fresh provider, plus
one that raises a given shared error. The in-test double stays registered next to the MOCK adapter
(IMP-207), so the suite keeps checking its own expectations.

Adapters join by adding one entry:
- IMP-207: ``mock`` (``app.ai.providers.mock.MockProvider``, scenarios and ``raise_error``);
- IMP-301: ``gemini_recorded`` (Gemini adapter driven by tests/fixtures/provider_recordings/);
- IMP-512: completes the suite for every adapter (failure scenarios per error type, live marker).
"""

import asyncio
import inspect
import socket
from collections.abc import Callable
from dataclasses import dataclass

import pytest
from fixtures.ai import DoubleProvider, sample_request

from app.ai.errors import (
    ProviderAuthError,
    ProviderBadRequest,
    ProviderError,
    ProviderInvalidOutput,
    ProviderQuotaExhausted,
    ProviderRateLimited,
    ProviderTimeout,
    ProviderUnavailable,
)
from app.ai.providers.base import ModelProvider
from app.ai.providers.mock import MockProvider
from app.core.config import MockScenario
from app.schemas.ai import (
    HealthStatus,
    ItineraryOutput,
    ModelMetadata,
    ModificationRequest,
    ProviderResult,
)


@dataclass(frozen=True)
class Adapter:
    build: Callable[[], ModelProvider]
    failing: Callable[[ProviderError], ModelProvider]


ADAPTERS: dict[str, Adapter] = {
    "double": Adapter(build=DoubleProvider, failing=lambda error: DoubleProvider(error)),
    "mock": Adapter(
        build=lambda: MockProvider("ok", app_env="test"),
        failing=lambda error: MockProvider("ok", app_env="test", raise_error=error),
    ),
    # IMP-301: "gemini_recorded": Adapter(...),
}

OPERATIONS = ("generate_itinerary", "modify_itinerary", "health_check", "get_model_metadata")


@pytest.fixture(params=sorted(ADAPTERS), ids=str)
def adapter(request: pytest.FixtureRequest) -> Adapter:
    return ADAPTERS[request.param]


def test_tc_001_adapter_implements_the_model_provider_interface(adapter: Adapter) -> None:
    provider = adapter.build()
    assert isinstance(provider, ModelProvider)
    assert provider.name in ("GEMINI", "MOCK", "FINETUNED_MODEL")
    for name in OPERATIONS:
        operation = getattr(provider, name)
        expected = getattr(ModelProvider, name)
        assert inspect.iscoroutinefunction(operation) == inspect.iscoroutinefunction(expected)
        assert (
            list(inspect.signature(operation).parameters)
            == list(inspect.signature(expected).parameters)[1:]
        )


def test_tc_158_generate_itinerary_returns_a_valid_io_1_result(adapter: Adapter) -> None:
    request = sample_request()
    result = asyncio.run(adapter.build().generate_itinerary(request))

    assert isinstance(result, ProviderResult)
    output = ItineraryOutput.model_validate(result.output.model_dump())
    assert output.unknown_place_ids(request) == []
    assert result.latency_ms >= 0
    # Usage is reported or null, never estimated: no negative or invented values.
    for count in result.usage.model_dump().values():
        assert count is None or count >= 0


def test_health_check_and_metadata_shapes(adapter: Adapter) -> None:
    provider = adapter.build()
    health = asyncio.run(provider.health_check())
    metadata = provider.get_model_metadata()

    assert isinstance(health, HealthStatus)
    assert isinstance(metadata, ModelMetadata)
    assert metadata.provider == provider.name
    assert metadata.supports_structured_output is True
    assert metadata.is_tuned is False


def test_modify_itinerary_is_not_enabled_in_the_mvp(adapter: Adapter) -> None:
    with pytest.raises(ProviderBadRequest):
        asyncio.run(adapter.build().modify_itinerary(ModificationRequest()))


@pytest.mark.parametrize(
    "error",
    [
        ProviderTimeout(),
        ProviderRateLimited(retry_after_s=1),
        ProviderUnavailable(),
        ProviderQuotaExhausted(),
        ProviderInvalidOutput("malformed_json"),
        ProviderAuthError(),
        ProviderBadRequest("model not found"),
    ],
    ids=lambda error: type(error).__name__,
)
def test_failures_surface_as_the_shared_error_types(adapter: Adapter, error: ProviderError) -> None:
    with pytest.raises(type(error)) as raised:
        asyncio.run(adapter.failing(error).generate_itinerary(sample_request()))
    assert raised.value.failure_reason == error.failure_reason


def test_tc_162_generate_itinerary_makes_no_network_call(
    adapter: Adapter, monkeypatch: pytest.MonkeyPatch
) -> None:
    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("an adapter opened a network connection")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket.socket, "connect_ex", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)
    result = asyncio.run(adapter.build().generate_itinerary(sample_request()))
    assert result.output.days


# MOCK_PROVIDER_SCENARIO (IMD-27): each failure scenario raises the matching shared error.
MOCK_FAILURE_SCENARIOS: dict[MockScenario, type[ProviderError]] = {
    "timeout": ProviderTimeout,
    "rate_limited": ProviderRateLimited,
    "quota": ProviderQuotaExhausted,
    "invalid_json": ProviderInvalidOutput,
}


@pytest.mark.parametrize("scenario", sorted(MOCK_FAILURE_SCENARIOS))
def test_tc_163_mock_failure_scenarios_raise_the_shared_error(scenario: MockScenario) -> None:
    expected = MOCK_FAILURE_SCENARIOS[scenario]
    provider = MockProvider(scenario, app_env="test")
    with pytest.raises(expected) as raised:
        asyncio.run(provider.generate_itinerary(sample_request()))
    assert raised.value.failure_reason == expected.failure_reason
