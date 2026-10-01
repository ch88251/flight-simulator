"""create aircraft table

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-30 23:59:29.851679
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "aircraft",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("callsign", sa.String(length=8), nullable=False),
        sa.Column("aircraft_type", sa.String(length=40), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "on_ground",
                "climbing",
                "cruising",
                "descending",
                "landed",
                name="aircraft_status",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("altitude_ft", sa.Float(), nullable=False),
        sa.Column("heading_deg", sa.Float(), nullable=False),
        sa.Column("ground_speed_kts", sa.Float(), nullable=False),
        sa.Column("origin_airport_id", sa.Integer(), nullable=False),
        sa.Column("destination_airport_id", sa.Integer(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["destination_airport_id"], ["airports.id"]),
        sa.ForeignKeyConstraint(["origin_airport_id"], ["airports.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_aircraft_callsign"), "aircraft", ["callsign"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_aircraft_callsign"), table_name="aircraft")
    op.drop_table("aircraft")
