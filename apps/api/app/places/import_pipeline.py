"""Provenance-preserving place import (specification §5.6; FR-022, FR-023; IMP-205 step 3).

``run(directories, check=, strict=)`` is the core of ``python -m app.places.seed``. Per destination
directory it reads the four files, applies the quality gate to every place row, writes
``<dir>/quality_report.md`` and, unless ``check`` is set, loads the result in one transaction:

- data_sources upserted by name, the destination by slug, places by (source_id, external_ref);
- a place's opening hours replaced as a set when they differ;
- places of the same destination and sources that are missing from the file or rejected by the
  gate are deactivated (``is_active = false``), never deleted.

A second run with unchanged files changes nothing. The report holds only what the gate decided
(rows read, loaded, rejected with reasons, flagged, usable count against ``min_usable_places``),
so ``--check`` and a load write the same file. A shortfall is stated in the report; with
``strict`` it also exits 1 before anything is written. A file that cannot be read as the §5.6
format, SAMPLE data outside APP_ENV local or test (when loading), or a row the database refuses
exits 1 with a message naming the file.
"""

import asyncio
import csv
import json
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import select
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import DataSource, Destination, Place, PlaceOpeningHours
from app.db.session import get_engine, transaction
from app.places import quality_gate
from app.places.quality_gate import (
    DestinationBox,
    GateResult,
    HoursLine,
    HoursRow,
    PlaceRow,
    SourceRecord,
)

DESTINATION_FILE = "destination.json"
SOURCES_FILE = "sources.csv"
PLACES_FILE = "places.csv"
HOURS_FILE = "opening_hours.csv"
REPORT_FILE = "quality_report.md"
MIN_USABLE_KEY = "min_usable_places"

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


class SeedFormatError(Exception):
    """A file cannot be read as the §5.6 format; the message names the file and line."""


class SeedRefusedError(Exception):
    """The data may not be loaded in this environment (SAMPLE data outside local or test)."""


@dataclass(frozen=True)
class CheckedRow:
    line: int
    source_name: str | None
    result: GateResult

    @property
    def external_ref(self) -> str | None:
        ref: str | None = self.result.values["external_ref"]
        return ref


@dataclass
class Prepared:
    """One destination directory, read and passed through the gate; nothing is written yet."""

    directory: Path
    destination: dict[str, Any]
    min_usable_places: int | None
    sources: list[SourceRecord]
    rows: list[CheckedRow]
    hours_rows_read: int

    @property
    def label(self) -> str:
        return str(self.destination["slug"])

    @property
    def accepted(self) -> list[CheckedRow]:
        return [row for row in self.rows if row.result.accepted]

    @property
    def rejected(self) -> list[CheckedRow]:
        return [row for row in self.rows if not row.result.accepted]

    @property
    def flagged(self) -> list[CheckedRow]:
        return [row for row in self.accepted if row.result.flags]

    @property
    def shortfall(self) -> int:
        """Usable places missing against the minimum (0 when met or no minimum is set)."""
        if self.min_usable_places is None:
            return 0
        return max(0, self.min_usable_places - len(self.accepted))


@dataclass
class Counts:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0

    def __str__(self) -> str:
        return f"inserted {self.inserted}, updated {self.updated}, unchanged {self.unchanged}"


@dataclass
class LoadReport:
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
        return [
            f"{prefix} data_sources {self.data_sources}",
            f"{prefix} destinations {self.destinations}",
            f"{prefix} places {self.places}, deactivated {self.deactivated}",
            f"{prefix} opening hours replaced for {self.hours_replaced} places, "
            f"unchanged for {self.hours_unchanged}",
        ]


# ---------- Reading the files ----------


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


def _cell(row: dict[str, str], column: str) -> str | None:
    value = (row.get(column) or "").strip()
    return value or None


