"""Enforce unique non-null asset serial numbers

Revision ID: d3f4a9c8b721
Revises: 7ca3a6644496
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3f4a9c8b721'
down_revision: Union[str, Sequence[str], None] = '7ca3a6644496'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_assets_serial_number_not_null",
        "assets",
        ["serial_number"],
        unique=True,
        postgresql_where=sa.text("serial_number IS NOT NULL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_assets_serial_number_not_null",
        table_name="assets",
    )