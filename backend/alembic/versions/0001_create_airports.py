"""create airports table

Revision ID: 0001
Revises:
Create Date: 2026-09-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "airports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=3), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("altitude_ft", sa.Integer(), nullable=False),
    )
    op.create_index("ix_airports_code", "airports", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_airports_code", table_name="airports")
    op.drop_table("airports")
