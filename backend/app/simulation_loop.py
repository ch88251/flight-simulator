"""Background task that advances the simulation in the database on a fixed tick."""

import asyncio
import logging
import random
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Aircraft, Airport
from app.simulation import advance_aircraft

logger = logging.getLogger(__name__)

# Cap on real time credited to one tick, so a stall (debugger, laptop sleep)
# doesn't teleport aircraft across the map.
MAX_TICK_REAL_SECONDS = 5.0


def tick(db: Session, dt_s: float, rng: random.Random) -> None:
    """Advance every aircraft by `dt_s` simulated seconds and commit."""
    airports = list(db.scalars(select(Airport)))
    for aircraft in db.scalars(select(Aircraft)):
        advance_aircraft(aircraft, airports, dt_s, rng)
    db.commit()


def _tick_in_new_session(dt_s: float, rng: random.Random) -> None:
    with SessionLocal() as db:
        tick(db, dt_s, rng)


async def run_simulation(time_scale: float, tick_seconds: float) -> None:
    """Run until cancelled. Each tick advances by elapsed real time x `time_scale`."""
    rng = random.Random()
    logger.info("Simulation started: %gx time scale, %gs tick", time_scale, tick_seconds)
    last = time.monotonic()
    while True:
        await asyncio.sleep(tick_seconds)
        now = time.monotonic()
        elapsed = min(now - last, MAX_TICK_REAL_SECONDS)
        last = now
        try:
            # SQLAlchemy sessions here are synchronous; keep them off the event loop.
            await asyncio.to_thread(_tick_in_new_session, elapsed * time_scale, rng)
        except Exception:
            logger.exception("Simulation tick failed")
