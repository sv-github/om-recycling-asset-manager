"""Enforce the asset lifecycle state model.

Revision ID: 5e9b1a2c7d44
Revises: 8bcd4c61fe86, ea5614e7ecee
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5e9b1a2c7d44"
down_revision: Union[str, Sequence[str], None] = (
    "8bcd4c61fe86",
    "ea5614e7ecee",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assets",
        sa.Column("lifecycle_previous_status", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "assets",
        sa.Column("lifecycle_hold_reason", sa.Text(), nullable=True),
    )

    op.create_check_constraint(
        "ck_assets_status_valid",
        "assets",
        "status IN ('received', 'in_process', 'ready', 'disposed', 'on_hold', 'closed')",
    )
    op.create_check_constraint(
        "ck_assets_hold_state_consistent",
        "assets",
        "(status = 'on_hold' AND lifecycle_previous_status IN "
        "('received', 'in_process', 'ready') "
        "AND lifecycle_hold_reason IS NOT NULL) "
        "OR (status <> 'on_hold' AND lifecycle_previous_status IS NULL "
        "AND lifecycle_hold_reason IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_assets_hold_state_consistent", "assets", type_="check")
    op.drop_constraint("ck_assets_status_valid", "assets", type_="check")
    op.drop_column("assets", "lifecycle_hold_reason")
    op.drop_column("assets", "lifecycle_previous_status")
