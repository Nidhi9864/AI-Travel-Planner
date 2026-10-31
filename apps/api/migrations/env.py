"""Alembic environment (specification §5.5, IMD-01).

The schema is defined only by the SQL files in ``migrations/sql/``; each revision executes one of
them, so there is no target metadata and no autogenerate. Migrations use a synchronous engine with
the psycopg driver. The URL is ``DATABASE_URL`` read through ``app.core.config`` (never from
``alembic.ini``), and it is never printed. A caller that already holds a connection (the test
database fixture) passes it as ``config.attributes["connection"]`` instead.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection, make_url

from app.core.config import get_settings

config = context.config

# A caller that configures its own logging (pytest) sets configure_logger to False.
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def _database_url() -> str:
    url = get_settings().database_url.get_secret_value().strip()
    if not url:
        raise RuntimeError("DATABASE_URL is not set; alembic needs it (specification §4.5)")
    # Both the migrations and the app use psycopg 3 (§5.5); a plain postgresql:// URL would
    # otherwise select a driver that is not installed.
    return make_url(url).set(drivername="postgresql+psycopg").render_as_string(hide_password=False)


def _run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=None)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Write the SQL to standard output (alembic upgrade head --sql) without connecting."""
    context.configure(url=_database_url(), target_metadata=None, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection")
    if connection is not None:
        _run(connection)
        return
    engine = create_engine(_database_url(), poolclass=pool.NullPool)
    try:
        with engine.connect() as new_connection:
            _run(new_connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
