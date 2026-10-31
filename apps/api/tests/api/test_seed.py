"""Seed command and the Sampleton SAMPLE fixture (§5.6, IMD-09; IMP-107: TC-110).

Database tests run in the rolled-back session of tests/fixtures/db.py, so they hold whether or
not the test database was already seeded. Format and environment refusals happen before any
database access.
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
from app.places import seed

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
        ("places.csv", "53.868000", "north", "places.csv line 2: lat is not a number"),
        ("places.csv", "typical_duration_min", "duration", "places.csv line 1: missing columns"),
        (
            "places.csv",
            "sample-002,SAMPLE fixture (synthetic)",
            "sample-002,Unknown source",
            "places.csv line 3: source_name 'Unknown source' is not in sources.csv",
        ),
        ("opening_hours.csv", "09:00", "9am", "opening_hours.csv line 2: open_time is not a time"),
        ("destination.json", "Europe/London", "Europe/Nowhere", "is not an IANA name"),
    ],
    ids=["bad number", "missing column", "unknown source", "bad time", "bad timezone"],
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
