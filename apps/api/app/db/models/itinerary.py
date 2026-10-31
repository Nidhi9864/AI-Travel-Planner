"""The current plan, its findings and versions, written by MOD-B08 (migration 0004, Appendix A.5)."""

import uuid
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    CHAR,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class ItineraryDay(Base):
    __tablename__ = "itinerary_days"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    day_number: Mapped[int] = mapped_column(SmallInteger)
    plan_date: Mapped[date] = mapped_column(Date)
    theme: Mapped[str | None] = mapped_column(Text)
    source_generation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_generations.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class ItineraryItem(Base):
    __tablename__ = "itinerary_items"
    # An item belongs to the same trip as its day (§5.3).
    __table_args__ = (
        ForeignKeyConstraint(
            ["day_id", "trip_id"],
            ["itinerary_days.id", "itinerary_days.trip_id"],
            ondelete="CASCADE",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    day_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    position: Mapped[int] = mapped_column(SmallInteger)
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="RESTRICT")
    )
    slot_type: Mapped[str] = mapped_column(Text, server_default=text("'activity'"))
    start_time: Mapped[time] = mapped_column(Time)
    duration_min: Mapped[int] = mapped_column(Integer)
    origin: Mapped[str] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    note_origin: Mapped[str] = mapped_column(Text, server_default=text("'none'"))
    is_locked: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    cost_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    cost_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    cost_currency: Mapped[str | None] = mapped_column(CHAR(3))
    cost_label: Mapped[str | None] = mapped_column(Text)
    travel_from_prev_min: Mapped[int | None] = mapped_column(Integer)
    travel_from_prev_m: Mapped[int | None] = mapped_column(Integer)
    travel_mode: Mapped[str | None] = mapped_column(Text)
    travel_source: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class ItineraryWarning(Base):
    __tablename__ = "itinerary_warnings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    plan_revision: Mapped[int] = mapped_column(Integer)
    code: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(Text)
    message: Mapped[str] = mapped_column(Text)
    day_number: Mapped[int | None] = mapped_column(SmallInteger)
    item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("itinerary_items.id", ondelete="CASCADE")
    )
    place_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE")
    )
    suggested_fix: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class ItineraryVersion(Base):
    __tablename__ = "itinerary_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    version_no: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text)
    plan_revision: Mapped[int] = mapped_column(Integer)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    validation_summary: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    generation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_generations.id", ondelete="SET NULL")
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
