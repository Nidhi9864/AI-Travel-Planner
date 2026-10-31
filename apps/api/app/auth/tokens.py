"""Supabase access-token verification (specification §3.4, §6.2; IMD-04).

With ``SUPABASE_JWKS_URL`` set, tokens are verified with the project's published asymmetric keys
(5 s fetch timeout, key set cached 10 minutes); otherwise with HS256 and ``SUPABASE_JWT_SECRET``.
Every token must carry ``exp``, a UUID ``sub`` and ``aud`` = ``authenticated``. Any failure is the
same 401 UNAUTHENTICATED with the same message, so a caller never learns which check failed. A key
set that cannot be fetched (and no cached key matches) is 503 SERVICE_UNAVAILABLE. Tokens are
never logged.
"""

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Protocol
from uuid import UUID

import anyio
import jwt

from app.core.config import Settings
from app.core.errors import ServiceUnavailable, Unauthenticated

logger = logging.getLogger(__name__)

AUDIENCE = "authenticated"
REQUIRED_CLAIMS = ["exp", "sub", "aud"]
HS256 = ["HS256"]
# Asymmetric algorithms Supabase signing keys use; "none" and HMAC are never accepted with JWKS.
JWKS_ALGORITHMS = ["ES256", "RS256", "EdDSA"]
JWKS_FETCH_TIMEOUT_S = 5
JWKS_CACHE_S = 600


@dataclass(frozen=True)
class TokenClaims:
    user_id: UUID
    email: str | None


class SigningKeySource(Protocol):
    """The part of ``jwt.PyJWKClient`` used here (tests pass a fake)."""

    def get_signing_key_from_jwt(self, token: str) -> Any: ...


@lru_cache(maxsize=4)
def jwks_client(url: str) -> jwt.PyJWKClient:
    """One client per JWKS URL for the process; it caches the key set and its keys."""
    return jwt.PyJWKClient(
        url, cache_keys=True, lifespan=JWKS_CACHE_S, timeout=JWKS_FETCH_TIMEOUT_S
    )


def _reject(reason: str) -> Unauthenticated:
    # Only the reason class is logged, never the token or a claim value.
    logger.info("access token rejected: %s", reason)
    return Unauthenticated()


def claims_from_payload(payload: dict[str, Any]) -> TokenClaims:
    try:
        user_id = UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise _reject("sub is not a UUID") from exc
    email = payload.get("email")
    return TokenClaims(user_id=user_id, email=email if isinstance(email, str) else None)


class TokenVerifier:
    """Verifies one bearer token per call; built from the settings by ``verifier_for``."""

    def __init__(self, *, jwt_secret: str = "", key_source: SigningKeySource | None = None) -> None:
        self._jwt_secret = jwt_secret
        self._key_source = key_source

    async def verify(self, token: str) -> TokenClaims:
        if self._key_source is not None:
            key = await self._signing_key(self._key_source, token)
            return self._decode(token, key, JWKS_ALGORITHMS)
        if not self._jwt_secret:
            logger.error("token verification is not configured (SUPABASE_JWT_SECRET is empty)")
            raise ServiceUnavailable()
        return self._decode(token, self._jwt_secret, HS256)

    @staticmethod
    async def _signing_key(source: SigningKeySource, token: str) -> Any:
        try:
            # PyJWKClient fetches over the network synchronously; keep it off the event loop.
            signing_key = await anyio.to_thread.run_sync(source.get_signing_key_from_jwt, token)
        except jwt.PyJWKClientConnectionError as exc:
            logger.warning("JWKS key set could not be fetched")
            raise ServiceUnavailable() from exc
        except (jwt.PyJWKClientError, jwt.InvalidTokenError) as exc:
            raise _reject(type(exc).__name__) from exc
        return signing_key.key

    @staticmethod
    def _decode(token: str, key: Any, algorithms: list[str]) -> TokenClaims:
        try:
            payload = jwt.decode(
                token,
                key,
                algorithms=algorithms,
                audience=AUDIENCE,
                options={"require": REQUIRED_CLAIMS},
            )
        except jwt.InvalidTokenError as exc:
            raise _reject(type(exc).__name__) from exc
        return claims_from_payload(payload)


def verifier_for(settings: Settings) -> TokenVerifier:
    """JWKS when SUPABASE_JWKS_URL is set, otherwise HS256 with SUPABASE_JWT_SECRET (IMD-04)."""
    jwks_url = settings.supabase_jwks_url.strip()
    if jwks_url:
        return TokenVerifier(key_source=jwks_client(jwks_url))
    return TokenVerifier(jwt_secret=settings.supabase_jwt_secret.get_secret_value())
