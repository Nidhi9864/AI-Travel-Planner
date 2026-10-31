"""Seed command: ``python -m app.places.seed <dir> [<dir> ...]`` (specification §5.6, IMP-107).

Loads one destination per directory (``destination.json``, ``sources.csv``, ``places.csv``,
``opening_hours.csv``) into the four reference tables, of which this command is the only writer.
Each directory is one transaction, written in the order data_sources, destinations, places,
opening hours. Rows are matched by their natural keys (source name, destination slug, and
(source, external_ref) for places); a row is inserted, updated when a value differs, or left
untouched, so a second run with unchanged files changes nothing. A place's opening hours are
replaced as a set when they differ; a place without rows gets ``hours_label = unavailable``.
Places of the same source and destination that are missing from the file are deactivated, never
deleted.

Every directory is read before anything is written. A file-format error, a ``destination.json``
with ``is_sample: true`` outside ``APP_ENV`` local or test, or a row the database rejects exits 1
with a message naming the file and line. IMP-205 replaces the loading core with the provenance
import and quality gate behind the same command.
"""

import argparse
import asyncio
import csv
import json
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import date, time
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, TypeVar
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import DataSource, Destination, Place, PlaceOpeningHours
from app.db.session import get_engine, transaction

DESTINATION_FILE = "destination.json"
SOURCES_FILE = "sources.csv"
PLACES_FILE = "places.csv"
HOURS_FILE = "opening_hours.csv"

SOURCE_COLUMNS = (
    "name",
    "source_type",
    "licence",
    "attribution_text",
    "url",
    "retrieved_on",
    "notes",
)
PLACE_COLUMNS = (
    "external_ref",
    "source_name",
    "name",
    "category",
    "tags",
    "description",
    "address",
    "lat",
    "lon",
    "typical_duration_min",
    "price_min",
    "price_max",
    "price_currency",
    "price_label",
    "hours_label",
    "hours_checked_on",
    "verification_status",
    "step_free",
    "child_friendly",
    "indoor",
    "website_url",
    "booking_url",
)
HOURS_COLUMNS = (
    "external_ref",
    "weekday",
    "is_closed",
    "open_time",
    "close_time",
    "closes_next_day",
)
SAMPLE_ALLOWED_ENVS = ("local", "test")

T = TypeVar("T")
HoursRow = tuple[int, bool, time | None, time | None, bool]


class SeedFormatError(Exception):
    """A file cannot be read as the §5.6 format; the message names the file and line."""


class SeedRefusedError(Exception):
    """The data may not be loaded in this environment (SAMPLE data outside local or test)."""


@dataclass
class Fixture:
    directory: Path
    destination: dict[str, Any]
    sources: list[dict[str, Any]]
    places: list[dict[str, Any]]  # each carries "source_name"; the loader resolves source_id
    hours: dict[str, list[HoursRow]]  # by external_ref, sorted

    @property
    def label(self) -> str:
        return str(self.destination["slug"])


@dataclass
class Counts:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0

    def __str__(self) -> str:
        return f"inserted {self.inserted}, updated {self.updated}, unchanged {self.unchanged}"


@dataclass
class SeedReport:
    slug: str
    read: dict[str, int]
    data_sources: Counts = field(default_factory=Counts)
    destinations: Counts = field(default_factory=Counts)
    places: Counts = field(default_factory=Counts)
    deactivated: int = 0
    hours_replaced: int = 0
    hours_unchanged: int = 0

    def lines(self) -> list[str]:
        prefix = f"seed {self.slug}:"
        read = self.read
        return [
            f"{prefix} read {read['destinations']} destination, {read['data_sources']} source(s), "
            f"{read['places']} places, {read['opening_hours']} opening-hours rows",
            f"{prefix} data_sources {self.data_sources}",
            f"{prefix} destinations {self.destinations}",
            f"{prefix} places {self.places}, deactivated {self.deactivated}",
            f"{prefix} opening hours replaced for {self.hours_replaced} places, "
            f"unchanged for {self.hours_unchanged}",
        ]


# ---------- Reading the files ----------


