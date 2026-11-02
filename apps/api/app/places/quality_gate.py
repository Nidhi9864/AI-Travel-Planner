"""Place quality gate (specification §5.6; FR-022, FR-023; IMP-205 step 2).

``check(row, destination)`` parses one ``places.csv`` row and its ``opening_hours.csv`` rows and
returns the place values with the reasons the row is rejected or flagged. Pure: it reads no file
and touches no database, so ``--check`` mode and the loader apply the same rules.

Rejected (the row is not loaded, and a stored place with the same key is deactivated): no
external_ref; no known source, or a source without licence or retrieved date; no or unknown
verification status; coordinates outside the destination bounding box; unknown category or tag;
a negative price, max below min, a price without currency or with label ``unavailable``; duration
outside 15 to 480 minutes; and values the places table would refuse (name, description length,
labels, suitability that is not true, false or empty).

Flagged (the row is loaded): opening hours that do not parse into weekday intervals; the place is
stored with ``hours_label = unavailable`` and no hour rows.
"""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal, InvalidOperation
from typing import Any

from app.places.vocabulary import CATEGORIES, SOURCE_LABELS, TAGS, VERIFICATION_STATUSES

MIN_DURATION_MIN = 15
MAX_DURATION_MIN = 480
NAME_MAX_CHARS = 160
DESCRIPTION_MAX_CHARS = 600
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
HOURS_FILE = "opening_hours.csv"

# (weekday, is_closed, open_time, close_time, closes_next_day), as place_opening_hours stores it.
HoursRow = tuple[int, bool, time | None, time | None, bool]


@dataclass(frozen=True)
class SourceRecord:
    name: str
    source_type: str
    licence: str | None
    attribution_text: str | None
    url: str | None
    retrieved_on: date | None
    notes: str | None


@dataclass(frozen=True)
class DestinationBox:
    min_lat: Decimal
    max_lat: Decimal
    min_lon: Decimal
    max_lon: Decimal

    def contains(self, lat: Decimal, lon: Decimal) -> bool:
        return self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon


@dataclass(frozen=True)
class HoursLine:
    line: int
    cells: Mapping[str, str]


@dataclass(frozen=True)
class PlaceRow:
    """One places.csv row as text, with its source (None when the name is unknown) and hours."""

    line: int
    cells: Mapping[str, str]
    source: SourceRecord | None
    hours: Sequence[HoursLine] = ()


@dataclass
class GateResult:
    values: dict[str, Any]
    hours: list[HoursRow] = field(default_factory=list)
    rejects: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

    @property
    def accepted(self) -> bool:
        return not self.rejects


def _text(cells: Mapping[str, str], column: str) -> str | None:
    value = (cells.get(column) or "").strip()
    return value or None


def _hhmm(value: str) -> time:
    if len(value) != 5 or value[2] != ":":
        raise ValueError(value)
    return time.fromisoformat(value)


def _bool(value: str) -> bool:
    if value.lower() not in ("true", "false"):
        raise ValueError(value)
    return value.lower() == "true"


class _Row:
    """Parses the cells of one row and collects the reject reasons."""

    def __init__(self, cells: Mapping[str, str]) -> None:
        self.cells = cells
        self.rejects: list[str] = []

    def text(self, column: str) -> str | None:
        return _text(self.cells, column)

    def decimal(self, column: str) -> Decimal | None:
        value = self.text(column)
        if value is None:
            return None
        try:
            return Decimal(value)
        except InvalidOperation:
            self.rejects.append(f"{column} is not a number: {value!r}")
            return None

    def integer(self, column: str) -> int | None:
        value = self.text(column)
        if value is None:
            self.rejects.append(f"{column} is missing")
            return None
        try:
            return int(value)
        except ValueError:
            self.rejects.append(f"{column} is not a whole number: {value!r}")
            return None

    def day(self, column: str) -> date | None:
        value = self.text(column)
        if value is None:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            self.rejects.append(f"{column} is not a date (YYYY-MM-DD): {value!r}")
            return None

    def suitability(self, column: str) -> bool | None:
        # Unknown stays NULL; only an explicit "false" is stored as false (FR-019 AC2).
        value = self.text(column)
        if value is None:
            return None
        try:
            return _bool(value)
        except ValueError:
            self.rejects.append(f"{column} must be true, false or empty: {value!r}")
            return None


