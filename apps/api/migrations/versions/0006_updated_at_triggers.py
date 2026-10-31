"""0006 updated_at triggers; revokes the helper functions and alembic_version from browser roles (Appendix A.7).

Revision ID: 0006
Revises: 0005

Executes migrations/sql/0006_updated_at_triggers.sql; downgrade runs sql/down/0006_updated_at_triggers.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0006_updated_at_triggers"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
