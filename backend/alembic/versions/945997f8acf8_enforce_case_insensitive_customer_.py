"""Enforce case insensitive customer company names

Revision ID: 945997f8acf8
Revises: ea5614e7ecee
Create Date: 2026-09-02 16:20:09.329974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '945997f8acf8'
down_revision: Union[str, Sequence[str], None] = 'ea5614e7ecee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        "uq_customers_company_name_lower",
        "customers",
        [sa.text("lower(company_name)")],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "uq_customers_company_name_lower",
        table_name="customers",
    )


