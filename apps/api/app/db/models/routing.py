"""Travel-time cache, written by MOD-B10 (migration 0004, Appendix A.5)."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class RouteCache(Base):
    __tablename__ = "route_cache"

    from_place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), primary_key=True
    )
    to_place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE"), primary_key=True
    )
    mode: Mapped[str] = mapped_column(Text, primary_key=True)
    travel_minutes: Mapped[int] = mapped_column(Integer)
    distance_m: Mapped[int] = mapped_column(Integer)
    travel_source: Mapped[str] = mapped_column(Text)
    provider_name: Mapped[str | None] = mapped_column(Text)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