def read_destination(directory: Path) -> tuple[dict[str, Any], int | None]:
    """The destinations row of destination.json and its min_usable_places (None when absent)."""
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
        minimum = data.get(MIN_USABLE_KEY)
    except json.JSONDecodeError as exc:
        raise SeedFormatError(f"{DESTINATION_FILE} line {exc.lineno}: not valid JSON") from exc
    except (KeyError, TypeError, InvalidOperation) as exc:
        raise SeedFormatError(f"{DESTINATION_FILE}: missing or invalid field {exc}") from exc
    if minimum is not None and (
        isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 0
    ):
        raise SeedFormatError(f"{DESTINATION_FILE}: {MIN_USABLE_KEY} must be a whole number >= 0")
    try:
        ZoneInfo(destination["timezone"])
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise SeedFormatError(
            f"{DESTINATION_FILE}: timezone {destination['timezone']!r} is not an IANA name"
        ) from exc
    return destination, minimum


def _read_sources(directory: Path) -> list[SourceRecord]:
    sources = []
    for line, row in _rows(directory, SOURCES_FILE, SOURCE_COLUMNS):
        name, source_type = _cell(row, "name"), _cell(row, "source_type")
        if name is None or source_type is None:
            raise SeedFormatError(f"{SOURCES_FILE} line {line}: name and source_type are required")
        retrieved = _cell(row, "retrieved_on")
        try:
            retrieved_on = date.fromisoformat(retrieved) if retrieved else None
        except ValueError as exc:
            raise SeedFormatError(
                f"{SOURCES_FILE} line {line}: retrieved_on is not a date (YYYY-MM-DD)"
            ) from exc
        # A missing licence or retrieved date is not a format error: the gate rejects the places
        # that cite the source and lists them in the report.
        sources.append(
            SourceRecord(
                name=name,
                source_type=source_type,
                licence=_cell(row, "licence"),
                attribution_text=_cell(row, "attribution_text"),
                url=_cell(row, "url"),
                retrieved_on=retrieved_on,
                notes=_cell(row, "notes"),
            )
        )
    return sources


def prepare(directory: Path) -> Prepared:
    """Read one destination directory and apply the quality gate; nothing is written."""
    destination, minimum = read_destination(directory)
    box = DestinationBox(
        min_lat=destination["bbox_min_lat"],
        max_lat=destination["bbox_max_lat"],
        min_lon=destination["bbox_min_lon"],
        max_lon=destination["bbox_max_lon"],
    )
    sources = _read_sources(directory)
    by_name = {source.name: source for source in sources}

    place_rows = _rows(directory, PLACES_FILE, PLACE_COLUMNS)
    refs = {_cell(row, "external_ref") for _, row in place_rows} - {None}
    hours: dict[str, list[HoursLine]] = {}
    hours_rows = _rows(directory, HOURS_FILE, HOURS_COLUMNS)
    for line, row in hours_rows:
        ref = _cell(row, "external_ref")
        if ref is None or ref not in refs:
            raise SeedFormatError(
                f"{HOURS_FILE} line {line}: external_ref {ref!r} is not in {PLACES_FILE}"
            )
        hours.setdefault(ref, []).append(HoursLine(line=line, cells=row))

    checked = []
    first_line: dict[str, int] = {}
    for line, row in place_rows:
        ref = _cell(row, "external_ref")
        source_name = _cell(row, "source_name")
        place = PlaceRow(
            line=line,
            cells=row,
            source=by_name.get(source_name) if source_name else None,
            hours=hours.get(ref, []) if ref else [],
        )
        result = quality_gate.check(place, box)
        if ref is not None:
            if ref in first_line:
                result.rejects.append(
                    f"external_ref appears twice (first on line {first_line[ref]})"
                )
            else:
                first_line[ref] = line
        checked.append(CheckedRow(line=line, source_name=source_name, result=result))

    return Prepared(
        directory=directory,
        destination=destination,
        min_usable_places=minimum,
        sources=sources,
        rows=checked,
        hours_rows_read=len(hours_rows),
    )


def check_allowed(prepared: Prepared, app_env: str) -> None:
    if prepared.destination["is_sample"] and app_env not in SAMPLE_ALLOWED_ENVS:
        raise SeedRefusedError(
            f"{prepared.label}: SAMPLE data (is_sample true) is loaded only when APP_ENV is "
            f"local or test, not {app_env}"
        )


