"""Flight simulation engine.

Each aircraft cycles through these phases:

    on_ground --(departure time)--> climbing --> cruising --> descending
        ^                                                          |
        |                                                     (touchdown)
        +---(next flight assigned)--- landed (taxi-in) <-----------+

Aircraft fly the great circle from origin to destination. They climb at a fixed rate,
cruise, and start descending on a 3 nm per 1,000 ft profile so they reach the
destination's elevation at touchdown. Speed ramps between takeoff/landing speed and
the type's cruise speed with altitude.

All durations here are *simulated* seconds; the caller decides how fast simulated time
runs relative to wall-clock time.
"""

import random
from collections.abc import Sequence

from app import geo
from app.models import Aircraft, AircraftStatus, Airport

CLIMB_RATE_FPM = 2500
DESCENT_NM_PER_1000_FT = 3.0
TAKEOFF_SPEED_KTS = 160.0
LANDING_SPEED_KTS = 140.0
MAX_CRUISE_ALTITUDE_FT = 37000
# Cruise altitude grows with route length: ~1,000 ft per 7 nm, so short hops stay low.
CRUISE_ALTITUDE_FT_PER_NM = 150
MIN_CRUISE_ABOVE_FIELD_FT = 2000
# Destinations closer than this are only used if nothing farther exists.
MIN_ROUTE_NM = 100.0

TAXI_IN_TIME_S = 5 * 60
TURNAROUND_TIME_S = (10 * 60, 30 * 60)

AIRBORNE = {AircraftStatus.CLIMBING, AircraftStatus.CRUISING, AircraftStatus.DESCENDING}


def cruise_altitude_ft(origin: Airport, destination: Airport, route_nm: float) -> float:
    highest_field = max(origin.altitude_ft, destination.altitude_ft)
    target = highest_field + max(MIN_CRUISE_ABOVE_FIELD_FT, route_nm * CRUISE_ALTITUDE_FT_PER_NM)
    return float(min(MAX_CRUISE_ALTITUDE_FT, round(target / 1000) * 1000))


def choose_destination(origin: Airport, airports: Sequence[Airport], rng: random.Random) -> Airport:
    def route_nm(a: Airport) -> float:
        return geo.distance_nm(origin.latitude, origin.longitude, a.latitude, a.longitude)

    others = [a for a in airports if a.id != origin.id]
    if not others:
        raise ValueError("Need at least two airports to plan a flight.")
    far_enough = [a for a in others if route_nm(a) >= MIN_ROUTE_NM]
    return rng.choice(far_enough or others)


def plan_next_flight(
    aircraft: Aircraft,
    airports: Sequence[Airport],
    rng: random.Random,
    ground_time_s: float | None = None,
) -> None:
    """Park the aircraft at its origin with a new destination and a departure countdown."""
    origin = aircraft.origin
    destination = choose_destination(origin, airports, rng)
    route_nm = geo.distance_nm(
        origin.latitude, origin.longitude, destination.latitude, destination.longitude
    )

    aircraft.status = AircraftStatus.ON_GROUND
    aircraft.destination = destination
    aircraft.latitude = origin.latitude
    aircraft.longitude = origin.longitude
    aircraft.altitude_ft = float(origin.altitude_ft)
    aircraft.ground_speed_kts = 0.0
    aircraft.heading_deg = geo.initial_bearing_deg(
        origin.latitude, origin.longitude, destination.latitude, destination.longitude
    )
    aircraft.route_distance_nm = route_nm
    aircraft.distance_flown_nm = 0.0
    aircraft.cruise_altitude_ft = cruise_altitude_ft(origin, destination, route_nm)
    aircraft.ground_time_remaining_s = (
        ground_time_s if ground_time_s is not None else rng.uniform(*TURNAROUND_TIME_S)
    )


