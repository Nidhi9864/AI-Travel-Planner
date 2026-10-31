"""Budget settings, written by MOD-B09 (migration 0003, Appendix A.4)."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class BudgetSettings(Base):
    __tablename__ = "budget_settings"

    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), primary_key=True
    )
    transport_allowance_per_day: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    stay_budget_per_night: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    contingency_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), server_default=text("10"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
