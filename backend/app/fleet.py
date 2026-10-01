import logging
import random

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Aircraft, AircraftStatus, Airport

logger = logging.getLogger(__name__)

AIRLINE_PREFIXES = ["AAL", "DAL", "UAL", "SWA", "ASA", "JBU", "FFT", "NKS"]
AIRCRAFT_TYPES = [
    "Airbus A320",
    "Airbus A321neo",
    "Boeing 737-800",
    "Boeing 737 MAX 8",
    "Boeing 787-9",
    "Embraer E175",
]


def generate_callsigns(count: int, rng: random.Random) -> list[str]:
    callsigns: set[str] = set()
    while len(callsigns) < count:
        callsigns.add(f"{rng.choice(AIRLINE_PREFIXES)}{rng.randint(1, 9999)}")
    return sorted(callsigns)


def replace_fleet(db: Session, count: int, rng: random.Random | None = None) -> list[Aircraft]:
    """Delete all aircraft and create `count` new ones parked at random airports."""
    rng = rng or random.Random()
    airports = list(db.scalars(select(Airport)))
    if not airports:
        raise RuntimeError("No airports in the database; run `alembic upgrade head` first.")

    db.execute(delete(Aircraft))
    fleet = []
    for callsign in generate_callsigns(count, rng):
        airport = rng.choice(airports)
        fleet.append(
            Aircraft(
                callsign=callsign,
                aircraft_type=rng.choice(AIRCRAFT_TYPES),
                status=AircraftStatus.ON_GROUND,
                latitude=airport.latitude,
                longitude=airport.longitude,
                altitude_ft=airport.altitude_ft,
                heading_deg=0.0,
                ground_speed_kts=0.0,
                origin=airport,
                destination=None,
            )
        )
    db.add_all(fleet)
    db.commit()
    logger.info(
        "Created fleet: %s", ", ".join(f"{a.callsign}@{a.origin.code}" for a in fleet)
    )
    return fleet
