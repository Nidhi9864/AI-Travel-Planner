"""Test database fixtures (specification §5.5 and §5.6; IMP-106 step 5).

``migrated_database_url`` (session scope) prepares the database at ``TEST_DATABASE_URL`` (default
§4.7) once per run: it creates the database if it is missing, applies ``test_auth_stub.sql`` only
when schema ``auth`` is absent (plain PostgreSQL; Supabase already has it), and runs
``alembic upgrade head``. ``db_session`` gives each test an ``AsyncSession`` inside one outer
transaction that is rolled back when the test ends, so tests leave no rows behind; a commit in the
code under test only releases a savepoint. ``insert_auth_user`` adds the ``auth.users`` row that a
test user's profile refers to.

Registered for every suite by one import line in ``tests/conftest.py``.
"""

import uuid
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.pool import NullPool

from app.core.config import load_settings
from app.db.session import create_engine as create_async_engine
from app.db.session import psycopg_url

DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/travel_test"
API_DIR = Path(__file__).resolve().parents[2]
ALEMBIC_INI = API_DIR / "alembic.ini"
AUTH_STUB_SQL = API_DIR / "migrations" / "sql" / "test_auth_stub.sql"


def get_test_database_url() -> str:
    """TEST_DATABASE_URL from the settings (environment or apps/api/.env), else the §4.7 default."""
    url = load_settings().test_database_url.get_secret_value().strip()
    return psycopg_url(url or DEFAULT_TEST_DATABASE_URL)


def _create_database_if_missing(url: str) -> None:
    target = make_url(url)
    name = target.database
    if not name:
        raise RuntimeError("TEST_DATABASE_URL names no database")
    server = create_engine(
        target.set(database="postgres"), poolclass=NullPool, isolation_level="AUTOCOMMIT"
    )
    try:
        with server.connect() as conn:
            exists = conn.execute(
                text("select 1 from pg_database where datname = :name"), {"name": name}
            ).first()
            if exists is None:
                quoted = conn.dialect.identifier_preparer.quote(name)
                conn.exec_driver_sql(f"create database {quoted}")
    finally:
        server.dispose()


def _apply_auth_stub_if_absent(url: str) -> None:
    # The stub holds its own begin/commit, so it runs on an autocommit connection.
    engine = create_engine(url, poolclass=NullPool, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            has_auth = conn.execute(
                text("select exists (select 1 from pg_namespace where nspname = 'auth')")
            ).scalar_one()
            if not has_auth:
                conn.exec_driver_sql(AUTH_STUB_SQL.read_text(encoding="utf-8"))
    finally:
        engine.dispose()


def _upgrade_head(url: str) -> None:
    config = Config(str(ALEMBIC_INI))
    # pytest owns logging; env.py skips fileConfig when configure_logger is False.
    config.attributes["configure_logger"] = False
    engine = create_engine(url, poolclass=NullPool)
    try:
        with engine.begin() as conn:
            config.attributes["connection"] = conn
            command.upgrade(config, "head")
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def migrated_database_url() -> str:
    """The URL of the test database, migrated to head (created and stubbed first when needed)."""
    url = get_test_database_url()
    _create_database_if_missing(url)
    _apply_auth_stub_if_absent(url)
    _upgrade_head(url)
    return url


@pytest_asyncio.fixture
async def db_session(migrated_database_url: str) -> AsyncIterator[AsyncSession]:
    """An AsyncSession in one transaction that is rolled back at the end of the test."""
    engine = create_async_engine(migrated_database_url, poolclass=NullPool)
    try:
        async with engine.connect() as conn:
            outer = await conn.begin()
            session = AsyncSession(
                bind=conn, expire_on_commit=False, join_transaction_mode="create_savepoint"
            )
            try:
                yield session
            finally:
                await session.close()
                await outer.rollback()
    finally:
        await engine.dispose()


async def insert_auth_user(
    session: AsyncSession, user_id: uuid.UUID | None = None, email: str | None = None
) -> uuid.UUID:
    """Insert a test user into auth.users (the stub's table) and return its id."""
    user_id = user_id or uuid.uuid4()
    await session.execute(
        text("insert into auth.users (id, email) values (:id, :email)"),
        {"id": user_id, "email": email or f"{user_id}@example.test"},
    )
    return user_id
