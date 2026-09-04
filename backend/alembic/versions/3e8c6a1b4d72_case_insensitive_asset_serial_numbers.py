"""Enforce case-insensitive unique asset serial numbers

Revision ID: 3e8c6a1b4d72
Revises: d3f4a9c8b721
Create Date: 2026-09-04
"""

from alembic import op
import sqlalchemy as sa


revision = "3e8c6a1b4d72"
down_revision = "20b1e532935b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(
        "uq_assets_serial_number_not_null",
        table_name="assets",
    )

    op.create_index(
        "uq_assets_serial_number_not_null",
        "assets",
        [sa.text("lower(serial_number)")],
        unique=True,
        postgresql_where=sa.text("serial_number IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_assets_serial_number_not_null",
        table_name="assets",
    )

    op.create_index(
        "uq_assets_serial_number_not_null",
        "assets",
        ["serial_number"],
        unique=True,
        postgresql_where=sa.text("serial_number IS NOT NULL"),
    )