class _Cell:
    """Parses one CSV cell; errors name the file, line and column."""

    def __init__(self, file: str, line: int, row: dict[str, str]) -> None:
        self.file, self.line, self.row = file, line, row

    def error(self, column: str, problem: str) -> SeedFormatError:
        return SeedFormatError(f"{self.file} line {self.line}: {column} {problem}")

    def text(self, column: str, *, required: bool = False) -> str | None:
        value = (self.row.get(column) or "").strip()
        if not value:
            if required:
                raise self.error(column, "is required")
            return None
        return value

    def _parse(self, column: str, parse: Callable[[str], T], kind: str, required: bool) -> T | None:
        value = self.text(column, required=required)
        if value is None:
            return None
        try:
            return parse(value)
        except (ValueError, InvalidOperation) as exc:
            raise self.error(column, f"is not {kind}: {value!r}") from exc

    def required(self, column: str, parse: Callable[[str], T], kind: str) -> T:
        value = self._parse(column, parse, kind, True)
        if value is None:  # unreachable: _parse raises for an empty required cell
            raise self.error(column, "is required")
        return value

    def decimal(self, column: str, *, required: bool = False) -> Decimal | None:
        return self._parse(column, Decimal, "a number", required)

    def integer(self, column: str, *, required: bool = False) -> int | None:
        return self._parse(column, int, "a whole number", required)

    def day(self, column: str) -> date | None:
        return self._parse(column, date.fromisoformat, "a date (YYYY-MM-DD)", False)

    def clock(self, column: str) -> time | None:
        return self._parse(column, _hhmm, "a time (HH:MM)", False)

    def boolean(self, column: str, *, required: bool = False) -> bool | None:
        return self._parse(column, _bool, "true or false", required)


def _hhmm(value: str) -> time:
    if len(value) != 5 or value[2] != ":":
        raise ValueError(value)
    return time.fromisoformat(value)


def _bool(value: str) -> bool:
    if value.lower() not in ("true", "false"):
        raise ValueError(value)
    return value.lower() == "true"


