"""Operator commands for a stub database (Amendment A1 §5.1, NFR-022; IMP-219).

``python -m app.db.admin delete-user --user-id <uuid>`` is the database half of the deletion
procedure: after the user is deleted in Supabase Auth, Kirtan runs it as a one-off task. It deletes
the user's ``auth.users`` row in one transaction; the foreign keys cascade to the profile, trips
and plans. It refuses unless ``DB_AUTH_STUB`` is true, because on Supabase the auth schema belongs
to Supabase Auth. It prints only the number of rows deleted; never the URL or credentials.
"""

import argparse
import sys
import uuid

import psycopg

from app.core.config import ConfigError, load_settings
from app.db.auth_stub import libpq_url


def delete_user(conninfo: str, user_id: uuid.UUID) -> int:
    """Delete the auth.users row of ``user_id``; returns the number of rows deleted (0 or 1)."""
    with psycopg.connect(conninfo) as conn, conn.transaction():
        cursor = conn.execute("delete from auth.users where id = %s", (user_id,))
        return cursor.rowcount


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    commands = parser.add_subparsers(dest="command", required=True)
    delete = commands.add_parser("delete-user", help="delete one user's rows (NFR-022)")
    delete.add_argument("--user-id", type=uuid.UUID, required=True)
    args = parser.parse_args(argv)

    try:
        settings = load_settings()
        if not settings.db_auth_stub:
            print(
                "delete-user: refused; DB_AUTH_STUB is false (delete the user in Supabase Auth)",
                file=sys.stderr,
            )
            return 1
        database_url = settings.database_url.get_secret_value()
        if not database_url.strip():
            print("delete-user: DATABASE_URL is not set", file=sys.stderr)
            return 1
        deleted = delete_user(libpq_url(database_url), args.user_id)
    except (ConfigError, psycopg.Error, OSError) as exc:
        # The class name only: a driver message may carry the host or user name.
        print(f"delete-user: failed ({type(exc).__name__})", file=sys.stderr)
        return 1
    print(f"delete-user: {deleted} row(s) deleted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