def advance_aircraft(
    aircraft: Aircraft, airports: Sequence[Airport], dt_s: float, rng: random.Random
) -> None:
    """Advance one aircraft by `dt_s` simulated seconds."""
    match aircraft.status:
        case AircraftStatus.ON_GROUND:
            aircraft.ground_time_remaining_s -= dt_s
            if aircraft.ground_time_remaining_s <= 0:
                _depart(aircraft)
        case AircraftStatus.LANDED:
            aircraft.ground_time_remaining_s -= dt_s
            if aircraft.ground_time_remaining_s <= 0:
                aircraft.origin = aircraft.destination
                plan_next_flight(aircraft, airports, rng)
        case _:
            _fly(aircraft, dt_s)


def _depart(aircraft: Aircraft) -> None:
    aircraft.status = AircraftStatus.CLIMBING
    aircraft.ground_time_remaining_s = 0.0
    aircraft.distance_flown_nm = 0.0
    aircraft.ground_speed_kts = TAKEOFF_SPEED_KTS


def _speed_kts(aircraft: Aircraft, origin: Airport, destination: Airport) -> float:
    cruise_alt = aircraft.cruise_altitude_ft
    cruise_speed = aircraft.cruise_speed_kts
    if aircraft.status == AircraftStatus.CRUISING:
        return cruise_speed
    if aircraft.status == AircraftStatus.CLIMBING:
        low_speed, field_alt = TAKEOFF_SPEED_KTS, origin.altitude_ft
    else:
        low_speed, field_alt = LANDING_SPEED_KTS, destination.altitude_ft
    span = max(1.0, cruise_alt - field_alt)
    progress = min(1.0, max(0.0, (aircraft.altitude_ft - field_alt) / span))
    return low_speed + (cruise_speed - low_speed) * progress


def _fly(aircraft: Aircraft, dt_s: float) -> None:
    origin, destination = aircraft.origin, aircraft.destination
    assert destination is not None, "airborne aircraft must have a destination"

    speed = _speed_kts(aircraft, origin, destination)
    aircraft.ground_speed_kts = speed
    aircraft.distance_flown_nm = min(
        aircraft.route_distance_nm, aircraft.distance_flown_nm + speed * dt_s / 3600
    )
    remaining_nm = aircraft.route_distance_nm - aircraft.distance_flown_nm

    if remaining_nm <= 0:
        _land(aircraft, destination)
        return

    fraction = aircraft.distance_flown_nm / aircraft.route_distance_nm
    aircraft.latitude, aircraft.longitude = geo.intermediate_point(
        origin.latitude, origin.longitude, destination.latitude, destination.longitude, fraction
    )
    aircraft.heading_deg = geo.initial_bearing_deg(
        aircraft.latitude, aircraft.longitude, destination.latitude, destination.longitude
    )

    if aircraft.status == AircraftStatus.CLIMBING:
        aircraft.altitude_ft += CLIMB_RATE_FPM * dt_s / 60
        if aircraft.altitude_ft >= aircraft.cruise_altitude_ft:
            aircraft.altitude_ft = aircraft.cruise_altitude_ft
            aircraft.status = AircraftStatus.CRUISING

    # Altitude on the descent path at this distance from the destination.
    glide_path_ft = destination.altitude_ft + remaining_nm / DESCENT_NM_PER_1000_FT * 1000
    if aircraft.status != AircraftStatus.DESCENDING and glide_path_ft <= aircraft.altitude_ft:
        aircraft.status = AircraftStatus.DESCENDING
    if aircraft.status == AircraftStatus.DESCENDING:
        aircraft.altitude_ft = min(aircraft.altitude_ft, glide_path_ft)


def _land(aircraft: Aircraft, destination: Airport) -> None:
    aircraft.status = AircraftStatus.LANDED
    aircraft.latitude = destination.latitude
    aircraft.longitude = destination.longitude
    aircraft.altitude_ft = float(destination.altitude_ft)
    aircraft.ground_speed_kts = 0.0
    aircraft.ground_time_remaining_s = TAXI_IN_TIME_S
