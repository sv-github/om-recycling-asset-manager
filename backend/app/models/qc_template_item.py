from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QCTemplateItem(Base):
    __tablename__ = "qc_template_items"

    __table_args__ = (
        UniqueConstraint(
            "template_id",
            "item_code",
            name="uq_qc_template_items_template_code",
        ),
        UniqueConstraint(
            "template_id",
            "sort_order",
            name="uq_qc_template_items_template_sort_order",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="ck_qc_template_items_sort_order_nonnegative",
        ),
        Index(
            "ix_qc_template_items_template_id",
            "template_id",
        ),
        Index(
            "ix_qc_template_items_sort_order",
            "sort_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    template_id: Mapped[int] = mapped_column(
        ForeignKey(
            "qc_templates.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    item_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    label: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    response_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    options: Mapped[list[Any] | dict[str, Any] | None] = mapped_column(
        JSONB,
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

    template = relationship(
        "QCTemplate",
        back_populates="items",
    )