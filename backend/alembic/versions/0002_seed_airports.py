"""seed major US airports

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (code, name, city, latitude, longitude, altitude_ft)
AIRPORTS = [
    ("ATL", "Hartsfield-Jackson Atlanta International", "Atlanta, GA", 33.6407, -84.4277, 1026),
    ("BOS", "Boston Logan International", "Boston, MA", 42.3656, -71.0096, 20),
    ("CLT", "Charlotte Douglas International", "Charlotte, NC", 35.2144, -80.9473, 748),
    ("DEN", "Denver International", "Denver, CO", 39.8561, -104.6737, 5434),
    ("DFW", "Dallas/Fort Worth International", "Dallas-Fort Worth, TX", 32.8998, -97.0403, 607),
    ("DTW", "Detroit Metropolitan Wayne County", "Detroit, MI", 42.2162, -83.3554, 645),
    ("EWR", "Newark Liberty International", "Newark, NJ", 40.6895, -74.1745, 18),
    ("IAH", "George Bush Intercontinental", "Houston, TX", 29.9902, -95.3368, 97),
    ("JFK", "John F. Kennedy International", "New York, NY", 40.6413, -73.7781, 13),
    ("LAS", "Harry Reid International", "Las Vegas, NV", 36.0840, -115.1537, 2181),
    ("LAX", "Los Angeles International", "Los Angeles, CA", 33.9416, -118.4085, 128),
    ("MCO", "Orlando International", "Orlando, FL", 28.4312, -81.3081, 96),
    ("MIA", "Miami International", "Miami, FL", 25.7959, -80.2870, 8),
    ("MSP", "Minneapolis-Saint Paul International", "Minneapolis, MN", 44.8848, -93.2223, 841),
    ("ORD", "O'Hare International", "Chicago, IL", 41.9742, -87.9073, 672),
    ("PHL", "Philadelphia International", "Philadelphia, PA", 39.8744, -75.2424, 36),
    ("PHX", "Phoenix Sky Harbor International", "Phoenix, AZ", 33.4342, -112.0116, 1135),
    ("SEA", "Seattle-Tacoma International", "Seattle, WA", 47.4502, -122.3088, 433),
    ("SFO", "San Francisco International", "San Francisco, CA", 37.6213, -122.3790, 13),
    ("SLC", "Salt Lake City International", "Salt Lake City, UT", 40.7899, -111.9791, 4227),
]

airports = sa.table(
    "airports",
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("city", sa.String),
    sa.column("latitude", sa.Float),
    sa.column("longitude", sa.Float),
    sa.column("altitude_ft", sa.Integer),
)


def upgrade() -> None:
    op.bulk_insert(
        airports,
        [
            dict(code=c, name=n, city=city, latitude=lat, longitude=lon, altitude_ft=alt)
            for c, n, city, lat, lon, alt in AIRPORTS
        ],
    )


def downgrade() -> None:
    op.execute(airports.delete().where(airports.c.code.in_([a[0] for a in AIRPORTS])))
