"""0001 helpers: the updated_at trigger functions (Appendix A.2).

Revision ID: 0001
Revises: (none)

Executes migrations/sql/0001_helpers.sql; downgrade runs sql/down/0001_helpers.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0001_helpers"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
