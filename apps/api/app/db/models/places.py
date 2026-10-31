"""Reference data and trip places, written by MOD-B04 (migrations 0002 and 0003, Appendix A.3, A.4).

destinations, data_sources, places and place_opening_hours are written only by the seed; trip_places
holds the must-visit, saved and rejected places of a trip.
"""

import uuid
from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    ARRAY,
    CHAR,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    Text,
    Time,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Destination(Base):
    __tablename__ = "destinations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    slug: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(Text)
    country_code: Mapped[str] = mapped_column(CHAR(2))
    timezone: Mapped[str] = mapped_column(Text)
    currency: Mapped[str] = mapped_column(CHAR(3))
    center_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    center_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    bbox_min_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    bbox_max_lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    bbox_min_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    bbox_max_lon: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    is_sample: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(Text)
    licence: Mapped[str] = mapped_column(Text)
    attribution_text: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    retrieved_on: Mapped[date | None] = mapped_column(Date)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class Place(Base):
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="RESTRICT")
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.id", ondelete="RESTRICT")
    )
    external_ref: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    tags: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default=text("'{}'::text[]"))
    description: Mapped[str | None] = mapped_column(Text)
    address: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    lon: Mapped[Decimal] = mapped_column(Numeric(9, 6))
    typical_duration_min: Mapped[int] = mapped_column(Integer)
    price_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    price_currency: Mapped[str | None] = mapped_column(CHAR(3))
    price_label: Mapped[str] = mapped_column(Text, server_default=text("'unavailable'"))
    hours_label: Mapped[str] = mapped_column(Text, server_default=text("'unavailable'"))
    hours_checked_on: Mapped[date | None] = mapped_column(Date)
    verification_status: Mapped[str] = mapped_column(Text, server_default=text("'unverified'"))
    step_free: Mapped[bool | None] = mapped_column(Boolean)
    child_friendly: Mapped[bool | None] = mapped_column(Boolean)
    indoor: Mapped[bool | None] = mapped_column(Boolean)
    website_url: Mapped[str | None] = mapped_column(Text)
    booking_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class PlaceOpeningHours(Base):
    __tablename__ = "place_opening_hours"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="CASCADE")
    )
    weekday: Mapped[int] = mapped_column(SmallInteger)
    is_closed: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    open_time: Mapped[time | None] = mapped_column(Time)
    close_time: Mapped[time | None] = mapped_column(Time)
    closes_next_day: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )


class TripPlace(Base):
    __tablename__ = "trip_places"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("places.id", ondelete="RESTRICT")
    )
    relation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
