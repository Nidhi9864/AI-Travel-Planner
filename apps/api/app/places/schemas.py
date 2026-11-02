"""Place and destination response shapes (specification §6.5 Destination, PlaceSummary; §6.6.3).

Categories and tags are the enums of places/vocabulary.py, so the OpenAPI contract lists them.
Suitability is true, false or null (unknown, FR-019 AC2); prices are IMD-05 money strings.
"""

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models import Destination as DestinationRow
from app.db.models import Place as PlaceRow
from app.places.vocabulary import Category, SourceLabel, Tag, VerificationStatus
from app.schemas.ai import HHMM
from app.schemas.common import MoneyAmount

COORDINATE_PLACES = 6


def _coordinate(value: Decimal) -> float:
    return round(float(value), COORDINATE_PLACES)


class Point(BaseModel):
    lat: float
    lon: float


class BoundingBox(BaseModel):
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class Destination(BaseModel):
    id: UUID
    slug: str
    name: str
    region: str | None
    country_code: str
    timezone: str = Field(description="IANA time zone; trip dates and times are local to it")
    currency: str
    is_sample: bool = Field(description="True for the SAMPLE fixture; the web shows a banner")
    center: Point
    bbox: BoundingBox

    @classmethod
    def from_row(cls, row: DestinationRow) -> "Destination":
        return cls(
            id=row.id,
            slug=row.slug,
            name=row.name,
            region=row.region,
            country_code=row.country_code,
            timezone=row.timezone,
            currency=row.currency,
            is_sample=row.is_sample,
            center=Point(lat=_coordinate(row.center_lat), lon=_coordinate(row.center_lon)),
            bbox=BoundingBox(
                min_lat=_coordinate(row.bbox_min_lat),
                max_lat=_coordinate(row.bbox_max_lat),
                min_lon=_coordinate(row.bbox_min_lon),
                max_lon=_coordinate(row.bbox_max_lon),
            ),
        )


class PlacePrice(BaseModel):
    min: MoneyAmount
    max: MoneyAmount | None
    currency: str
    label: SourceLabel


class Suitability(BaseModel):
    """Each flag is true, false or null; null means unknown, never "not suitable"."""

    step_free: bool | None
    child_friendly: bool | None
    indoor: bool | None


class PlaceSummary(BaseModel):
    id: UUID
    name: str
    category: Category
    tags: list[Tag]
    lat: float
    lon: float
    typical_duration_min: int
    price: PlacePrice | None = Field(description="Null when the place has no price")
    price_label: SourceLabel
    hours_label: SourceLabel
    verification_status: VerificationStatus
    suitability: Suitability

    @classmethod
    def from_row(cls, row: PlaceRow) -> "PlaceSummary":
        price = None
        if row.price_min is not None and row.price_currency is not None:
            price = PlacePrice(
                min=row.price_min,
                max=row.price_max,
                currency=row.price_currency,
                label=SourceLabel(row.price_label),
            )
        return cls(
            id=row.id,
            name=row.name,
            category=Category(row.category),
            tags=[Tag(tag) for tag in row.tags],
            lat=_coordinate(row.lat),
            lon=_coordinate(row.lon),
            typical_duration_min=row.typical_duration_min,
            price=price,
            price_label=SourceLabel(row.price_label),
            hours_label=SourceLabel(row.hours_label),
            verification_status=VerificationStatus(row.verification_status),
            suitability=Suitability(
                step_free=row.step_free, child_friendly=row.child_friendly, indoor=row.indoor
            ),
        )


class OpeningHours(BaseModel):
    weekday: int = Field(ge=1, le=7, description="1 is Monday")
    is_closed: bool
    open_time: HHMM | None
    close_time: HHMM | None
    closes_next_day: bool


class PlaceSource(BaseModel):
    name: str
    source_type: Literal["curated_manual", "osm_import", "official_site", "estimate", "other"]
    licence: str
    attribution_text: str | None
    url: str | None
    retrieved_on: date | None


class PlaceOut(PlaceSummary):
    """API-17 detail. Missing hours or prices are never filled in (FR-018 AC2)."""

    description: str | None
    address: str | None
    website_url: str | None
    booking_url: str | None
    hours: list[OpeningHours]
    hours_checked_on: date | None
    source: PlaceSource
    saved: bool | None = Field(None, description="Set only when trip_id is given")
    must_visit: bool | None = Field(None, description="Set only when trip_id is given")
