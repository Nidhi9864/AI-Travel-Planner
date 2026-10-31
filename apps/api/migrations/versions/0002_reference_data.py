"""0002 reference data: destinations, data_sources, places, place_opening_hours (Appendix A.3).

Revision ID: 0002
Revises: 0001

Executes migrations/sql/0002_reference_data.sql; downgrade runs sql/down/0002_reference_data.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0002_reference_data"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
