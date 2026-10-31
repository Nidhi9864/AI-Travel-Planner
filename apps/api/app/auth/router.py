"""API-03 GET /api/v1/me (specification §6.6.1; FR-002, FR-003, FR-004; IMD-14).

IMP-305 adds the ai_notice_acknowledged flag of API-04 and IMP-601 the editable profile fields.
"""

from fastapi import APIRouter

from app.auth import service
from app.auth.deps import CurrentUser, DbSession
from app.auth.schemas import Profile

router = APIRouter(tags=["profile"])


@router.get("/me", response_model=Profile, summary="API-03 Read my profile")
async def get_me(user: CurrentUser, session: DbSession) -> Profile:
    # The profile row was ensured by CurrentUser in this same request (IMD-14).
    return await service.get_profile(session, user.user_id, user.email)