# ---------- The quality report ----------


def _md(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _row_table(rows: Sequence[CheckedRow], reasons: str) -> list[str]:
    if not rows:
        return ["None."]
    lines = [f"| Line | external_ref | Name | {reasons} |", "| --- | --- | --- | --- |"]
    for row in rows:
        values = row.result.values
        problems = row.result.rejects if reasons == "Reasons" else row.result.flags
        lines.append(
            f"| {row.line} | {_md(values['external_ref'] or '')} | {_md(values['name'] or '')} "
            f"| {_md('; '.join(problems))} |"
        )
    return lines


def render_report(prepared: Prepared) -> str:
    """quality_report.md for one directory; deterministic, so an unchanged import keeps it."""
    usable = len(prepared.accepted)
    minimum = prepared.min_usable_places
    if minimum is None:
        verdict = f"No minimum is set ({MIN_USABLE_KEY} is absent from {DESTINATION_FILE})."
    elif prepared.shortfall:
        verdict = (
            f"Shortfall: {usable} usable places, {prepared.shortfall} below the minimum of "
            f"{minimum}."
        )
    else:
        verdict = f"Minimum met: {usable} usable places against a minimum of {minimum}."
    categories = Counter(str(row.result.values["category"]) for row in prepared.accepted)
    destination = prepared.destination
    lines = [
        f"# Quality report: {destination['name']} (`{prepared.label}`)",
        "",
        "Written by `python -m app.places.seed` (specification §5.6) from the files in this "
        "directory. Run the seed again to refresh it; do not edit it by hand.",
        "",
        "| Measure | Count |",
        "| --- | --- |",
        f"| Place rows read (`{PLACES_FILE}`) | {len(prepared.rows)} |",
        f"| Opening-hours rows read (`{HOURS_FILE}`) | {prepared.hours_rows_read} |",
        f"| Sources read (`{SOURCES_FILE}`) | {len(prepared.sources)} |",
        f"| Loaded (passed the gate) | {usable} |",
        f"| Rejected | {len(prepared.rejected)} |",
        f"| Flagged (loaded with hours unavailable) | {len(prepared.flagged)} |",
        f"| Usable places | {usable} |",
        f"| Minimum usable places (`{MIN_USABLE_KEY}`) | "
        f"{minimum if minimum is not None else 'not set'} |",
        "",
        verdict,
        "",
        "## Usable places by category",
        "",
    ]
    if categories:
        lines += ["| Category | Places |", "| --- | --- |"]
        lines += [f"| {name} | {count} |" for name, count in sorted(categories.items())]
    else:
        lines.append("None.")
    lines += ["", "## Rejected rows", "", *_row_table(prepared.rejected, "Reasons")]
    lines += ["", "## Flagged rows", "", *_row_table(prepared.flagged, "Flags"), ""]
    return "\n".join(lines)


def write_report(prepared: Prepared) -> Path:
    path = prepared.directory / REPORT_FILE
    path.write_text(render_report(prepared), encoding="utf-8")
    return path


def summary_lines(prepared: Prepared) -> list[str]:
    prefix = f"seed {prepared.label}:"
    lines = [
        f"{prefix} read {len(prepared.rows)} places, {prepared.hours_rows_read} opening-hours "
        f"rows, {len(prepared.sources)} source(s)",
        f"{prefix} gate loaded {len(prepared.accepted)}, rejected {len(prepared.rejected)}, "
        f"flagged {len(prepared.flagged)}",
    ]
    for row in prepared.rejected:
        lines.append(f"{prefix} rejected line {row.line}: {'; '.join(row.result.rejects)}")
    for row in prepared.flagged:
        lines.append(f"{prefix} flagged line {row.line}: {'; '.join(row.result.flags)}")
    if prepared.shortfall:
        lines.append(
            f"{prefix} shortfall: {len(prepared.accepted)} usable places, minimum "
            f"{prepared.min_usable_places}"
        )
    return lines


# ---------- Writing ----------


def _differs(row: Any, values: dict[str, Any]) -> bool:
    return any(getattr(row, column) != value for column, value in values.items())


def _apply(row: Any, values: dict[str, Any]) -> None:
    for column, value in values.items():
        setattr(row, column, value)


async def _upsert_sources(
    session: AsyncSession, prepared: Prepared, report: LoadReport
) -> dict[str, Any]:
    source_ids = {}
    for source in prepared.sources:
        values = {
            "name": source.name,
            "source_type": source.source_type,
            "licence": source.licence,
            "attribution_text": source.attribution_text,
            "url": source.url,
            "retrieved_on": source.retrieved_on,
            "notes": source.notes,
        }
        row = await session.scalar(select(DataSource).where(DataSource.name == source.name))
        if source.licence is None:
            # Not storable (licence is required); its places were rejected by the gate. A row
            # stored earlier stays as it is, so its places can be deactivated below.
            if row is not None:
                source_ids[source.name] = row.id
            continue
        if row is None:
            row = DataSource(**values)
            session.add(row)
            report.data_sources.inserted += 1
        elif _differs(row, values):
            _apply(row, values)
            report.data_sources.updated += 1
        else:
            report.data_sources.unchanged += 1
        await session.flush()
        source_ids[source.name] = row.id
    return source_ids


async def _replace_hours(
    session: AsyncSession, place: Place, wanted: list[HoursRow], report: LoadReport
) -> None:
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
        key=quality_gate.hours_sort_key,
    )
    if current == wanted:
        report.hours_unchanged += 1
        return
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


