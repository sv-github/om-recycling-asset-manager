"""Prevent negative collection expected item counts

Revision ID: 1afac97d02e3
Revises: c7401b522a3c
Create Date: 2026-09-03 10:52:46.949169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1afac97d02e3'
down_revision: Union[str, Sequence[str], None] = 'c7401b522a3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_collections_expected_item_count_nonnegative",
        "collections",
        "expected_item_count IS NULL OR expected_item_count >= 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_collections_expected_item_count_nonnegative",
        "collections",
        type_="check",
    )