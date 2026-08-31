from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AssetInspection(Base):
    __tablename__ = "asset_inspections"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    inspection_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    inspection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    inspected_by: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    working_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    overall_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    display_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    body_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    keyboard_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    touchpad_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    hinge_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    ports_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    battery_condition: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    charger_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    ram_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    storage_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    cpu_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    gpu_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    accessories: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    inspection_notes: Mapped[str | None] = mapped_column(
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