"""enforce QC template item order uniqueness

Revision ID: 394f8adb5142
Revises: d79ad011f32b
Create Date: 2026-09-14

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "394f8adb5142"
down_revision: Union[str, Sequence[str], None] = "d79ad011f32b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_qc_template_items_template_sort_order",
        "qc_template_items",
        ["template_id", "sort_order"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_qc_template_items_template_sort_order",
        "qc_template_items",
        type_="unique",
    )