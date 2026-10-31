"""API-01 GET /health: liveness with version, environment and provider name (FR-123).

No database or provider call and never a secret; outside /api/v1 (§6.1).
"""

from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import AiProvider, AppEnv, Settings

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: Literal["ok"]
    version: str
    environment: AppEnv
    provider: AiProvider


@router.get("/health", response_model=HealthOut)
async def health(request: Request) -> HealthOut:
    settings: Settings = request.app.state.settings
    return HealthOut(
        status="ok",
        version=settings.build_version,
        environment=settings.app_env,
        provider=settings.ai_provider,
    )
