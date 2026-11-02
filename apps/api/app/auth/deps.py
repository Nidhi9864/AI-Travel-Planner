"""The CurrentUser dependency (specification §3.4, §6.2; IMD-04, IMD-14, IMD-45).

The user ID comes only from the verified bearer token; no endpoint accepts it in a path, query or
body. The token is checked before a database session is opened, so a call without a valid token
never reaches the database. On every authenticated call CurrentUser ensures the caller's profile
row exists (insert … on conflict do nothing).
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import service
from app.auth.tokens import TokenClaims, verifier_for
from app.core.config import Settings
from app.core.errors import Unauthenticated
from app.db.session import transaction

# auto_error=False: a missing or non-bearer header becomes our 401 envelope, not FastAPI's error.
bearer_scheme = HTTPBearer(
    auto_error=False, description="Supabase access token: Authorization: Bearer <token>"
)


async def verified_claims(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> TokenClaims:
    if credentials is None or not credentials.credentials:
        raise Unauthenticated()
    settings: Settings = request.app.state.settings
    return await verifier_for(settings).verify(credentials.credentials)


async def db_session() -> AsyncIterator[AsyncSession]:
    """One transaction per request for the auth module: committed after the handler, rolled back
    if it raises. Tests override this dependency with their rolled-back session."""
    async with transaction() as session:
        yield session


DbSession = Annotated[AsyncSession, Depends(db_session)]


async def current_user(
    claims: Annotated[TokenClaims, Depends(verified_claims)], session: DbSession, request: Request
) -> TokenClaims:
    # verified_claims is resolved first (parameter order), so db_session opens only for a valid token.
    settings: Settings = request.app.state.settings
    await service.get_or_create_profile(
        session, claims.user_id, mirror_auth_user=settings.db_auth_stub
    )
    return claims


CurrentUser = Annotated[TokenClaims, Depends(current_user)]
