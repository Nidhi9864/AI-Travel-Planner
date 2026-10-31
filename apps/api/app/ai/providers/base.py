"""The ModelProvider interface (specification §8.3, FR-040, IMD-06).

Code outside ``app/ai/`` uses a provider only through this module, ``app.ai.errors`` and
``app.ai.factory`` (IMP-207); it never imports an adapter or a vendor SDK (§4.4, NFR-031). The
types of the interface are defined in ``app.schemas.ai`` and re-exported here.
"""

from typing import Protocol, runtime_checkable

from app.schemas.ai import (
    EditOperations,
    GenerationRequest,
    HealthStatus,
    ItineraryOutput,
    ModelMetadata,
    ModificationRequest,
    ProviderName,
    ProviderResult,
    UsageMetadata,
)

__all__ = [
    "EditOperations",
    "GenerationRequest",
    "HealthStatus",
    "ItineraryOutput",
    "ModelMetadata",
    "ModelProvider",
    "ModificationRequest",
    "ProviderName",
    "ProviderResult",
    "UsageMetadata",
]


@runtime_checkable
class ModelProvider(Protocol):
    """One model provider: GEMINI, MOCK or FINETUNED_MODEL (Stage 2).

    Every operation raises only ``app.ai.errors.ProviderError`` subclasses. The assistive EXT
    operations of §8.20 are added by their own cards.
    """

    @property
    def name(self) -> ProviderName:
        """GEMINI, MOCK or FINETUNED_MODEL; an adapter sets it as a class attribute.

        Read-only in the interface, so an adapter may declare its own single literal.
        """
        ...

    async def generate_itinerary(
        self, request: GenerationRequest
    ) -> ProviderResult[ItineraryOutput]:
        """Propose an itinerary (io-1) for a gr-1 request."""
        ...

    async def modify_itinerary(
        self, request: ModificationRequest
    ) -> ProviderResult[EditOperations]:
        """R2. In the MVP an adapter may raise ``ProviderBadRequest("not enabled")``."""
        ...

    async def health_check(self) -> HealthStatus:
        """Cheap status check; never raises and makes no generation call."""
        ...

    def get_model_metadata(self) -> ModelMetadata:
        """Provider, model and adapter identity; never raises."""
        ...
