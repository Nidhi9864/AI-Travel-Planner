"""Async engine, session factory and the transaction helper (specification §5.5 and §5.8, MOD-D01).

This is the only module that creates an engine. The application uses SQLAlchemy's asyncio
extension with psycopg 3 (``postgresql+psycopg``); the URL is ``DATABASE_URL`` from the settings and
is never logged. Services open one transaction per operation with ``transaction()``, and no
transaction stays open across a provider call (§5.8).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

DRIVER = "postgresql+psycopg"


def psycopg_url(url: str) -> str:
    """The same URL with the psycopg 3 driver (a plain ``postgresql://`` URL would pick another)."""
    return make_url(url).set(drivername=DRIVER).render_as_string(hide_password=False)


def create_engine(url: str, **options: Any) -> AsyncEngine:
    """An async engine for ``url``. Options go to ``create_async_engine`` (tests pass a pool class)."""
    return create_async_engine(psycopg_url(url), pool_pre_ping=True, **options)


def create_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # Loaded attributes stay readable after commit, so a service can return what it wrote.
    return async_sessionmaker(engine, expire_on_commit=False)


@lru_cache
def get_engine() -> AsyncEngine:
    """The process-wide engine for DATABASE_URL, created on first use."""
    url = get_settings().database_url.get_secret_value().strip()
    if not url:
        raise RuntimeError("DATABASE_URL is not set (specification §4.5)")
    return create_engine(url)


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return create_sessionmaker(get_engine())


@asynccontextmanager
async def transaction() -> AsyncIterator[AsyncSession]:
    """One database transaction: committed when the block ends, rolled back if it raises.

    Usage in a service: ``async with transaction() as session: ...``.
    """
    async with get_sessionmaker()() as session, session.begin():
        yield session
