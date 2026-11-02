"""Seed command: ``python -m app.places.seed <dir> [<dir> ...] [--check] [--strict]`` (§5.6).

Loads one destination per directory (``destination.json``, ``sources.csv``, ``places.csv``,
``opening_hours.csv``) into the four reference tables, of which this command is the only writer.
The work is done by ``app.places.import_pipeline.run`` (IMP-205): every place row passes the
quality gate, each directory gets its ``quality_report.md``, and each directory is loaded in one
transaction. ``--check`` applies the gate and writes the report without touching the database;
``--strict`` exits 1 when a destination has fewer usable places than ``min_usable_places``.
"""

import argparse
from pathlib import Path

from app.places.import_pipeline import (
    LoadReport,
    Prepared,
    SeedFormatError,
    SeedRefusedError,
    check_allowed,
    load,
    prepare,
    run,
)

# Names kept from IMP-107, used by the tests that load the SAMPLE fixture.
Fixture = Prepared
SeedReport = LoadReport
read_fixture = prepare
load_fixture = load

__all__ = [
    "Fixture",
    "SeedFormatError",
    "SeedRefusedError",
    "SeedReport",
    "check_allowed",
    "load_fixture",
    "main",
    "read_fixture",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m app.places.seed", description="Load destination directories (§5.6)."
    )
    parser.add_argument("directories", nargs="+", type=Path)
    parser.add_argument(
        "--check",
        action="store_true",
        help="apply the quality gate and write quality_report.md; write nothing to the database",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 (and load nothing) when usable places fall below min_usable_places",
    )
    args = parser.parse_args(argv)
    return run(args.directories, check=args.check, strict=args.strict)


if __name__ == "__main__":
    raise SystemExit(main())
