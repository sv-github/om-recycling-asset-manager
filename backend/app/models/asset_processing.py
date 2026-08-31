from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AssetProcessing(Base):
    __tablename__ = "asset_processing"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    processing_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    grade: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        index=True,
    )

    refurbishment_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="not_required",
        server_default="not_required",
        index=True,
    )

    processor: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    processing_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    condition_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    repairs_performed: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    parts_replaced: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    testing_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    processing_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )