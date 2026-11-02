"""Auth stub bootstrap and user row mirroring (IMP-219; TC-439, TC-440; FR-003, NFR-020, NFR-022;
Amendment A1 §5.1).

The mirroring tests run the real app on the migrated test database (stub present) inside the
test's rolled-back transaction. The command tests connect on their own, as the release task does:
the bootstrap test uses a scratch database that it drops afterwards, and the delete-user test
commits its rows and removes them again.
"""

import uuid
from collections.abc import AsyncIterator, Iterator
from datetime import date

import httpx
import psycopg
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fixtures.auth import auth_test_settings, bearer, client_for, make_token
from fixtures.db import insert_auth_user
from psycopg import sql
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import deps
from app.db import admin, auth_stub
from app.db.auth_stub import libpq_url
from app.main import create_app


def _app(db_session: AsyncSession, *, stub: bool) -> FastAPI:
    app = create_app(auth_test_settings(db_auth_stub=stub))

    async def test_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[deps.db_session] = test_session
    return app


@pytest_asyncio.fixture
async def stub_client(db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    async with client_for(_app(db_session, stub=True)) as client:
        yield client


@pytest_asyncio.fixture
async def plain_client(db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    async with client_for(_app(db_session, stub=False)) as client:
        yield client


async def _count(session: AsyncSession, table: str, user_id: uuid.UUID) -> int:
    query = text(f"select count(*) from {table} where id = :id")  # noqa: S608  # fixed table names
    return int((await session.execute(query, {"id": user_id})).scalar_one())


# ---------- TC-439: mirroring on the first call ----------


@pytest.mark.asyncio
async def test_auth_stub_first_call_mirrors_the_user_then_creates_nothing(
    stub_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    user_id = uuid.uuid4()  # a hosted-Auth user that the database has never seen
    headers = bearer(make_token(user_id, email="new.traveller@example.test"))

    first = await stub_client.get("/api/v1/me", headers=headers)
    assert first.status_code == 200
    assert first.json()["id"] == str(user_id)
    assert first.json()["email"] == "new.traveller@example.test"  # from the token only
    assert await _count(db_session, "auth.users", user_id) == 1
    assert await _count(db_session, "public.profiles", user_id) == 1
    stored_email = await db_session.scalar(
        text("select email from auth.users where id = :id"), {"id": user_id}
    )
    assert stored_email is None  # NFR-020: the e-mail claim is never written

    second = await stub_client.get("/api/v1/me", headers=headers)
    assert second.status_code == 200
    assert await _count(db_session, "auth.users", user_id) == 1
    assert await _count(db_session, "public.profiles", user_id) == 1


@pytest.mark.asyncio
async def test_auth_stub_mirroring_keeps_an_existing_auth_row(
    stub_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    user_id = await insert_auth_user(db_session, email="known@example.test")
    response = await stub_client.get(
        "/api/v1/me", headers=bearer(make_token(user_id, email="other@example.test"))
    )
    assert response.status_code == 200
    stored_email = await db_session.scalar(
        text("select email from auth.users where id = :id"), {"id": user_id}
    )
    assert stored_email == "known@example.test"


@pytest.mark.asyncio
async def test_auth_stub_setting_false_writes_no_auth_row(
    plain_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    user_id = uuid.uuid4()
    response = await plain_client.get(
        "/api/v1/me", headers=bearer(make_token(user_id, email="new@example.test"))
    )
    # As before IMP-219: a token whose user has no auth.users row is refused (IMP-108).
    assert response.status_code == 401
    assert await _count(db_session, "auth.users", user_id) == 0
    assert await _count(db_session, "public.profiles", user_id) == 0


# ---------- TC-440: auth_stub --if-missing ----------


@pytest.fixture
def scratch_database(migrated_database_url: str) -> Iterator[str]:
    """A blank database on the test server (no schema auth), dropped afterwards."""
    url = make_url(migrated_database_url)
    name = f"{url.database}_stub_{uuid.uuid4().hex[:8]}"
    server = libpq_url(url.set(database="postgres").render_as_string(hide_password=False))
    with psycopg.connect(server, autocommit=True) as conn:
        conn.execute(sql.SQL("create database {}").format(sql.Identifier(name)))
    try:
        yield url.set(database=name).render_as_string(hide_password=False)
    finally:
        with psycopg.connect(server, autocommit=True) as conn:
            conn.execute(
                sql.SQL("drop database if exists {} with (force)").format(sql.Identifier(name))
            )


def _run_stub(monkeypatch: pytest.MonkeyPatch, database_url: str) -> int:
    monkeypatch.setenv("DATABASE_URL", database_url)
    return auth_stub.main(["--if-missing"])


def test_auth_stub_applies_once_on_a_database_without_auth(
    clean_settings_env: pytest.MonkeyPatch,
    scratch_database: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run_stub(clean_settings_env, scratch_database) == 0
    assert capsys.readouterr().out.strip() == "auth stub: applied"
    with psycopg.connect(libpq_url(scratch_database)) as conn:
        assert conn.execute("select to_regclass('auth.users') is not null").fetchone() == (True,)
        assert conn.execute("select to_regproc('auth.uid') is not null").fetchone() == (True,)

    assert _run_stub(clean_settings_env, scratch_database) == 0
    assert capsys.readouterr().out.strip() == "auth schema present; nothing to do"


def test_auth_stub_is_a_no_op_when_schema_auth_exists(
    clean_settings_env: pytest.MonkeyPatch,
    migrated_database_url: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert _run_stub(clean_settings_env, migrated_database_url) == 0
    assert capsys.readouterr().out.strip() == "auth schema present; nothing to do"


def test_auth_stub_failure_exits_1_without_printing_the_url(
    clean_settings_env: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    password = "never-printed-test-password"  # noqa: S105  # fake, the port is closed
    url = f"postgresql+psycopg://stub-user:{password}@127.0.0.1:9/nowhere"
    assert _run_stub(clean_settings_env, url) == 1
    output = capsys.readouterr()
    assert password not in output.out + output.err
    assert "127.0.0.1" not in output.out + output.err


# ---------- NFR-022: app.db.admin delete-user ----------

DESTINATION_SQL = """
insert into public.destinations (id, slug, name, country_code, timezone, currency, center_lat,
  center_lon, bbox_min_lat, bbox_max_lat, bbox_min_lon, bbox_max_lon, is_sample)
values (%(id)s, %(slug)s, 'Admin delete check (SAMPLE)', 'GB', 'Europe/London', 'GBP',
  51.5, -0.1, 51.0, 52.0, -1.0, 1.0, true)
"""


def test_auth_stub_delete_user_refuses_when_the_setting_is_false(
    clean_settings_env: pytest.MonkeyPatch,
    migrated_database_url: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    clean_settings_env.setenv("DATABASE_URL", migrated_database_url)
    clean_settings_env.setenv("DB_AUTH_STUB", "false")
    assert admin.main(["delete-user", "--user-id", str(uuid.uuid4())]) == 1
    assert "refused" in capsys.readouterr().err


def test_auth_stub_delete_user_cascades_to_profile_and_trips(
    clean_settings_env: pytest.MonkeyPatch,
    migrated_database_url: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    conninfo = libpq_url(migrated_database_url)
    user_id, destination_id = uuid.uuid4(), uuid.uuid4()
    with psycopg.connect(conninfo) as conn, conn.transaction():
        conn.execute(DESTINATION_SQL, {"id": destination_id, "slug": f"del-{user_id.hex[:8]}"})
        conn.execute("insert into auth.users (id) values (%s)", (user_id,))
        conn.execute("insert into public.profiles (id) values (%s)", (user_id,))
        conn.execute(
            "insert into public.trips (user_id, destination_id, title, start_date, end_date)"
            " values (%s, %s, 'SAMPLE trip', %s, %s)",
            (user_id, destination_id, date(2026, 12, 4), date(2026, 12, 5)),
        )
    try:
        clean_settings_env.setenv("DATABASE_URL", migrated_database_url)
        clean_settings_env.setenv("DB_AUTH_STUB", "true")
        assert admin.main(["delete-user", "--user-id", str(user_id)]) == 0
        assert capsys.readouterr().out.strip() == "delete-user: 1 row(s) deleted"
        with psycopg.connect(conninfo) as conn:
            counts = conn.execute(
                "select (select count(*) from auth.users where id = %(id)s),"
                " (select count(*) from public.profiles where id = %(id)s),"
                " (select count(*) from public.trips where user_id = %(id)s)",
                {"id": user_id},
            ).fetchone()
        assert counts == (0, 0, 0)  # auth.users, profiles, trips
    finally:
        with psycopg.connect(conninfo) as conn, conn.transaction():
            conn.execute("delete from auth.users where id = %s", (user_id,))
            conn.execute("delete from public.destinations where id = %s", (destination_id,))
