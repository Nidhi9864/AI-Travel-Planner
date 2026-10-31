"""``make db-reset`` step 1 (specification §4.7, §5.7): empty a local or test database.

Refuses unless ``APP_ENV`` is local or test and the host of ``DATABASE_URL`` is localhost or
127.0.0.1. Then it drops and recreates schema public (every table, the data and
``alembic_version``) and, on a plain PostgreSQL without schema auth, applies the auth test stub.
The Makefile then runs ``make db-migrate`` and ``make seed``. Staging and production are never
reset. The URL is never printed.
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url

from app.core.config import get_settings
from app.db.session import create_engine

ALLOWED_ENVS = ("local", "test")
LOCAL_HOSTS = ("localhost", "127.0.0.1")
AUTH_STUB_SQL = Path(__file__).resolve().parents[2] / "migrations" / "sql" / "test_auth_stub.sql"


class ResetRefusedError(Exception):
    """The database may not be reset from this environment."""


def check_allowed(app_env: str, database_url: str) -> None:
    if app_env not in ALLOWED_ENVS:
        raise ResetRefusedError(
            f"APP_ENV is {app_env}; db-reset runs only when it is local or test"
        )
    if not database_url:
        raise ResetRefusedError("DATABASE_URL is not set")
    if make_url(database_url).host not in LOCAL_HOSTS:
        raise ResetRefusedError("the DATABASE_URL host is not localhost or 127.0.0.1")


async def reset(database_url: str) -> bool:
    """Drop and recreate schema public; returns True when the auth stub was applied."""
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as conn:
            await conn.execute(text("drop schema if exists public cascade"))
            await conn.execute(text("create schema public"))
            # The default privilege of schema public (PostgreSQL 15 and later): usage for all.
            await conn.execute(text("grant usage on schema public to public"))
            has_auth = await conn.scalar(
                text("select exists (select 1 from pg_namespace where nspname = 'auth')")
            )
            if not has_auth:
                # Plain PostgreSQL (compose db): the stub stands in for Supabase's auth schema.
                await conn.exec_driver_sql(AUTH_STUB_SQL.read_text(encoding="utf-8"))
            return not has_auth
    finally:
        await engine.dispose()


def main() -> int:
    settings = get_settings()
    database_url = settings.database_url.get_secret_value().strip()
    try:
        check_allowed(settings.app_env, database_url)
    except ResetRefusedError as exc:
        print(f"db-reset: refused: {exc}", file=sys.stderr)
        return 1
    stub_applied = asyncio.run(reset(database_url))
    print(
        "db-reset: schema public dropped and recreated"
        + ("; auth test stub applied" if stub_applied else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
