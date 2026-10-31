"""Declarative base shared by every ORM model.

The models mirror the SQL migrations (IMD-01) for queries only: the schema is created by Alembic
running ``migrations/sql/``, never by ``Base.metadata.create_all`` (§5.5).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
