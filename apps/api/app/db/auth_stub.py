"""Apply the Appendix A.1 auth stub when schema ``auth`` is missing (Amendment A1 §5.1; IMP-219).

``python -m app.db.auth_stub --if-missing`` (run by ``make db-bootstrap`` and the release task)
connects to ``DATABASE_URL`` with synchronous psycopg. On a database that already has schema
``auth`` (Supabase, or a stub applied earlier) it changes nothing. Otherwise it runs the stub file
that IMP-106 committed, unchanged; the file holds its own begin and commit, so it is one
transaction. Exit 0 on success, 1 on any error. The URL and credentials are never printed.
"""

import argparse
import sys

import psycopg

from app.core.config import ConfigError, load_settings
from app.db.reset import AUTH_STUB_SQL

_AUTH_SCHEMA_EXISTS = "select exists (select 1 from pg_namespace where nspname = 'auth')"


def libpq_url(database_url: str) -> str:
    """The SQLAlchemy URL as a libpq URL: the ``+psycopg`` driver suffix is removed."""
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def apply_if_missing(conninfo: str) -> bool:
    """Apply the stub unless schema auth exists; True when it was applied."""
    # Autocommit: the stub file's own begin/commit is the transaction.
    with psycopg.connect(conninfo, autocommit=True) as conn:
        row = conn.execute(_AUTH_SCHEMA_EXISTS).fetchone()
        if row is not None and row[0]:
            return False
        conn.execute(AUTH_STUB_SQL.read_text(encoding="utf-8"))  # the committed file, unchanged
        return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    parser.add_argument(
        "--if-missing",
        action="store_true",
        required=True,
        help="apply the stub only when schema auth does not exist (the only mode)",
    )
    parser.parse_args(argv)
    try:
        database_url = load_settings().database_url.get_secret_value()
        if not database_url.strip():
            print("auth stub: DATABASE_URL is not set", file=sys.stderr)
            return 1
        applied = apply_if_missing(libpq_url(database_url))
    except (ConfigError, psycopg.Error, OSError) as exc:
        # The class name only: a driver message may carry the host or user name.
        print(f"auth stub: failed ({type(exc).__name__})", file=sys.stderr)
        return 1
    print("auth stub: applied" if applied else "auth schema present; nothing to do")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
