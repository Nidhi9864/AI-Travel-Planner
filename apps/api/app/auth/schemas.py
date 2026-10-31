"""Auth request and response shapes (specification §6.5 Profile, §6.6.1 API-03)."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class Profile(BaseModel):
    """The caller's profile. `email` comes from the token and is never stored (§6.5)."""

    id: UUID
    email: str | None
    display_name: str | None
    home_country: str | None
    preferred_currency: str | None
    default_preferences: dict[str, Any] = Field(
        description="PreferencesIn keys except notes and must_visit_place_ids (FR-004); "
        "typed and validated by API-04 (IMP-601)",
    )
    ai_notice_ack_at: datetime | None
