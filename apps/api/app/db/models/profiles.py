"""Profiles, written by MOD-B02 (migration 0003, Appendix A.4).

``profiles.id`` equals ``auth.users.id``. The SQL foreign key to ``auth.users`` is not declared
here because the auth schema belongs to Supabase Auth and is not part of this metadata.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CHAR, DateTime, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    display_name: Mapped[str | None] = mapped_column(Text)
    home_country: Mapped[str | None] = mapped_column(CHAR(2))
    preferred_currency: Mapped[str | None] = mapped_column(CHAR(3))
    ai_notice_ack_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    default_preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
