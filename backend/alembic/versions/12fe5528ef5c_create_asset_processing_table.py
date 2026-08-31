"""Create asset processing table

Revision ID: 12fe5528ef5c
Revises: cb856cbf1b40
Create Date: 2026-08-31 21:30:20.818105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12fe5528ef5c'
down_revision: Union[str, Sequence[str], None] = 'cb856cbf1b40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'asset_processing',

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
            'processing_type',
            sa.String(length=30),
            nullable=False,
        ),

        sa.Column(
            'grade',
            sa.String(length=20),
            nullable=True,
        ),

        sa.Column(
            'refurbishment_status',
            sa.String(length=30),
            server_default='not_required',
            nullable=False,
        ),

        sa.Column(
            'processor',
            sa.String(length=150),
            nullable=True,
        ),

        sa.Column(
            'processing_date',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),

        sa.Column(
            'condition_summary',
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            'repairs_performed',
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            'parts_replaced',
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            'testing_notes',
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            'processing_reference',
            sa.String(length=100),
            nullable=True,
        ),

        sa.Column(
            'cost',
            sa.Numeric(12, 2),
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
        op.f('ix_asset_processing_asset_id'),
        'asset_processing',
        ['asset_id'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_processing_processing_type'),
        'asset_processing',
        ['processing_type'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_processing_grade'),
        'asset_processing',
        ['grade'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_processing_refurbishment_status'),
        'asset_processing',
        ['refurbishment_status'],
        unique=False,
    )

    op.create_index(
        op.f('ix_asset_processing_processing_reference'),
        'asset_processing',
        ['processing_reference'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_asset_processing_processing_reference'),
        table_name='asset_processing',
    )

    op.drop_index(
        op.f('ix_asset_processing_refurbishment_status'),
        table_name='asset_processing',
    )

    op.drop_index(
        op.f('ix_asset_processing_grade'),
        table_name='asset_processing',
    )

    op.drop_index(
        op.f('ix_asset_processing_processing_type'),
        table_name='asset_processing',
    )

    op.drop_index(
        op.f('ix_asset_processing_asset_id'),
        table_name='asset_processing',
    )

    op.drop_table('asset_processing')