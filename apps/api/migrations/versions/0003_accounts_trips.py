"""0003 accounts and trips: profiles, trips, trip_preferences, trip_places, budget_settings (Appendix A.4).

Needs auth.users: Supabase provides it; plain PostgreSQL needs sql/test_auth_stub.sql first.

Revision ID: 0003
Revises: 0002

Executes migrations/sql/0003_accounts_trips.sql; downgrade runs sql/down/0003_accounts_trips.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0003_accounts_trips"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
