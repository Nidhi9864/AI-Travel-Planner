"""Fine-tuned model adapter: a Stage 2 stub (specification §8.4, FR-043 AC3).

It has the ModelProvider shape, but nothing in Stage 1 can use it: constructing it raises
``ProviderBadRequest`` (a ``ProviderConfigError``), and so does every operation, should an
instance ever exist. Selecting ``AI_PROVIDER=FINETUNED_MODEL`` already stops start-up
(``app.core.config``); Stage 2 replaces this module after a recorded decision.
"""

from typing import TYPE_CHECKING, Literal

from app.ai.errors import ProviderBadRequest
from app.schemas.ai import (
    EditOperations,
    GenerationRequest,
    HealthStatus,
    ItineraryOutput,
    ModelMetadata,
    ModificationRequest,
    ProviderResult,
)

NOT_ENABLED = "FINETUNED_MODEL not enabled in Stage 1"


class FineTunedProvider:
    name: Literal["FINETUNED_MODEL"] = "FINETUNED_MODEL"

    def __init__(self) -> None:
        raise ProviderBadRequest(NOT_ENABLED)

    async def generate_itinerary(
        self, request: GenerationRequest
    ) -> ProviderResult[ItineraryOutput]:
        raise ProviderBadRequest(NOT_ENABLED)

    async def modify_itinerary(
        self, request: ModificationRequest
    ) -> ProviderResult[EditOperations]:
        raise ProviderBadRequest(NOT_ENABLED)

    async def health_check(self) -> HealthStatus:
        raise ProviderBadRequest(NOT_ENABLED)

    def get_model_metadata(self) -> ModelMetadata:
        raise ProviderBadRequest(NOT_ENABLED)


if TYPE_CHECKING:
    from app.ai.providers.base import ModelProvider

    def _conforms_to_model_provider(provider: FineTunedProvider) -> ModelProvider:
        # mypy (make typecheck) fails here if the stub stops matching the interface.
        return provider
