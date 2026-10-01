"""add flight plan columns

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-01 11:34:12.153911
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "aircraft", sa.Column("cruise_speed_kts", sa.Float(), server_default="450", nullable=False)
    )
    op.add_column(
        "aircraft", sa.Column("cruise_altitude_ft", sa.Float(), server_default="0", nullable=False)
    )
    op.add_column(
        "aircraft", sa.Column("route_distance_nm", sa.Float(), server_default="0", nullable=False)
    )
    op.add_column(
        "aircraft", sa.Column("distance_flown_nm", sa.Float(), server_default="0", nullable=False)
    )
    op.add_column(
        "aircraft",
        sa.Column("ground_time_remaining_s", sa.Float(), server_default="0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("aircraft", "ground_time_remaining_s")
    op.drop_column("aircraft", "distance_flown_nm")
    op.drop_column("aircraft", "route_distance_nm")
    op.drop_column("aircraft", "cruise_altitude_ft")
    op.drop_column("aircraft", "cruise_speed_kts")
