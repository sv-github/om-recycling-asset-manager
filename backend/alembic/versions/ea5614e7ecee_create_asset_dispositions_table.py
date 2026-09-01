"""Create asset dispositions table

Revision ID: ea5614e7ecee
Revises: 12fe5528ef5c
Create Date: 2026-09-01 06:04:12.553281

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea5614e7ecee'
down_revision: Union[str, Sequence[str], None] = '12fe5528ef5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'asset_dispositions',

        sa.Column(
            'id',
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            'asset_id',
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            'disposition_type',
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            'disposition_status',
            sa.String(length=30),
            server_default='pending',
            nullable=False,
        ),

        sa.Column(
            'disposition_date',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),

        sa.Column(
            'processed_by',
            sa.String(length=150),
            nullable=True,
        ),

        sa.Column(
            'disposition_reference',
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            'recipient_name',
            sa.String(length=150),
            nullable=True,
        ),

        sa.Column(
            'recipient_reference',
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            'amount',
            sa.Numeric(12, 2),
            nullable=True,
        ),

        sa.Column(
            'currency',
            sa.String(length=3),
            nullable=True,
        ),

        sa.Column(
            'notes',
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),

        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ['asset_id'],
            ['assets.id'],
            ondelete='RESTRICT',
        ),

        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index(
        op.f('ix_asset_dispositions_asset_id'),
        'asset_dispositions',
        ['asset_id'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_dispositions_disposition_type'),
        'asset_dispositions',
        ['disposition_type'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_dispositions_disposition_status'),
        'asset_dispositions',
        ['disposition_status'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_dispositions_disposition_reference'),
        'asset_dispositions',
        ['disposition_reference'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_asset_dispositions_disposition_reference'),
        table_name='asset_dispositions',
    )

    op.drop_index(
        op.f('ix_asset_dispositions_disposition_status'),
        table_name='asset_dispositions',
    )

    op.drop_index(
        op.f('ix_asset_dispositions_disposition_type'),
        table_name='asset_dispositions',
    )

    op.drop_index(
        op.f('ix_asset_dispositions_asset_id'),
        table_name='asset_dispositions',
    )

    op.drop_table('asset_dispositions')