import pytest

from app import geo

LAX = (33.9416, -118.4085)
JFK = (40.6413, -73.7781)


def test_distance_lax_to_jfk() -> None:
    # Published great-circle distance is about 2,145 nm.
    assert geo.distance_nm(*LAX, *JFK) == pytest.approx(2145, rel=0.01)


def test_distance_is_symmetric_and_zero_for_same_point() -> None:
    assert geo.distance_nm(*LAX, *JFK) == pytest.approx(geo.distance_nm(*JFK, *LAX))
    assert geo.distance_nm(*LAX, *LAX) == 0


@pytest.mark.parametrize(
    ("destination", "expected"),
    [((1, 0), 0), ((0, 1), 90), ((-1, 0), 180), ((0, -1), 270)],
)
def test_initial_bearing_cardinal_directions(
    destination: tuple[float, float], expected: float
) -> None:
    assert geo.initial_bearing_deg(0, 0, *destination) == pytest.approx(expected)


def test_intermediate_point_endpoints_and_midpoint() -> None:
    assert geo.intermediate_point(*LAX, *JFK, 0) == pytest.approx(LAX)
    assert geo.intermediate_point(*LAX, *JFK, 1) == pytest.approx(JFK)

    mid = geo.intermediate_point(*LAX, *JFK, 0.5)
    assert geo.distance_nm(*LAX, *mid) == pytest.approx(geo.distance_nm(*mid, *JFK))


def test_intermediate_point_follows_great_circle_north_of_rhumb_line() -> None:
    # Great-circle routes between northern-hemisphere cities bow toward the pole.
    mid_lat, _ = geo.intermediate_point(*LAX, *JFK, 0.5)
    assert mid_lat > (LAX[0] + JFK[0]) / 2
