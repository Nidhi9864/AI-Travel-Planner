"""Seed command, import pipeline and the Sampleton SAMPLE fixture (§5.6, IMD-09; IMP-107, IMP-205:
TC-101, TC-108, TC-109, TC-110, TC-112, TC-113).

Database tests run in the rolled-back session of tests/fixtures/db.py, so they hold whether or
not the test database was already seeded. Format and environment refusals and --check runs happen
before any database access; --check runs work on copies in tmp_path, so the committed report is
never rewritten by a test.
"""

import shutil
from collections import Counter
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import reset
from app.db.models import DataSource, Destination, Place, PlaceOpeningHours
from app.places import import_pipeline, seed, vocabulary

REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLETON = REPO_ROOT / "data" / "fixtures" / "sampleton"
SAMPLE_SOURCE = "SAMPLE fixture (synthetic)"


async def table_counts(session: AsyncSession) -> dict[str, int]:
    counts = {}
    for model in (Destination, DataSource, Place, PlaceOpeningHours):
        counts[model.__tablename__] = int(
            await session.scalar(select(func.count()).select_from(model)) or 0
        )
    return counts


async def sampleton_snapshot(session: AsyncSession) -> list[Any]:
    """Every Sampleton row, ids and updated_at included, in a stable order."""
    destination = await session.scalar(select(Destination).where(Destination.slug == "sampleton"))
    assert destination is not None
    places = list(
        await session.scalars(
            select(Place).where(Place.destination_id == destination.id).order_by(Place.external_ref)
        )
    )
    hours = list(
        await session.scalars(
            select(PlaceOpeningHours)
            .where(PlaceOpeningHours.place_id.in_([place.id for place in places]))
            .order_by(PlaceOpeningHours.place_id, PlaceOpeningHours.weekday)
        )
    )

    def row(obj: Any) -> tuple[Any, ...]:
        return tuple(getattr(obj, c.key) for c in obj.__table__.columns)

    return [row(destination), *(row(p) for p in places), *(row(h) for h in hours)]


async def load(session: AsyncSession, directory: Path = SAMPLETON) -> seed.SeedReport:
    report = await seed.load_fixture(session, seed.read_fixture(directory))
    session.expire_all()
    return report


# ---------- TC-110: idempotent loading ----------


@pytest.mark.asyncio
async def test_tc_110_seed_twice_gives_identical_rows(db_session: AsyncSession) -> None:
    await load(db_session)
    counts = await table_counts(db_session)
    snapshot = await sampleton_snapshot(db_session)

    second = await load(db_session)

    assert await table_counts(db_session) == counts
    assert await sampleton_snapshot(db_session) == snapshot  # ids and updated_at untouched
    assert (second.places.inserted, second.places.updated) == (0, 0)
    assert second.places.unchanged == 30
    assert second.hours_replaced == 0
    assert second.deactivated == 0


@pytest.mark.asyncio
async def test_seed_loads_one_sample_destination_with_30_places(db_session: AsyncSession) -> None:
    report = await load(db_session)
    assert report.read == {
        "destinations": 1,
        "data_sources": 1,
        "places": 30,
        "opening_hours": 189,
    }

    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    assert destination.is_sample is True
    assert destination.name.endswith("(sample)")
    source = await db_session.scalar(select(DataSource).where(DataSource.name == SAMPLE_SOURCE))
    assert source is not None
    assert (source.source_type, source.licence) == ("other", "synthetic test data")
    assert source.retrieved_on is not None  # PD-IMP-205-1: every source carries a retrieved date

    places = list(
        await db_session.scalars(select(Place).where(Place.destination_id == destination.id))
    )
    assert len(places) == 30
    for place in places:
        # Every place is labelled SAMPLE and comes from the SAMPLE data source.
        assert "(sample)" in place.name
        assert place.source_id == source.id
        assert place.verification_status == "estimated"
        assert place.is_active is True