def _check_provenance(row: PlaceRow, parsed: _Row) -> None:
    if parsed.text("external_ref") is None:
        parsed.rejects.append("external_ref is missing")
    source = row.source
    if source is None:
        name = parsed.text("source_name")
        parsed.rejects.append(
            f"source {name!r} is not in sources.csv" if name else "source_name is missing"
        )
    else:
        if source.licence is None:
            parsed.rejects.append(f"source {source.name!r} has no licence")
        if source.retrieved_on is None:
            parsed.rejects.append(f"source {source.name!r} has no retrieved date")
    status = parsed.text("verification_status")
    if status is None:
        parsed.rejects.append("verification_status is missing")
    elif status not in VERIFICATION_STATUSES:
        parsed.rejects.append(f"verification_status {status!r} is not allowed")


def _check_prices(parsed: _Row, values: dict[str, Any]) -> None:
    price_min, price_max = values["price_min"], values["price_max"]
    currency, label = values["price_currency"], values["price_label"]
    has_price = price_min is not None or price_max is not None
    for column, value in (("price_min", price_min), ("price_max", price_max)):
        if value is not None and value < 0:
            parsed.rejects.append(f"{column} is negative")
    if price_min is not None and price_max is not None and price_max < price_min:
        parsed.rejects.append("price_max is below price_min")
    if has_price and currency is None:
        parsed.rejects.append("a price is given without price_currency")
    if currency is not None and not CURRENCY_PATTERN.fullmatch(currency):
        parsed.rejects.append(f"price_currency {currency!r} is not a three-letter code")
    if label not in SOURCE_LABELS:
        parsed.rejects.append(f"price_label {label!r} is not allowed")
    elif has_price and label == "unavailable":
        parsed.rejects.append("price_label is unavailable but a price is given")
    elif label != "unavailable" and price_min is None:
        parsed.rejects.append(f"price_label {label} needs price_min")


def _parse_hours(lines: Sequence[HoursLine]) -> tuple[list[HoursRow], str | None]:
    """The place's weekly hours, or the first problem that makes them unusable."""
    rows: list[HoursRow] = []
    slots: set[tuple[int, bool, time | None]] = set()
    for hours_line in lines:
        where = f"{HOURS_FILE} line {hours_line.line}"
        cells = hours_line.cells
        try:
            weekday = int(_text(cells, "weekday") or "")
            is_closed = _bool(_text(cells, "is_closed") or "")
            next_day_text = _text(cells, "closes_next_day")
            closes_next_day = _bool(next_day_text) if next_day_text else False
            open_text, close_text = _text(cells, "open_time"), _text(cells, "close_time")
            open_time = _hhmm(open_text) if open_text else None
            close_time = _hhmm(close_text) if close_text else None
        except ValueError:
            return [], f"{where}: a value does not parse"
        if not 1 <= weekday <= 7:
            return [], f"{where}: weekday {weekday} is not 1 to 7"
        if is_closed:
            if open_time or close_time or closes_next_day:
                return [], f"{where}: a closed day has times"
        elif open_time is None or close_time is None:
            return [], f"{where}: open_time and close_time are required"
        elif not closes_next_day and close_time <= open_time:
            return [], f"{where}: close_time is not after open_time"
        slot = (weekday, is_closed, None if is_closed else open_time)
        if slot in slots:
            return [], f"{where}: the weekday has this slot twice"
        slots.add(slot)
        rows.append((weekday, is_closed, open_time, close_time, closes_next_day))
    rows.sort(key=hours_sort_key)
    return rows, None


