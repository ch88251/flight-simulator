import random
from unittest.mock import MagicMock

from app import simulation_loop
from app.models import AircraftStatus
from tests.test_simulation import AIRPORTS, JFK, LAX, make_aircraft


def test_tick_advances_every_aircraft_and_commits() -> None:
    parked = make_aircraft(LAX, JFK)  # departs after 60 s
    flying = make_aircraft(JFK, LAX)
    flying.ground_time_remaining_s = 0
    simulation_loop.advance_aircraft(flying, AIRPORTS, 1, random.Random(0))
    assert flying.status == AircraftStatus.CLIMBING
    flown_before = flying.distance_flown_nm

    db = MagicMock()
    db.scalars.side_effect = [AIRPORTS, [parked, flying]]

    simulation_loop.tick(db, 30, random.Random(0))

    assert parked.ground_time_remaining_s == 30
    assert flying.distance_flown_nm > flown_before
    db.commit.assert_called_once()
