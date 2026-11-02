"""API-01 GET /health: liveness with version, environment and provider name (FR-123).

No database or provider call and never a secret; outside /api/v1 (§6.1).

API-02 GET /health/ready is declared with its final shape and answers 501 NOT_IMPLEMENTED until
IMP-201 builds the checks (IMD-37).
"""

from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.config import AiProvider, AppEnv, Settings
from app.core.errors import EndpointNotImplemented

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: Literal["ok"]
    version: str
    environment: AppEnv
    provider: AiProvider


@router.get("/health", response_model=HealthOut, summary="API-01 Liveness")
async def health(request: Request) -> HealthOut:
    settings: Settings = request.app.state.settings
    return HealthOut(
        status="ok",
        version=settings.build_version,
        environment=settings.app_env,
        provider=settings.ai_provider,
    )


class ProviderCheck(BaseModel):
    name: AiProvider
    model_id: str
    status: Literal["ok", "degraded", "down"]


class ReadinessChecks(BaseModel):
    database: Literal["ok", "down"]
    migration: str = Field(description="The Alembic head, or 'behind'")
    provider: ProviderCheck


class ReadinessOut(BaseModel):
    status: Literal["ready", "degraded", "not_ready"]
    version: str
    checks: ReadinessChecks


@router.get(
    "/health/ready",
    response_model=ReadinessOut,
    responses={503: {"model": ReadinessOut, "description": "The database is down"}},
    summary="API-02 Readiness",
)
async def ready() -> ReadinessOut:
    raise EndpointNotImplemented()
