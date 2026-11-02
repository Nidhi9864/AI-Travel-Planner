"""0007 RAG store: pgvector, rag_documents and rag_chunks, item citations and retrieval record (A1 §5.3).

Revision ID: 0007
Revises: 0006

Executes migrations/sql/0007_rag_store.sql; downgrade runs sql/down/0007_rag_store.down.sql (§5.5).
"""

from pathlib import Path

from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | None = None
depends_on: str | None = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
NAME = "0007_rag_store"


def upgrade() -> None:
    op.execute((SQL_DIR / f"{NAME}.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "down" / f"{NAME}.down.sql").read_text(encoding="utf-8"))
