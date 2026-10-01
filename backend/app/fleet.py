import logging
import random

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Aircraft, Airport
from app.simulation import plan_next_flight

logger = logging.getLogger(__name__)

AIRLINE_PREFIXES = ["AAL", "DAL", "UAL", "SWA", "ASA", "JBU", "FFT", "NKS"]
# Aircraft type -> typical cruise speed (knots).
AIRCRAFT_TYPES = {
    "Airbus A320": 450.0,
    "Airbus A321neo": 450.0,
    "Boeing 737-800": 453.0,
    "Boeing 737 MAX 8": 453.0,
    "Boeing 787-9": 488.0,
    "Embraer E175": 430.0,
}
# First departures are staggered over this many simulated seconds.
INITIAL_DEPARTURE_WINDOW_S = 10 * 60


def generate_callsigns(count: int, rng: random.Random) -> list[str]:
    callsigns: set[str] = set()
    while len(callsigns) < count:
        callsigns.add(f"{rng.choice(AIRLINE_PREFIXES)}{rng.randint(1, 9999)}")
    return sorted(callsigns)


def replace_fleet(db: Session, count: int, rng: random.Random | None = None) -> list[Aircraft]:
    """Delete all aircraft and create `count` new ones on the ground at random airports.

    Each aircraft is given a destination and a departure countdown.
    """
    rng = rng or random.Random()
    airports = list(db.scalars(select(Airport)))
    if not airports:
        raise RuntimeError("No airports in the database; run `alembic upgrade head` first.")

    db.execute(delete(Aircraft))
    fleet = []
    for callsign in generate_callsigns(count, rng):
        aircraft_type = rng.choice(list(AIRCRAFT_TYPES))
        aircraft = Aircraft(
            callsign=callsign,
            aircraft_type=aircraft_type,
            cruise_speed_kts=AIRCRAFT_TYPES[aircraft_type],
            origin=rng.choice(airports),
        )
        plan_next_flight(
            aircraft, airports, rng, ground_time_s=rng.uniform(0, INITIAL_DEPARTURE_WINDOW_S)
        )
        fleet.append(aircraft)
    db.add_all(fleet)
    db.commit()
    logger.info(
        "Created fleet: %s",
        ", ".join(f"{a.callsign} {a.origin.code}->{a.destination.code}" for a in fleet),
    )
    return fleet
