"""API-01 GET /health: liveness with version, environment and provider name (FR-123).

No database or provider call and never a secret; outside /api/v1 (§6.1).

API-02 GET /health/ready: readiness (FR-123 AC2, IMP-201). ``select 1`` with a 2 s timeout, the
applied Alembic revision against ``MIGRATION_HEAD``, and the active provider's ``health_check()``
cached for 60 s. The database down answers 503 ``not_ready``; a provider that is not ok or a
database behind the head answers 200 ``degraded`` (PD-12, FR-044 AC2). The ECS health check uses
/health, not this route (Amendment A1 §4.3).
"""

import asyncio
import logging
import time
from typing import Final, Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from app.ai.factory import get_model_provider
from app.core.config import AiProvider, AppEnv, Settings
from app.db.session import create_engine
from app.schemas.ai import HealthStatus

logger = logging.getLogger(__name__)

# The image ships no migrations folder (Dockerfile), so the head is a constant here;
# tests/api/test_health.py fails when it differs from the head of migrations/versions.
MIGRATION_HEAD: Final = "0007"
DATABASE_TIMEOUT_S: Final = 2.0
PROVIDER_CACHE_S: Final = 60.0

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
async def ready(request: Request) -> ReadinessOut | JSONResponse:
    settings: Settings = request.app.state.settings
    revision = await _applied_revision(settings)
    provider = get_model_provider(request)
    health = await _provider_health(request)
    checks = ReadinessChecks(
        database="down" if revision is None else "ok",
        migration=MIGRATION_HEAD if revision == MIGRATION_HEAD else "behind",
        provider=ProviderCheck(
            name=provider.name,
            model_id=provider.get_model_metadata().model_id,
            status=health.status,
        ),
    )
    if checks.database == "down":
        body = ReadinessOut(status="not_ready", version=settings.build_version, checks=checks)
        return JSONResponse(body.model_dump(mode="json"), status_code=503)
    ok = checks.migration == MIGRATION_HEAD and health.status == "ok"
    return ReadinessOut(
        status="ready" if ok else "degraded", version=settings.build_version, checks=checks
    )


async def _applied_revision(settings: Settings) -> str | None:
    """The revision in alembic_version ("" when the table is empty), or None when the database is
    unreachable. A fresh connection each call, so a pooled one never hides an outage."""
    engine = create_engine(
        settings.database_url.get_secret_value(),
        poolclass=NullPool,
        connect_args={"connect_timeout": int(DATABASE_TIMEOUT_S)},
    )
    try:
        async with asyncio.timeout(DATABASE_TIMEOUT_S), engine.connect() as conn:
            await conn.execute(text("select 1"))
            if not await conn.scalar(text("select to_regclass('alembic_version') is not null")):
                return ""  # reachable but never migrated
            revision = await conn.scalar(text("select max(version_num) from alembic_version"))
            return str(revision or "")
    except (SQLAlchemyError, OSError, TimeoutError) as exc:
        # The class name only: a driver message may carry the host or user name.
        logger.warning("readiness: database check failed (%s)", type(exc).__name__)
        return None
    finally:
        await engine.dispose()


async def _provider_health(request: Request) -> HealthStatus:
    """The provider's health_check(), cached on the app for PROVIDER_CACHE_S seconds."""
    cached: tuple[float, HealthStatus] | None = getattr(request.app.state, "provider_health", None)
    now = time.monotonic()
    if cached is not None and now - cached[0] < PROVIDER_CACHE_S:
        return cached[1]
    health = await get_model_provider(request).health_check()
    request.app.state.provider_health = (now, health)
    return health
