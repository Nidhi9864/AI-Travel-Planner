"""Profile service (MOD-B02): ensures and reads the caller's profile (§3.4 rule 4, IMD-14)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import repository
from app.auth.schemas import Profile
from app.core.errors import NotFound, Unauthenticated


async def get_or_create_profile(session: AsyncSession, user_id: UUID) -> None:
    """Create the profile row on the first authenticated call; later calls change nothing.

    Called only by the CurrentUser dependency; trips.user_id references profiles.id, so the row
    must exist before any trip is written.
    """
    if not await repository.insert_if_absent(session, user_id):
        # A valid token for an account that no longer exists in auth.users.
        raise Unauthenticated()


async def get_profile(session: AsyncSession, user_id: UUID, email: str | None) -> Profile:
    row = await repository.get(session, user_id)
    if row is None:
        raise NotFound()
    return Profile(
        id=row.id,
        email=email,
        display_name=row.display_name,
        home_country=row.home_country,
        preferred_currency=row.preferred_currency,
        default_preferences=row.default_preferences,
        ai_notice_ack_at=row.ai_notice_ack_at,
    )
