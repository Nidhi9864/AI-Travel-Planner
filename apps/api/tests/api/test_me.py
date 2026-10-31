"""API-03 GET /api/v1/me and first-call profile creation (§6.6.1, IMD-14; IMP-108: TC-057).

Runs against the migrated test database (tests/fixtures/db.py); every test is rolled back.
"""

import uuid

import httpx
import pytest
from fixtures.auth import AuthUser, bearer, make_token
from fixtures.db import insert_auth_user
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Profile as ProfileRow

PROFILE_FIELDS = {
    "id",
    "email",
    "display_name",
    "home_country",
    "preferred_currency",
    "default_preferences",
    "ai_notice_ack_at",
}


async def profile_rows(session: AsyncSession, user_id: uuid.UUID) -> int:
    query = select(func.count()).select_from(ProfileRow).where(ProfileRow.id == user_id)
    return int((await session.execute(query)).scalar_one())


@pytest.mark.asyncio
async def test_me_creates_exactly_one_profile_on_the_first_call(
    api_client: httpx.AsyncClient, db_session: AsyncSession, auth_user: AuthUser
) -> None:
    assert await profile_rows(db_session, auth_user.user_id) == 0

    first = await api_client.get("/api/v1/me", headers=auth_user.headers)
    assert first.status_code == 200
    assert await profile_rows(db_session, auth_user.user_id) == 1

    second = await api_client.get("/api/v1/me", headers=auth_user.headers)
    assert second.status_code == 200
    assert second.json() == first.json()
    assert await profile_rows(db_session, auth_user.user_id) == 1


@pytest.mark.asyncio
async def test_tc_057_me_returns_the_token_users_profile(
    api_client: httpx.AsyncClient, auth_user: AuthUser
) -> None:
    response = await api_client.get("/api/v1/me", headers=auth_user.headers)

    assert response.status_code == 200
    profile = response.json()
    assert set(profile) == PROFILE_FIELDS
    assert profile["id"] == str(auth_user.user_id)
    # The email comes from the token; it is not stored in profiles.
    assert profile["email"] == auth_user.email
    assert profile["display_name"] is None
    assert profile["default_preferences"] == {}
    assert profile["ai_notice_ack_at"] is None


@pytest.mark.asyncio
async def test_me_never_returns_another_users_profile(
    api_client: httpx.AsyncClient, auth_user: AuthUser, db_session: AsyncSession
) -> None:
    other = uuid.uuid4()
    await insert_auth_user(db_session, other)
    mine = (await api_client.get("/api/v1/me", headers=auth_user.headers)).json()
    theirs = (await api_client.get("/api/v1/me", headers=bearer(make_token(other)))).json()

    assert mine["id"] == str(auth_user.user_id)
    assert theirs["id"] == str(other)


@pytest.mark.asyncio
async def test_me_without_a_token_is_401_and_creates_nothing(
    api_client: httpx.AsyncClient, db_session: AsyncSession, auth_user: AuthUser
) -> None:
    response = await api_client.get("/api/v1/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"
    assert await profile_rows(db_session, auth_user.user_id) == 0


@pytest.mark.asyncio
async def test_a_valid_token_for_a_deleted_account_is_401(
    api_client: httpx.AsyncClient, db_session: AsyncSession
) -> None:
    # Signed correctly, but no auth.users row exists: no profile can be created for it.
    ghost = uuid.uuid4()
    response = await api_client.get("/api/v1/me", headers=bearer(make_token(ghost)))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"
    assert await profile_rows(db_session, ghost) == 0
