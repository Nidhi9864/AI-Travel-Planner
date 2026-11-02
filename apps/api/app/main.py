"""App factory and the ASGI app that `make api` runs (uvicorn app.main:app).

`create_app` applies the start-up checks before anything else, so a bad configuration stops the
process with a message that names the variable, never its value (FR-124). The lifespan then
resolves the model provider and the prompt template (§8.4, IMP-208); a ConfigError there also
stops start-up.
"""

import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ai.factory import startup_provider
from app.auth.deps import current_user
from app.auth.router import router as auth_router
from app.budget.router import router as budget_router
from app.core.config import ConfigError, Settings, check_settings, get_settings
from app.core.errors import register_error_handlers
from app.core.health import router as health_router
from app.core.request_id import REQUEST_ID_HEADER, RequestIdMiddleware
from app.generation.router import router as generation_router
from app.itinerary.router import router as itinerary_router
from app.places.router import router as places_router
from app.schemas.common import ErrorEnvelope
from app.trips.router import router as trips_router

logger = logging.getLogger(__name__)

API_V1_PREFIX = "/api/v1"

# §6.1 CORS: exact origins, these methods and headers, no credentials (bearer token).
CORS_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
CORS_HEADERS = ["Authorization", "Content-Type", REQUEST_ID_HEADER]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    for warning in check_settings(settings, os.environ):
        logger.warning(warning)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            app.state.model_provider = await startup_provider(settings)
        except ConfigError as exc:
            logger.error("configuration error: %s", exc)
            raise
        yield

    # /docs is enabled in local, test and staging; production serves no OpenAPI page (§6.1).
    docs_enabled = settings.app_env != "production"
    app = FastAPI(
        lifespan=lifespan,
        title="AI Travel Planner API",
        version=settings.build_version,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
        # Every non-2xx answer is the §6.3 envelope; this also replaces FastAPI's own 422 shape.
        responses={"default": {"model": ErrorEnvelope, "description": "Error envelope (§6.3)"}},
    )
    app.state.settings = settings

    register_error_handlers(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
        allow_credentials=False,
    )
    # Added last, so it is the outermost of these and also tags CORS preflight responses.
    app.add_middleware(RequestIdMiddleware)

    app.include_router(health_router)
    # Mount point of every resource router (§6.1); the module cards add theirs here.
    # CurrentUser guards the whole prefix (IMP-108), so every new route requires a valid token by
    # default; /health and the docs stay outside it.
    api_v1 = APIRouter(prefix=API_V1_PREFIX, dependencies=[Depends(current_user)])
    api_v1.include_router(auth_router)
    api_v1.include_router(trips_router)
    api_v1.include_router(places_router)
    api_v1.include_router(generation_router)
    api_v1.include_router(itinerary_router)
    api_v1.include_router(budget_router)
    app.include_router(api_v1)
    return app


def __getattr__(name: str) -> FastAPI:
    # `app` is built on first access (uvicorn's `app.main:app` lookup), so importing this module
    # for `create_app` reads no settings. A bad configuration exits non-zero with the rules that
    # failed; the message never holds a value.
    if name != "app":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    try:
        application = create_app()
    except ConfigError as exc:
        sys.exit(f"configuration error: {exc}")
    globals()["app"] = application
    return application
