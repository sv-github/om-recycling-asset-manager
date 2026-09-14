from datetime import datetime

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
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QCTemplate(Base):
    __tablename__ = "qc_templates"

    __table_args__ = (
        UniqueConstraint(
            "category_id",
            "code",
            "version",
            name="uq_qc_templates_category_code_version",
        ),
        CheckConstraint(
            "version >= 1",
            name="ck_qc_templates_version_positive",
        ),
        Index(
            "ux_qc_templates_active_category",
            "category_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        Index(
            "ix_qc_templates_category_id",
            "category_id",
        ),
        Index(
            "ix_qc_templates_is_active",
            "is_active",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            "asset_categories.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
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

    category = relationship(
        "AssetCategory",
        lazy="joined",
    )

    items = relationship(
        "QCTemplateItem",
        back_populates="template",
        order_by="QCTemplateItem.sort_order",
    )
