"""Create collection statuses

Revision ID: 7ca3a6644496
Revises: 945997f8acf8
Create Date: 2026-09-02 18:07:51.154469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ca3a6644496'
down_revision: Union[str, Sequence[str], None] = '945997f8acf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "collection_statuses",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "code",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_index(
        "ix_collection_statuses_is_active",
        "collection_statuses",
        ["is_active"],
        unique=False,
    )

    op.create_index(
        "ix_collection_statuses_sort_order",
        "collection_statuses",
        ["sort_order"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            INSERT INTO collection_statuses
                (code, name, description, is_active, sort_order)
            VALUES
                (
                    'scheduled',
                    'Scheduled',
                    'Collection is scheduled but not yet completed.',
                    true,
                    10
                ),
                (
                    'completed',
                    'Completed',
                    'Collection has been completed.',
                    true,
                    20
                )
            """
        )
    )

    op.add_column(
        "collections",
        sa.Column(
            "status_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_collections_status_id",
        "collections",
        ["status_id"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            UPDATE collections
            SET status_id = collection_statuses.id
            FROM collection_statuses
            WHERE collection_statuses.code = collections.status
            """
        )
    )

    op.alter_column(
        "collections",
        "status_id",
        nullable=False,
    )

    op.create_foreign_key(
        "collections_status_id_fkey",
        "collections",
        "collection_statuses",
        ["status_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.drop_index(
        "ix_collections_status",
        table_name="collections",
    )

    op.drop_column(
        "collections",
        "status",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "collections",
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE collections
            SET status = collection_statuses.code
            FROM collection_statuses
            WHERE collection_statuses.id = collections.status_id
            """
        )
    )

    op.alter_column(
        "collections",
        "status",
        nullable=False,
    )

    op.create_index(
        "ix_collections_status",
        "collections",
        ["status"],
        unique=False,
    )

    op.drop_constraint(
        "collections_status_id_fkey",
        "collections",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_collections_status_id",
        table_name="collections",
    )

    op.drop_column(
        "collections",
        "status_id",
    )

    op.drop_index(
        "ix_collection_statuses_sort_order",
        table_name="collection_statuses",
    )

    op.drop_index(
        "ix_collection_statuses_is_active",
        table_name="collection_statuses",
    )


    op.drop_table(
        "collection_statuses",
    )