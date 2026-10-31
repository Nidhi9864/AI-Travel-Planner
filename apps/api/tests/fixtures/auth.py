"""Auth test helpers (IMP-108 step 4): HS256 test tokens, test settings and an API client.

Tokens are signed with ``TEST_JWT_SECRET``, a value that exists only in tests; no real key is
used anywhere. ``api_client`` runs the real app with the database dependency pointed at the
rolled-back ``db_session`` of tests/fixtures/db.py; ``auth_user`` inserts the auth.users row a
test user's profile refers to.
"""

import hashlib
import time
import uuid
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
import pytest_asyncio
from fastapi import FastAPI
from fixtures.db import insert_auth_user
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import deps
from app.core.config import Settings
from app.main import create_app

# Test-only HS256 secret, derived at import so no secret-like literal sits in the repository.
TEST_JWT_SECRET = hashlib.sha256(b"imp-108 pytest only, never a real Supabase secret").hexdigest()
AUDIENCE = "authenticated"


def make_token(
    user_id: uuid.UUID | str,
    *,
    expired: bool = False,
    wrong_aud: bool = False,
    secret: str = TEST_JWT_SECRET,
    email: str | None = None,
    omit: Iterable[str] = (),
    algorithm: str = "HS256",
    **claims: Any,
) -> str:
    """A Supabase-shaped access token; the flags produce the failure cases of TC-347."""
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "aud": "anon" if wrong_aud else AUDIENCE,
        "exp": now - 60 if expired else now + 600,
        "iat": now - 120 if expired else now,
        "role": "authenticated",
        **({"email": email} if email is not None else {}),
        **claims,
    }
    for name in omit:
        payload.pop(name, None)
    return jwt.encode(payload, secret, algorithm=algorithm)


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def auth_test_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": "test",
        "ai_provider": "MOCK",
        # Never connected to: requests reach the test database through the db_session override.
        "database_url": "postgresql+psycopg://unused:unused@127.0.0.1:9/unused",
        "supabase_jwt_secret": TEST_JWT_SECRET,
        "supabase_jwks_url": "",
        **overrides,
    }
    return Settings(**values)


def client_for(app: FastAPI) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


@dataclass(frozen=True)
class AuthUser:
    user_id: uuid.UUID
    email: str

    @property
    def token(self) -> str:
        return make_token(self.user_id, email=self.email)

    @property
    def headers(self) -> dict[str, str]:
        return bearer(self.token)


@pytest_asyncio.fixture
async def api_app(db_session: AsyncSession) -> FastAPI:
    """The real app; its per-request transaction is the test's rolled-back session."""
    app = create_app(auth_test_settings())

    async def test_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[deps.db_session] = test_session
    return app


@pytest_asyncio.fixture
async def api_client(api_app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with client_for(api_app) as client:
        yield client


@pytest_asyncio.fixture
async def auth_user(db_session: AsyncSession) -> AuthUser:
    """A user that exists in auth.users (the stub's table); no profile row yet."""
    user_id = uuid.uuid4()
    email = f"{user_id}@example.test"
    await insert_auth_user(db_session, user_id, email)
    return AuthUser(user_id=user_id, email=email)
