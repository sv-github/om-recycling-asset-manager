from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    __table_args__ = (
        Index(
            "uq_assets_serial_number_not_null",
            "serial_number",
            unique=True,
            postgresql_where=text("serial_number IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # Our permanent internal identifier
    asset_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Manufacturer's serial number.
    # Nullable because some equipment arrives without a readable serial.
    serial_number: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    # Traceability back to the receiving transaction
    collection_id: Mapped[int] = mapped_column(
        ForeignKey("collections.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Optional because an asset may be received without a customer-supplied
    # collection line item.
    collection_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("collection_items.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    asset_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    manufacturer: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Asset lifecycle
    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="received",
        server_default="received",
        index=True,
    )

    # Receiving information
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    received_by: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    receiving_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Data security / sanitisation
    data_wipe_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="not_started",
        server_default="not_started",
        index=True,
    )

    data_wipe_method: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    data_wipe_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    data_wipe_reference: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # Final processing result
    final_disposition: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
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