async def load(session: AsyncSession, prepared: Prepared) -> LoadReport:
    """Write one prepared directory inside the caller's transaction and report what changed."""
    report = LoadReport(
        slug=prepared.label,
        read={
            "destinations": 1,
            "data_sources": len(prepared.sources),
            "places": len(prepared.rows),
            "opening_hours": prepared.hours_rows_read,
        },
    )
    source_ids = await _upsert_sources(session, prepared, report)

    values = prepared.destination
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
    loaded: list[tuple[Place, list[HoursRow]]] = []
    for row in prepared.accepted:
        place_values = dict(row.result.values)
        place_values |= {
            "source_id": source_ids[str(row.source_name)],
            "destination_id": destination.id,
            "is_active": True,
        }
        place = existing.pop((place_values["source_id"], place_values["external_ref"]), None)
        if place is None:
            place = Place(**place_values)
            session.add(place)
            report.places.inserted += 1
        elif _differs(place, place_values):
            _apply(place, place_values)
            report.places.updated += 1
        else:
            report.places.unchanged += 1
        loaded.append((place, row.result.hours))
    # Missing from the file or rejected by the gate: deactivated, never deleted (§5.6).
    for missing in existing.values():
        if missing.is_active:
            missing.is_active = False
            report.deactivated += 1
    await session.flush()

    for place, wanted in loaded:
        await _replace_hours(session, place, wanted, report)
    await session.flush()
    return report


async def _load_all(prepared: list[Prepared]) -> list[LoadReport]:
    reports = []
    try:
        for item in prepared:
            async with transaction() as session:
                reports.append(await load(session, item))
    finally:
        await get_engine().dispose()
    return reports


def run(directories: Sequence[Path], *, check: bool = False, strict: bool = False) -> int:
    """Import every directory (or only check it); returns the process exit code."""
    try:
        prepared = [prepare(directory) for directory in directories]
        if not check:
            app_env = get_settings().app_env
            for item in prepared:
                check_allowed(item, app_env)
    except (SeedFormatError, SeedRefusedError) as exc:
        print(f"seed: {exc}", file=sys.stderr)
        return 1

    for item in prepared:
        write_report(item)
        print("\n".join(summary_lines(item)))

    short = [item for item in prepared if item.shortfall]
    if strict and short:
        names = ", ".join(item.label for item in short)
        print(f"seed: --strict: usable places below the minimum for {names}", file=sys.stderr)
        return 1
    if check:
        print("seed: --check: nothing was written to the database")
        return 0

    try:
        reports = asyncio.run(_load_all(prepared))
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
