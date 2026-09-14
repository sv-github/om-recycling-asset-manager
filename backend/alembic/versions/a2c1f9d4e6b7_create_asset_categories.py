"""Create asset category master.

Revision ID: a2c1f9d4e6b7
Revises: 5e9b1a2c7d44
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a2c1f9d4e6b7"
down_revision: Union[str, Sequence[str], None] = "5e9b1a2c7d44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


SEED_CATEGORIES = [
    {
        "code": "LAPTOP",
        "name": "Laptop",
        "description": "Laptop computers.",
        "is_active": True,
        "sort_order": 10,
    },
    {
        "code": "DESKTOP",
        "name": "Desktop",
        "description": "Desktop computers.",
        "is_active": True,
        "sort_order": 20,
    },
    {
        "code": "SERVER",
        "name": "Server",
        "description": "Server and rack-mounted computing equipment.",
        "is_active": True,
        "sort_order": 30,
    },
    {
        "code": "MONITOR",
        "name": "Monitor",
        "description": "Computer monitors and displays.",
        "is_active": True,
        "sort_order": 40,
    },
    {
        "code": "PRINTER",
        "name": "Printer",
        "description": "Printers and multifunction printing devices.",
        "is_active": True,
        "sort_order": 50,
    },
    {
        "code": "NETWORKING",
        "name": "Networking",
        "description": "Network equipment such as switches, routers, and access points.",
        "is_active": True,
        "sort_order": 60,
    },
    {
        "code": "MOBILE",
        "name": "Mobile",
        "description": "Mobile phones and related handheld devices.",
        "is_active": True,
        "sort_order": 70,
    },
    {
        "code": "TABLET",
        "name": "Tablet",
        "description": "Tablet computers.",
        "is_active": True,
        "sort_order": 80,
    },
    {
        "code": "STORAGE",
        "name": "Storage",
        "description": "Storage devices and storage systems.",
        "is_active": True,
        "sort_order": 90,
    },
    {
        "code": "UPS",
        "name": "UPS",
        "description": "Uninterruptible power supply equipment.",
        "is_active": True,
        "sort_order": 100,
    },
    {
        "code": "PERIPHERAL",
        "name": "Peripheral",
        "description": "Computer peripherals and accessories.",
        "is_active": True,
        "sort_order": 110,
    },
    {
        "code": "OTHER",
        "name": "Other",
        "description": "Equipment that does not fit another controlled category.",
        "is_active": True,
        "sort_order": 120,
    },
]


def upgrade() -> None:
    op.create_table(
        "asset_categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_asset_categories_code"),
    )

    op.create_index(
        "ix_asset_categories_is_active",
        "asset_categories",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "ix_asset_categories_sort_order",
        "asset_categories",
        ["sort_order"],
        unique=False,
    )
    op.create_index(
        "ux_asset_categories_code_lower",
        "asset_categories",
        [sa.text("lower(code)")],
        unique=True,
    )
    op.create_index(
        "ux_asset_categories_name_lower",
        "asset_categories",
        [sa.text("lower(name)")],
        unique=True,
    )

    op.bulk_insert(
        sa.table(
            "asset_categories",
            sa.column("code", sa.String(length=30)),
            sa.column("name", sa.String(length=100)),
            sa.column("description", sa.Text()),
            sa.column("is_active", sa.Boolean()),
            sa.column("sort_order", sa.Integer()),
        ),
        SEED_CATEGORIES,
    )


def downgrade() -> None:
    op.drop_index(
        "ux_asset_categories_name_lower",
        table_name="asset_categories",
    )
    op.drop_index(
        "ux_asset_categories_code_lower",
        table_name="asset_categories",
    )
    op.drop_index(
        "ix_asset_categories_sort_order",
        table_name="asset_categories",
    )
    op.drop_index(
        "ix_asset_categories_is_active",
        table_name="asset_categories",
    )
    op.drop_table("asset_categories")
