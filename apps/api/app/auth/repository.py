"""The profiles table (migration 0003). MOD-B02 is its only writer (§5.2, IMD-14)."""

from uuid import UUID

from psycopg import errors as pg_errors
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Profile as ProfileRow


async def insert_if_absent(session: AsyncSession, user_id: UUID) -> bool:
    """Insert the profile of ``user_id`` unless it exists (insert … on conflict do nothing).

    Returns False when no auth.users row has that id (the account no longer exists); the savepoint
    keeps the caller's transaction usable in that case.
    """
    statement = insert(ProfileRow).values(id=user_id).on_conflict_do_nothing(index_elements=["id"])
    try:
        async with session.begin_nested():
            await session.execute(statement)
    except IntegrityError as exc:
        if isinstance(exc.orig, pg_errors.ForeignKeyViolation):
            return False
        raise
    return True


async def get(session: AsyncSession, user_id: UUID) -> ProfileRow | None:
    return await session.get(ProfileRow, user_id)
