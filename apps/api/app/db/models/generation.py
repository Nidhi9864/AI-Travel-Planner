"""Generation records, written by MOD-B06 (migration 0004, Appendix A.5; retrieval columns 0007)."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, SmallInteger, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class AiGeneration(Base):
    __tablename__ = "ai_generations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE")
    )
    provider: Mapped[str] = mapped_column(Text)
    model_id: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str | None] = mapped_column(Text)
    adapter_version: Mapped[str | None] = mapped_column(Text)
    prompt_template_id: Mapped[str] = mapped_column(Text)
    prompt_version: Mapped[str] = mapped_column(Text)
    input_schema_version: Mapped[str] = mapped_column(Text, server_default=text("'gr-1'"))
    output_schema_version: Mapped[str] = mapped_column(Text, server_default=text("'io-1'"))
    mapping_version: Mapped[str] = mapped_column(Text)
    generation_settings: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    scope: Mapped[str] = mapped_column(Text)
    scope_day_number: Mapped[int | None] = mapped_column(SmallInteger)
    status: Mapped[str] = mapped_column(Text, server_default=text("'queued'"))
    outcome: Mapped[str | None] = mapped_column(Text)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    repair_attempts: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    deterministic_repairs: Mapped[int] = mapped_column(SmallInteger, server_default=text("0"))
    validation_summary: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    thinking_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_estimate_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    cost_basis: Mapped[str | None] = mapped_column(Text)
    request_hash: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    retention_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now() + '90 days'::interval")
    )
    # Retrieval record (migration 0007, A1 §5.3); null until IMP-316.
    retrieval_mode: Mapped[str | None] = mapped_column(Text)
    embedding_model_id: Mapped[str | None] = mapped_column(Text)
    retrieval_ms: Mapped[int | None] = mapped_column(Integer)
