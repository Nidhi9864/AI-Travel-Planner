"""Place vocabulary of app/places/vocabulary.py against the CHECK lists of migration 0002 (IMP-205).

The module says its categories, labels and verification statuses equal the migration; these
cases read the SQL file and compare. Pure: no database.
"""

import re
from pathlib import Path

import pytest

from app.places import vocabulary

MIGRATION_0002 = Path(__file__).parents[3] / "migrations" / "sql" / "0002_reference_data.sql"


def _check_list(column: str) -> set[str]:
    sql = MIGRATION_0002.read_text(encoding="utf-8")
    match = re.search(rf"check\s*\(\s*{column}\s+in\s*\(([^)]*)\)", sql)
    assert match, f"no CHECK list for {column}"
    return set(re.findall(r"'([^']+)'", match.group(1)))


def test_categories_equal_the_migration() -> None:
    assert _check_list("category") == vocabulary.CATEGORIES


def test_offered_categories_are_all_but_stay() -> None:
    assert vocabulary.CATEGORIES - {"stay"} == vocabulary.OFFERED_CATEGORIES


@pytest.mark.parametrize("column", ["price_label", "hours_label"])
def test_source_labels_equal_the_migration(column: str) -> None:
    assert _check_list(column) == vocabulary.SOURCE_LABELS


def test_verification_statuses_equal_the_migration() -> None:
    assert _check_list("verification_status") == vocabulary.VERIFICATION_STATUSES


def test_suitability_flags_are_place_columns() -> None:
    sql = MIGRATION_0002.read_text(encoding="utf-8")
    for flag in vocabulary.SUITABILITY_FLAGS:
        assert re.search(rf"^\s*{flag}\s+boolean,", sql, re.MULTILINE), flag


def test_pricing_tags_are_present() -> None:
    assert {"child_half", "child_free", "price_per_group"} <= vocabulary.TAGS


def test_tags_are_lower_case_slugs() -> None:
    for tag in vocabulary.TAGS:
        assert re.fullmatch(r"[a-z]+([_-][a-z]+)*", tag), tag


def test_no_duplicate_enum_values() -> None:
    for enum in (vocabulary.Category, vocabulary.Tag, vocabulary.SuitabilityFlag):
        values = [member.value for member in enum]
        assert len(values) == len(set(values)), enum.__name__