def _rows(directory: Path, name: str, columns: Iterable[str]) -> list[tuple[int, dict[str, str]]]:
    path = directory / name
    if not path.is_file():
        raise SeedFormatError(f"{name} is missing in {directory}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing = [column for column in columns if column not in header]
        unknown = [column for column in header if column not in columns]
        if missing or unknown:
            raise SeedFormatError(
                f"{name} line 1: missing columns {missing}, unknown columns {unknown}"
            )
        return [(index, row) for index, row in enumerate(reader, start=2)]


def read_destination(directory: Path) -> dict[str, Any]:
    path = directory / DESTINATION_FILE
    if not path.is_file():
        raise SeedFormatError(f"{DESTINATION_FILE} is missing in {directory}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        center, bbox = data["center"], data["bbox"]
        destination = {
            "slug": str(data["slug"]),
            "name": str(data["name"]),
            "region": data.get("region"),
            "country_code": str(data["country_code"]),
            "timezone": str(data["timezone"]),
            "currency": str(data["currency"]),
            "center_lat": Decimal(str(center["lat"])),
            "center_lon": Decimal(str(center["lon"])),
            "bbox_min_lat": Decimal(str(bbox["min_lat"])),
            "bbox_max_lat": Decimal(str(bbox["max_lat"])),
            "bbox_min_lon": Decimal(str(bbox["min_lon"])),
            "bbox_max_lon": Decimal(str(bbox["max_lon"])),
            "is_sample": bool(data.get("is_sample", False)),
        }
    except json.JSONDecodeError as exc:
        raise SeedFormatError(f"{DESTINATION_FILE} line {exc.lineno}: not valid JSON") from exc
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise SeedFormatError(f"{DESTINATION_FILE}: missing or invalid field {exc}") from exc
    try:
        ZoneInfo(destination["timezone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise SeedFormatError(
            f"{DESTINATION_FILE}: timezone {destination['timezone']!r} is not an IANA name"
        ) from exc
    return destination


def read_fixture(directory: Path) -> Fixture:
    """Read and type-check one destination directory; nothing is written."""
    destination = read_destination(directory)

    sources = []
    for line, row in _rows(directory, SOURCES_FILE, SOURCE_COLUMNS):
        cell = _Cell(SOURCES_FILE, line, row)
        sources.append(
            {
                "name": cell.text("name", required=True),
                "source_type": cell.text("source_type", required=True),
                "licence": cell.text("licence", required=True),
                "attribution_text": cell.text("attribution_text"),
                "url": cell.text("url"),
                "retrieved_on": cell.day("retrieved_on"),
                "notes": cell.text("notes"),
            }
        )
    source_names = {source["name"] for source in sources}

    places = []
    seen_refs: set[str] = set()
    for line, row in _rows(directory, PLACES_FILE, PLACE_COLUMNS):
        cell = _Cell(PLACES_FILE, line, row)
        external_ref = cell.text("external_ref", required=True)
        source_name = cell.text("source_name", required=True)
        if source_name not in source_names:
            raise cell.error("source_name", f"{source_name!r} is not in {SOURCES_FILE}")
        if external_ref in seen_refs:
            raise cell.error("external_ref", f"{external_ref!r} appears twice")
        seen_refs.add(str(external_ref))
        tags = cell.text("tags")
        places.append(
            {
                "source_name": source_name,
                "external_ref": external_ref,
                "name": cell.text("name", required=True),
                "category": cell.text("category", required=True),
                "tags": [tag.strip() for tag in tags.split(";") if tag.strip()] if tags else [],
                "description": cell.text("description"),
                "address": cell.text("address"),
                "lat": cell.required("lat", Decimal, "a number"),
                "lon": cell.required("lon", Decimal, "a number"),
                "typical_duration_min": cell.integer("typical_duration_min", required=True),
                "price_min": cell.decimal("price_min"),
                "price_max": cell.decimal("price_max"),
                "price_currency": cell.text("price_currency"),
                "price_label": cell.text("price_label") or "unavailable",
                "hours_label": cell.text("hours_label") or "unavailable",
                "hours_checked_on": cell.day("hours_checked_on"),
                "verification_status": cell.text("verification_status", required=True),
                "step_free": cell.boolean("step_free"),
                "child_friendly": cell.boolean("child_friendly"),
                "indoor": cell.boolean("indoor"),
                "website_url": cell.text("website_url"),
                "booking_url": cell.text("booking_url"),
            }
        )

    hours: dict[str, list[HoursRow]] = {}
    for line, row in _rows(directory, HOURS_FILE, HOURS_COLUMNS):
        cell = _Cell(HOURS_FILE, line, row)
        external_ref = str(cell.text("external_ref", required=True))
        if external_ref not in seen_refs:
            raise cell.error("external_ref", f"{external_ref!r} is not in {PLACES_FILE}")
        weekday = cell.required("weekday", int, "a whole number")
        is_closed = cell.required("is_closed", _bool, "true or false")
        closes_next_day = cell.boolean("closes_next_day") or False
        hours.setdefault(external_ref, []).append(
            (weekday, is_closed, cell.clock("open_time"), cell.clock("close_time"), closes_next_day)
        )
    for rows in hours.values():
        rows.sort(key=_hours_key)

    for place in places:
        # §5.6: a place without opening-hours rows is labelled unavailable.
        if place["external_ref"] not in hours:
            place["hours_label"] = "unavailable"

    return Fixture(directory, destination, sources, places, hours)


def _hours_key(row: HoursRow) -> tuple[int, bool, time, time, bool]:
    weekday, is_closed, open_time, close_time, next_day = row
    return (weekday, is_closed, open_time or time.min, close_time or time.min, next_day)


def check_allowed(fixture: Fixture, app_env: str) -> None:
    if fixture.destination["is_sample"] and app_env not in SAMPLE_ALLOWED_ENVS:
        raise SeedRefusedError(
            f"{fixture.label}: SAMPLE data (is_sample true) is loaded only when APP_ENV is "
            f"local or test, not {app_env}"
        )


# ---------- Writing ----------


def _differs(row: Any, values: dict[str, Any]) -> bool:
    return any(getattr(row, column) != value for column, value in values.items())


def _apply(row: Any, values: dict[str, Any]) -> None:
    for column, value in values.items():
        setattr(row, column, value)


async def load_fixture(session: AsyncSession, fixture: Fixture) -> SeedReport:
    """Write one directory inside the caller's transaction and report what changed."""
    report = SeedReport(
        slug=fixture.label,
        read={
            "destinations": 1,
            "data_sources": len(fixture.sources),
            "places": len(fixture.places),
            "opening_hours": sum(len(rows) for rows in fixture.hours.values()),
        },
    )

    source_ids = {}
    for values in fixture.sources:
        source = await session.scalar(select(DataSource).where(DataSource.name == values["name"]))
        if source is None:
            source = DataSource(**values)
            session.add(source)
            report.data_sources.inserted += 1
        elif _differs(source, values):
            _apply(source, values)
            report.data_sources.updated += 1
        else:
            report.data_sources.unchanged += 1
        await session.flush()
        source_ids[values["name"]] = source.id

    values = fixture.destination
    destination = await session.scalar(
        select(Destination).where(Destination.slug == values["slug"])
    )
    if destination is None:
        destination = Destination(**values)
        session.add(destination)
        report.destinations.inserted += 1
    elif _differs(destination, values):
        _apply(destination, values)
        report.destinations.updated += 1
    else:
        report.destinations.unchanged += 1
    await session.flush()

    existing = {
        (place.source_id, place.external_ref): place
        for place in await session.scalars(
            select(Place).where(
                Place.destination_id == destination.id,
                Place.source_id.in_(list(source_ids.values())),
            )
        )
    }
    loaded: dict[str, Place] = {}
    for item in fixture.places:
        values = {key: value for key, value in item.items() if key != "source_name"}
        values |= {
            "source_id": source_ids[item["source_name"]],
            "destination_id": destination.id,
            "is_active": True,
        }
        place = existing.pop((values["source_id"], values["external_ref"]), None)
        if place is None:
            place = Place(**values)
            session.add(place)
            report.places.inserted += 1
        elif _differs(place, values):
            _apply(place, values)
            report.places.updated += 1
        else:
            report.places.unchanged += 1
        loaded[values["external_ref"]] = place
    for missing in existing.values():
        if missing.is_active:
            missing.is_active = False
            report.deactivated += 1
    await session.flush()

    for external_ref, place in loaded.items():
        wanted = fixture.hours.get(external_ref, [])
        stored = list(
            await session.scalars(
                select(PlaceOpeningHours).where(PlaceOpeningHours.place_id == place.id)
            )
        )
        current = sorted(
            (
                (row.weekday, row.is_closed, row.open_time, row.close_time, row.closes_next_day)
                for row in stored
            ),
            key=_hours_key,
        )
        if current == wanted:
            report.hours_unchanged += 1
            continue
        for row in stored:
            await session.delete(row)
        await session.flush()
        for weekday, is_closed, open_time, close_time, next_day in wanted:
            session.add(
                PlaceOpeningHours(
                    place_id=place.id,
                    weekday=weekday,
                    is_closed=is_closed,
                    open_time=open_time,
                    close_time=close_time,
                    closes_next_day=next_day,
                )
            )
        report.hours_replaced += 1
    await session.flush()
    return report


async def _load_all(fixtures: list[Fixture]) -> list[SeedReport]:
    reports = []
    try:
        for fixture in fixtures:
            async with transaction() as session:
                reports.append(await load_fixture(session, fixture))
    finally:
        await get_engine().dispose()
    return reports


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.places.seed", description="Load destination directories (§5.6)."
    )
    parser.add_argument("directories", nargs="+", type=Path)
    args = parser.parse_args(argv)
    app_env = get_settings().app_env

    try:
        fixtures = [read_fixture(directory) for directory in args.directories]
        for fixture in fixtures:
            check_allowed(fixture, app_env)
    except (SeedFormatError, SeedRefusedError) as exc:
        print(f"seed: {exc}", file=sys.stderr)
        return 1

    try:
        reports = asyncio.run(_load_all(fixtures))
    except (IntegrityError, DataError) as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        print(
            f"seed: the database rejected a row ({constraint or type(exc.orig).__name__}); "
            "nothing was written for that directory",
            file=sys.stderr,
        )
        return 1

    for report in reports:
        print("\n".join(report.lines()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