def hours_sort_key(row: HoursRow) -> tuple[int, bool, time, time, bool]:
    weekday, is_closed, open_time, close_time, next_day = row
    return (weekday, is_closed, open_time or time.min, close_time or time.min, next_day)


def check(row: PlaceRow, destination: DestinationBox) -> GateResult:
    """Apply every §5.6 rule to one row; the result says what to load and why not."""
    parsed = _Row(row.cells)
    _check_provenance(row, parsed)

    tags_text = parsed.text("tags")
    tags = [tag.strip() for tag in tags_text.split(";") if tag.strip()] if tags_text else []
    values: dict[str, Any] = {
        "external_ref": parsed.text("external_ref"),
        "name": parsed.text("name"),
        "category": parsed.text("category"),
        "tags": tags,
        "description": parsed.text("description"),
        "address": parsed.text("address"),
        "lat": parsed.decimal("lat"),
        "lon": parsed.decimal("lon"),
        "typical_duration_min": parsed.integer("typical_duration_min"),
        "price_min": parsed.decimal("price_min"),
        "price_max": parsed.decimal("price_max"),
        "price_currency": parsed.text("price_currency"),
        "price_label": parsed.text("price_label") or "unavailable",
        "hours_label": parsed.text("hours_label") or "unavailable",
        "hours_checked_on": parsed.day("hours_checked_on"),
        "verification_status": parsed.text("verification_status"),
        "step_free": parsed.suitability("step_free"),
        "child_friendly": parsed.suitability("child_friendly"),
        "indoor": parsed.suitability("indoor"),
        "website_url": parsed.text("website_url"),
        "booking_url": parsed.text("booking_url"),
    }

    name = values["name"]
    if name is None:
        parsed.rejects.append("name is missing")
    elif len(name) > NAME_MAX_CHARS:
        parsed.rejects.append(f"name is longer than {NAME_MAX_CHARS} characters")
    description = values["description"]
    if description is not None and len(description) > DESCRIPTION_MAX_CHARS:
        parsed.rejects.append(f"description is longer than {DESCRIPTION_MAX_CHARS} characters")

    lat, lon = values["lat"], values["lon"]
    if lat is None or lon is None:
        if parsed.text("lat") is None or parsed.text("lon") is None:
            parsed.rejects.append("lat and lon are required")
    elif not destination.contains(lat, lon):
        parsed.rejects.append(f"coordinates {lat}, {lon} are outside the destination bounding box")

    category = values["category"]
    if category not in CATEGORIES:
        parsed.rejects.append(f"category {category!r} is not in the vocabulary")
    unknown_tags = [tag for tag in tags if tag not in TAGS]
    if unknown_tags:
        parsed.rejects.append(f"tags not in the vocabulary: {', '.join(unknown_tags)}")

    duration = values["typical_duration_min"]
    if duration is not None and not MIN_DURATION_MIN <= duration <= MAX_DURATION_MIN:
        parsed.rejects.append(
            f"typical_duration_min {duration} is outside {MIN_DURATION_MIN} to {MAX_DURATION_MIN}"
        )

    _check_prices(parsed, values)

    hours_label = values["hours_label"]
    if hours_label not in SOURCE_LABELS:
        parsed.rejects.append(f"hours_label {hours_label!r} is not allowed")
    elif hours_label == "curated" and values["hours_checked_on"] is None:
        parsed.rejects.append("hours_label curated needs hours_checked_on")

    result = GateResult(values=values, rejects=parsed.rejects)
    hours, problem = _parse_hours(row.hours)
    if problem is not None:
        result.flags.append(f"hours not parseable ({problem}); stored as unavailable")
        values["hours_label"] = "unavailable"
    elif not hours:
        # §5.6: a place without opening-hours rows is labelled unavailable.
        values["hours_label"] = "unavailable"
    result.hours = hours
    return result
