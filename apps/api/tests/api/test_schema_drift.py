"""TC-337: the ORM metadata equals the migrated schema (IMD-01, §5.5; IMP-106 step 6).

The test database is migrated by ``alembic upgrade head`` (the SQL of Appendix A) and reflected.
Every table, column, type, nullability, server default, generated column, primary key and foreign
key (within schema public) is compared with ``app.db.models.metadata``; any difference fails.
"""

import re
from collections.abc import Iterator
from typing import Any

import pytest
from sqlalchemy import Column, Engine, Inspector, create_engine, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.pool import NullPool

from app.db.models import metadata

# The 15 MVP tables of §5.2 (migrations 0002 to 0004).
MVP_TABLES = {
    "destinations",
    "data_sources",
    "places",
    "place_opening_hours",
    "profiles",
    "trips",
    "trip_preferences",
    "trip_places",
    "budget_settings",
    "ai_generations",
    "itinerary_days",
    "itinerary_items",
    "itinerary_warnings",
    "itinerary_versions",
    "route_cache",
}
DIALECT = postgresql.dialect()


@pytest.fixture(scope="module")
def engine(migrated_database_url: str) -> Iterator[Engine]:
    engine = create_engine(migrated_database_url, poolclass=NullPool)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def inspector(engine: Engine) -> Inspector:
    return inspect(engine)


def _sql(expression: str | None) -> str | None:
    """Normalise a default or generated expression: drop casts, brackets, spaces and case.

    PostgreSQL reports ``'balanced'::text`` or ``((end_date - start_date) + 1)`` where the model
    says ``'balanced'`` or ``end_date - start_date + 1``; both normalise to the same text.
    """
    if expression is None:
        return None
    normalised = re.sub(r"::[a-z ]+(\[\])?", "", expression.lower())
    return re.sub(r"[\s()]", "", normalised)


def _orm_default(column: Column[Any]) -> str | None:
    default = column.server_default
    if default is None:
        return None
    arg = getattr(default, "arg", None)
    return _sql(getattr(arg, "text", arg))


def _orm_computed(column: Column[Any]) -> tuple[str | None, bool | None] | None:
    computed = column.computed
    if computed is None:
        return None
    return _sql(str(computed.sqltext)), computed.persisted


def _type(type_: Any) -> str:
    return str(type_.compile(dialect=DIALECT))


def test_schema_drift_tables(inspector: Inspector) -> None:
    migrated = set(inspector.get_table_names(schema="public")) - {"alembic_version"}
    assert set(metadata.tables) == MVP_TABLES
    assert migrated == MVP_TABLES


@pytest.mark.parametrize("table_name", sorted(MVP_TABLES))
def test_schema_drift_columns(inspector: Inspector, table_name: str) -> None:
    table = metadata.tables[table_name]
    reflected = {c["name"]: c for c in inspector.get_columns(table_name, schema="public")}
    problems: list[str] = []

    missing = [name for name in reflected if name not in table.c]
    extra = [column.name for column in table.c if column.name not in reflected]
    if missing:
        problems.append(f"columns in the database, not in the model: {missing}")
    if extra:
        problems.append(f"columns in the model, not in the database: {extra}")

    for column in table.c:
        db = reflected.get(column.name)
        if db is None:
            continue
        where = f"{table_name}.{column.name}"
        if _type(column.type) != _type(db["type"]):
            problems.append(f"{where}: type {_type(column.type)} != {_type(db['type'])} (database)")
        if column.nullable != db["nullable"]:
            problems.append(f"{where}: nullable {column.nullable} != {db['nullable']} (database)")
        db_computed = db.get("computed")
        db_computed_key = (
            None
            if db_computed is None
            else (_sql(str(db_computed["sqltext"])), db_computed.get("persisted"))
        )
        if _orm_computed(column) != db_computed_key:
            problems.append(f"{where}: generated {_orm_computed(column)} != {db_computed_key}")
        # A generated column reports its expression, not a default.
        db_default = None if db_computed is not None else _sql(db.get("default"))
        if _orm_default(column) != db_default:
            problems.append(f"{where}: server default {_orm_default(column)} != {db_default}")

    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("table_name", sorted(MVP_TABLES))
def test_schema_drift_keys(inspector: Inspector, table_name: str) -> None:
    table = metadata.tables[table_name]

    db_pk = inspector.get_pk_constraint(table_name, schema="public")["constrained_columns"]
    assert sorted(c.name for c in table.primary_key.columns) == sorted(db_pk)

    # Foreign keys inside schema public. profiles.id -> auth.users(id) is left out: the auth schema
    # belongs to Supabase and is not in the ORM metadata (app/db/models/profiles.py).
    db_fks = {
        (
            tuple(fk["constrained_columns"]),
            fk["referred_table"],
            tuple(fk["referred_columns"]),
            (fk.get("options") or {}).get("ondelete"),
        )
        for fk in inspector.get_foreign_keys(table_name, schema="public")
        if fk.get("referred_schema") in (None, "public")
    }
    orm_fks = {
        (
            tuple(c.name for c in constraint.columns),
            constraint.referred_table.name,
            tuple(element.column.name for element in constraint.elements),
            constraint.ondelete,
        )
        for constraint in table.foreign_key_constraints
    }
    assert orm_fks == db_fks
