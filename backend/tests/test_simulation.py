import random

import pytest

from app import simulation
from app.models import Aircraft, AircraftStatus, Airport

DT_S = 30.0  # one tick at the default 30x time scale


def make_airport(id: int, code: str, lat: float, lon: float, alt: int) -> Airport:
    return Airport(
        id=id, code=code, name=code, city=code, latitude=lat, longitude=lon, altitude_ft=alt
    )


LAX = make_airport(1, "LAX", 33.9416, -118.4085, 128)
DEN = make_airport(2, "DEN", 39.8561, -104.6737, 5434)
JFK = make_airport(3, "JFK", 40.6413, -73.7781, 13)
EWR = make_airport(4, "EWR", 40.6895, -74.1745, 18)
AIRPORTS = [LAX, DEN, JFK, EWR]


def make_aircraft(origin: Airport, destination: Airport) -> Aircraft:
    aircraft = Aircraft(callsign="TST1", aircraft_type="Test", cruise_speed_kts=450.0)
    aircraft.origin = origin
    # Force the destination by offering only that airport.
    simulation.plan_next_flight(aircraft, [origin, destination], random.Random(0), ground_time_s=60)
    return aircraft


def fly_until_landed(aircraft: Aircraft, max_ticks: int = 10_000) -> list[Aircraft]:
    """Advance until landed, returning a snapshot of key fields for every tick."""
    history = []
    rng = random.Random(0)
    for _ in range(max_ticks):
        simulation.advance_aircraft(aircraft, AIRPORTS, DT_S, rng)
        history.append(
            Aircraft(
                status=aircraft.status,
                altitude_ft=aircraft.altitude_ft,
                ground_speed_kts=aircraft.ground_speed_kts,
                distance_flown_nm=aircraft.distance_flown_nm,
            )
        )
        if aircraft.status == AircraftStatus.LANDED:
            return history
    pytest.fail("aircraft never landed")


def phases(history: list[Aircraft]) -> list[AircraftStatus]:
    result: list[AircraftStatus] = []
    for snapshot in history:
        if not result or result[-1] != snapshot.status:
            result.append(snapshot.status)
    return result


def test_plan_next_flight_parks_aircraft_with_destination() -> None:
    aircraft = make_aircraft(LAX, JFK)

    assert aircraft.status == AircraftStatus.ON_GROUND
    assert aircraft.destination is JFK
    assert (aircraft.latitude, aircraft.longitude) == (LAX.latitude, LAX.longitude)
    assert aircraft.altitude_ft == LAX.altitude_ft
    assert aircraft.ground_speed_kts == 0
    assert aircraft.route_distance_nm == pytest.approx(2145, rel=0.01)
    assert aircraft.cruise_altitude_ft == simulation.MAX_CRUISE_ALTITUDE_FT
    assert 45 < aircraft.heading_deg < 90  # initial course is east-northeast


def test_waits_on_ground_until_departure_time() -> None:
    aircraft = make_aircraft(LAX, JFK)  # departs after 60 s
    rng = random.Random(0)

    simulation.advance_aircraft(aircraft, AIRPORTS, 30, rng)
    assert aircraft.status == AircraftStatus.ON_GROUND

    simulation.advance_aircraft(aircraft, AIRPORTS, 30, rng)
    assert aircraft.status == AircraftStatus.CLIMBING


def test_full_flight_goes_through_every_phase_and_lands_at_destination() -> None:
    aircraft = make_aircraft(LAX, JFK)
    history = fly_until_landed(aircraft)

    assert phases(history) == [
        AircraftStatus.ON_GROUND,
        AircraftStatus.CLIMBING,
        AircraftStatus.CRUISING,
        AircraftStatus.DESCENDING,
        AircraftStatus.LANDED,
    ]
    assert (aircraft.latitude, aircraft.longitude) == (JFK.latitude, JFK.longitude)
    assert aircraft.altitude_ft == JFK.altitude_ft
    assert aircraft.ground_speed_kts == 0
    assert aircraft.distance_flown_nm == pytest.approx(aircraft.route_distance_nm)

    # Roughly 2,145 nm at up to 450 kts: a bit over 5 hours of simulated time.
    flight_hours = sum(s.status in simulation.AIRBORNE for s in history) * DT_S / 3600
    assert 4.8 < flight_hours < 6


def test_altitude_and_speed_stay_within_flight_envelope() -> None:
    aircraft = make_aircraft(LAX, JFK)
    history = fly_until_landed(aircraft)

    airborne = [s for s in history if s.status in simulation.AIRBORNE]
    assert max(s.altitude_ft for s in airborne) == aircraft.cruise_altitude_ft
    assert min(s.altitude_ft for s in airborne) >= JFK.altitude_ft
    assert all(
        simulation.LANDING_SPEED_KTS <= s.ground_speed_kts <= aircraft.cruise_speed_kts
        for s in airborne
    )
    flown = [s.distance_flown_nm for s in airborne]
    assert flown == sorted(flown)


def test_descent_reaches_high_altitude_destination_field_elevation() -> None:
    aircraft = make_aircraft(LAX, DEN)
    history = fly_until_landed(aircraft)

    descending = [s for s in history if s.status == AircraftStatus.DESCENDING]
    altitudes = [s.altitude_ft for s in descending]
    assert altitudes == sorted(altitudes, reverse=True)
    assert altitudes[-1] >= DEN.altitude_ft
    assert aircraft.altitude_ft == DEN.altitude_ft


def test_short_hop_stays_low_and_may_skip_cruise() -> None:
    aircraft = make_aircraft(EWR, JFK)  # about 18 nm
    assert aircraft.cruise_altitude_ft <= 5000

    history = fly_until_landed(aircraft)
    assert phases(history)[-1] == AircraftStatus.LANDED
    assert max(s.altitude_ft for s in history) <= aircraft.cruise_altitude_ft


def test_after_taxi_in_aircraft_is_assigned_next_flight_from_arrival_airport() -> None:
    aircraft = make_aircraft(LAX, JFK)
    fly_until_landed(aircraft)
    rng = random.Random(0)

    simulation.advance_aircraft(aircraft, AIRPORTS, simulation.TAXI_IN_TIME_S - 1, rng)
    assert aircraft.status == AircraftStatus.LANDED

    simulation.advance_aircraft(aircraft, AIRPORTS, 1, rng)
    assert aircraft.status == AircraftStatus.ON_GROUND
    assert aircraft.origin is JFK
    assert aircraft.destination is not None
    assert aircraft.destination is not JFK
    low, high = simulation.TURNAROUND_TIME_S
    assert low <= aircraft.ground_time_remaining_s <= high


def test_choose_destination_prefers_routes_of_at_least_minimum_length() -> None:
    rng = random.Random(0)
    # From JFK, EWR is under MIN_ROUTE_NM away, so it is never chosen while others exist.
    choices = {simulation.choose_destination(JFK, AIRPORTS, rng).code for _ in range(200)}
    assert choices == {"LAX", "DEN"}

    # ...but it is used when it is the only other airport.
    assert simulation.choose_destination(JFK, [JFK, EWR], rng) is EWR


def test_choose_destination_needs_another_airport() -> None:
    with pytest.raises(ValueError):
        simulation.choose_destination(JFK, [JFK], random.Random(0))
