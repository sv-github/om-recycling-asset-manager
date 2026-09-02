"""Normalize customer company names

Revision ID: c7401b522a3c
Revises: d3f4a9c8b721
Create Date: 2026-09-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7401b522a3c"
down_revision: Union[str, Sequence[str], None] = "d3f4a9c8b721"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Normalize existing customer company names before applying
    # the stricter uniqueness and blank-name constraints.
    op.execute(
        """
        UPDATE customers
        SET company_name = btrim(company_name)
        WHERE company_name <> btrim(company_name)
        """
    )

    # Remove the previous case-insensitive uniqueness index.
    op.drop_index(
        "uq_customers_company_name_lower",
        table_name="customers",
    )

    # Prevent blank or whitespace-only company names.
    op.create_check_constraint(
        "ck_customers_company_name_not_blank",
        "customers",
        "btrim(company_name) <> ''",
    )

    # Enforce uniqueness after trimming and case normalization.
    op.create_index(
        "uq_customers_company_name_trimmed_lower",
        "customers",
        [sa.text("lower(btrim(company_name))")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "uq_customers_company_name_trimmed_lower",
        table_name="customers",
    )

    op.drop_constraint(
        "ck_customers_company_name_not_blank",
        "customers",
        type_="check",
    )

    op.create_index(
        "uq_customers_company_name_lower",
        "customers",
        [sa.text("lower(company_name)")],
        unique=True,
    )