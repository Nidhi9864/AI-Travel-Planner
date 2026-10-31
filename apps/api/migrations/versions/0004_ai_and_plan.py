"""0004 generation records and the current plan (Appendix A.5).

Tables ai_generations, itinerary_days, itinerary_items, itinerary_warnings, itinerary_versions and
route_cache.

Revision ID: 0004
Revises: 0003

Executes migrations/sql/0004_ai_and_plan.sql; downgrade runs sql/down/0004_ai_and_plan.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0004_ai_and_plan"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