@pytest.mark.asyncio
async def test_sampleton_has_the_counts_of_step_2(db_session: AsyncSession) -> None:
    await load(db_session)
    destination = await db_session.scalar(
        select(Destination).where(Destination.slug == "sampleton")
    )
    assert destination is not None
    places = list(
        await db_session.scalars(select(Place).where(Place.destination_id == destination.id))
    )
    hours = list(
        await db_session.scalars(
            select(PlaceOpeningHours).where(
                PlaceOpeningHours.place_id.in_([place.id for place in places])
            )
        )
    )
    with_hours = {row.place_id for row in hours}

    categories = Counter(place.category for place in places)
    assert set(categories) == {
        "sight",
        "museum",
        "nature",
        "food",
        "shopping",
        "entertainment",
        "religious",
        "activity",
    }
    assert categories["food"] >= 6
    assert len({row.place_id for row in hours if row.closes_next_day}) == 3
    assert len({row.place_id for row in hours if row.is_closed}) == 3
    no_hours = [place for place in places if place.id not in with_hours]
    assert len(no_hours) == 3
    assert all(place.hours_label == "unavailable" for place in no_hours)
    assert all(place.hours_label == "estimate" for place in places if place.id in with_hours)
    assert sum(place.step_free is True for place in places) == 2
    unpriced = [place for place in places if place.price_label == "unavailable"]
    assert len(unpriced) == 2
    assert all(place.price_min is None and place.price_max is None for place in unpriced)
    assert all(
        place.price_label == "estimate" and place.price_currency == "GBP"
        for place in places
        if place not in unpriced
    )


