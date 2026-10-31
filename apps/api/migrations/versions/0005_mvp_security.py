"""0005 security: row-level security, app_private.owns_trip and revoked browser privileges (Appendix A.6).

Revision ID: 0005
Revises: 0004

Executes migrations/sql/0005_mvp_security.sql; downgrade runs sql/down/0005_mvp_security.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0005_mvp_security"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