@pytest.mark.asyncio
async def test_seed_updates_changed_rows_and_deactivates_missing_places(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    await load(db_session)
    changed = tmp_path / "sampleton"
    shutil.copytree(SAMPLETON, changed)
    lines = (changed / "places.csv").read_text(encoding="utf-8").splitlines()
    header, rows = lines[0], lines[1:]
    rows = [
        row.replace(",60,", ",75,", 1) if row.startswith("sample-001,") else row for row in rows
    ]
    rows = [row for row in rows if not row.startswith("sample-030,")]
    (changed / "places.csv").write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")
    hours = (changed / "opening_hours.csv").read_text(encoding="utf-8").splitlines()
    (changed / "opening_hours.csv").write_text(
        "\n".join(line for line in hours if not line.startswith("sample-030,")) + "\n",
        encoding="utf-8",
    )

    report = await load(db_session, changed)

    assert (report.places.inserted, report.places.updated, report.places.unchanged) == (0, 1, 28)
    assert report.deactivated == 1
    retired = await db_session.scalar(select(Place).where(Place.external_ref == "sample-030"))
    assert retired is not None  # never deleted
    assert retired.is_active is False


# ---------- Exit codes ----------


def broken_copy(tmp_path: Path, file: str, old: str, new: str) -> Path:
    directory = tmp_path / "broken"
    shutil.copytree(SAMPLETON, directory)
    path = directory / file
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return directory


@pytest.mark.parametrize(
    ("file", "old", "new", "message"),
    [
        ("places.csv", "typical_duration_min", "duration", "places.csv line 1: missing columns"),
        ("destination.json", "Europe/London", "Europe/Nowhere", "is not an IANA name"),
        (
            "destination.json",
            '"min_usable_places": 30',
            '"min_usable_places": "thirty"',
            "min_usable_places must be a whole number",
        ),
        (
            "opening_hours.csv",
            "sample-001,1,",
            "sample-999,1,",
            "opening_hours.csv line 2: external_ref 'sample-999' is not in places.csv",
        ),
        (
            "sources.csv",
            "2026-10-31",
            "31/10/2026",
            "sources.csv line 2: retrieved_on is not a date",
        ),
    ],
    ids=["missing column", "bad timezone", "bad minimum", "hours for an unknown place", "bad date"],
)
def test_seed_format_error_exits_non_zero(
    clean_settings_env: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
    file: str,
    old: str,
    new: str,
    message: str,
) -> None:
    clean_settings_env.setenv("APP_ENV", "test")
    directory = broken_copy(tmp_path, file, old, new)

    assert seed.main([str(directory)]) == 1
    assert message in capsys.readouterr().err


def test_seed_refuses_sample_data_outside_local_and_test(
    clean_settings_env: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    clean_settings_env.setenv("APP_ENV", "staging")
    assert seed.main([str(SAMPLETON)]) == 1
    assert "loaded only when APP_ENV is local or test" in capsys.readouterr().err


# ---------- IMP-205: quality gate in the import ----------


def edited_copy(tmp_path: Path, file: str, edits: dict[str, str]) -> Path:
    """A copy of Sampleton where each row starting with a key is replaced by its value."""
    directory = tmp_path / "edited"
    if not directory.exists():
        shutil.copytree(SAMPLETON, directory)
    path = directory / file
    lines = path.read_text(encoding="utf-8").splitlines()
    for prefix, replacement in edits.items():
        matches = [n for n, line in enumerate(lines) if line.startswith(prefix)]
        assert matches, prefix
        lines[matches[0]] = replacement(lines[matches[0]]) if callable(replacement) else replacement
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return directory


def set_field(column: str, value: str) -> Any:
    index = import_pipeline.PLACE_COLUMNS.index(column)

    def edit(line: str) -> str:
        cells = line.split(",")
        cells[index] = value
        return ",".join(cells)

    return edit


async def places_by_ref(session: AsyncSession) -> dict[str, Place]:
    destination = await session.scalar(select(Destination).where(Destination.slug == "sampleton"))
    assert destination is not None
    rows = await session.scalars(select(Place).where(Place.destination_id == destination.id))
    return {str(place.external_ref): place for place in rows}


@pytest.mark.asyncio
async def test_tc_108_rows_without_source_or_verification_status_are_rejected_and_listed(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    directory = edited_copy(
        tmp_path,
        "places.csv",
        {
            "sample-002,": set_field("source_name", "Unknown source"),
            "sample-003,": set_field("verification_status", ""),
        },
    )
    prepared = seed.read_fixture(directory)

    assert [(row.line, row.external_ref) for row in prepared.rejected] == [
        (3, "sample-002"),
        (4, "sample-003"),
    ]
    assert prepared.rejected[0].result.rejects == ["source 'Unknown source' is not in sources.csv"]
    assert prepared.rejected[1].result.rejects == ["verification_status is missing"]
    report = import_pipeline.render_report(prepared)
    assert "| 3 | sample-002 |" in report
    assert "| 4 | sample-003 |" in report

    await seed.load_fixture(db_session, prepared)
    stored = await places_by_ref(db_session)
    assert len(stored) == 28
    assert "sample-002" not in stored
    assert "sample-003" not in stored


def test_tc_109_the_report_states_rows_read_loaded_and_rejected(
    clean_settings_env: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = edited_copy(tmp_path, "places.csv", {"sample-010,": set_field("lat", "10.000000")})
    # --check needs no database: no DATABASE_URL is set here.
    assert seed.main([str(directory), "--check"]) == 0

    report = (directory / "quality_report.md").read_text(encoding="utf-8")
    assert "| Place rows read (`places.csv`) | 30 |" in report
    assert "| Opening-hours rows read (`opening_hours.csv`) | 189 |" in report
    assert "| Loaded (passed the gate) | 29 |" in report
    assert "| Rejected | 1 |" in report
    assert "outside the destination bounding box" in report  # TC-111 through the pipeline
    out = capsys.readouterr().out
    assert "gate loaded 29, rejected 1, flagged 0" in out
    assert "nothing was written to the database" in out


def test_the_committed_sampleton_report_is_current() -> None:
    committed = (SAMPLETON / "quality_report.md").read_text(encoding="utf-8")
    assert committed == import_pipeline.render_report(seed.read_fixture(SAMPLETON))
    assert "| Loaded (passed the gate) | 30 |" in committed
    assert "| Rejected | 0 |" in committed
    assert "Minimum met: 30 usable places against a minimum of 30." in committed


@pytest.mark.asyncio
async def test_tc_110_a_place_that_now_fails_the_gate_is_deactivated_not_deleted(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    await load(db_session)
    directory = edited_copy(
        tmp_path, "places.csv", {"sample-004,": set_field("typical_duration_min", "600")}
    )

    report = await load(db_session, directory)

    assert report.deactivated == 1
    assert (report.places.inserted, report.places.unchanged) == (0, 29)
    stored = await places_by_ref(db_session)
    assert len(stored) == 30  # never deleted
    assert stored["sample-004"].is_active is False

    again = await load(db_session)  # the fixed file reactivates it
    assert again.places.updated == 1
    assert (await places_by_ref(db_session))["sample-004"].is_active is True


@pytest.mark.asyncio
async def test_tc_112_unparseable_hours_store_unavailable_and_flag_the_row(
    db_session: AsyncSession, tmp_path: Path
) -> None:
    directory = edited_copy(
        tmp_path,
        "opening_hours.csv",
        {"sample-001,1,": lambda line: line.replace("09:00", "9am", 1)},
    )
    prepared = seed.read_fixture(directory)
    assert [row.external_ref for row in prepared.flagged] == ["sample-001"]
    assert "Flagged (loaded with hours unavailable) | 1 |" in import_pipeline.render_report(
        prepared
    )

    await seed.load_fixture(db_session, prepared)
    place = (await places_by_ref(db_session))["sample-001"]
    assert place.is_active is True
    assert place.hours_label == "unavailable"
    hours = await db_session.scalars(
        select(PlaceOpeningHours).where(PlaceOpeningHours.place_id == place.id)
    )
    assert list(hours) == []


def test_tc_113_a_shortfall_is_stated_and_strict_exits_non_zero(
    clean_settings_env: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    directory = tmp_path / "short"
    shutil.copytree(SAMPLETON, directory)
    destination = directory / "destination.json"
    destination.write_text(
        destination.read_text(encoding="utf-8").replace(
            '"min_usable_places": 30', '"min_usable_places": 31'
        ),
        encoding="utf-8",
    )

    assert seed.main([str(directory), "--check"]) == 0  # §5.6: still exits 0 without --strict
    report = (directory / "quality_report.md").read_text(encoding="utf-8")
    assert "Shortfall: 30 usable places, 1 below the minimum of 31." in report
    assert seed.main([str(directory), "--check", "--strict"]) == 1
    assert "below the minimum for sampleton" in capsys.readouterr().err


def test_check_mode_reads_sample_data_in_any_environment(
    clean_settings_env: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Nothing is written in --check mode, so the SAMPLE refusal applies only to loading.
    clean_settings_env.setenv("APP_ENV", "staging")
    directory = tmp_path / "copy"
    shutil.copytree(SAMPLETON, directory)
    assert seed.main([str(directory), "--check"]) == 0


@pytest.mark.asyncio
async def test_tc_101_tags_come_from_the_vocabulary_and_unknown_suitability_is_null(
    db_session: AsyncSession,
) -> None:
    await load(db_session)
    stored = await places_by_ref(db_session)

    tagged = [place for place in stored.values() if place.tags]
    assert len(tagged) == 30
    assert all(set(place.tags) <= vocabulary.TAGS for place in tagged)
    lookout = stored["sample-001"]
    assert set(lookout.tags) == {"views", "outdoor"}
    # sample-002 leaves step_free empty: stored as NULL (unknown), never false (TC-102).
    assert stored["sample-002"].step_free is None
    assert lookout.step_free is True
    assert stored["sample-004"].step_free is False


# ---------- make db-reset guard (§4.7, §5.7) ----------


@pytest.mark.parametrize(
    ("app_env", "url"),
    [
        ("staging", "postgresql+psycopg://u:p@localhost:5432/db"),
        ("production", "postgresql+psycopg://u:p@127.0.0.1:5432/db"),
        ("test", "postgresql+psycopg://u:p@db.example.test:5432/db"),
        ("local", ""),
    ],
)
def test_seed_db_reset_refuses_outside_local_test_databases(app_env: str, url: str) -> None:
    with pytest.raises(reset.ResetRefusedError):
        reset.check_allowed(app_env, url)


def test_seed_db_reset_allows_local_and_test_databases() -> None:
    reset.check_allowed("test", "postgresql+psycopg://u:p@localhost:5432/travel_test")
    reset.check_allowed("local", "postgresql+psycopg://u:p@127.0.0.1:54322/postgres")
