"""Tests for boids/predator.py"""

import pygame as pg
import pytest

from my_boids.movement import arrival_velocity, limit_velocity, move_to
from my_boids.predator import Predator


def test_limit_velocity_accelerates_from_rest_without_mutating_inputs():
    current = pg.Vector2()
    desired = pg.Vector2(3, 4)

    result = limit_velocity(current, desired, max_speed=5, max_acceleration=0.5, max_deceleration=1)

    assert tuple(result) == pytest.approx((0.3, 0.4))
    assert current == pg.Vector2()
    assert desired == pg.Vector2(3, 4)
    assert result is not current
    assert result is not desired


@pytest.mark.parametrize(
    "speed, requested, braking, expected",
    [(5, 0, 1, 4), (5, 0, 0.1, 4.9), (0.4, 0, 1, 0), (0.4, -5, 1, 0)],
)
def test_limit_velocity_brakes_without_accelerating_through_rest(
    speed, requested, braking, expected
):
    result = limit_velocity(
        pg.Vector2(speed, 0),
        pg.Vector2(requested, 0),
        max_speed=5,
        max_acceleration=0.5,
        max_deceleration=braking,
    )

    assert tuple(result) == pytest.approx((expected, 0))


@pytest.mark.parametrize("requested", [(0, 5), (-5, 0), (8, 0), (0, 0)])
def test_limit_velocity_prioritizes_gradual_overspeed_braking(requested):
    current = pg.Vector2(8, 0)
    result = limit_velocity(
        current,
        pg.Vector2(requested),
        max_speed=5,
        max_acceleration=0.5,
        max_deceleration=1,
    )

    assert tuple(result) == pytest.approx((7, 0))
    assert current == pg.Vector2(8, 0)


@pytest.mark.parametrize("initial", [(0, 0), (3, 4)])
@pytest.mark.parametrize("max_speed", [5, 10])
def test_limit_velocity_coasts_with_independent_vectors(initial, max_speed):
    current = pg.Vector2(initial)
    desired = pg.Vector2(initial)

    result = limit_velocity(
        current, desired, max_speed=max_speed, max_acceleration=0.5, max_deceleration=1
    )

    assert tuple(result) == pytest.approx(initial)
    result.update(100, 100)
    assert tuple(current) == pytest.approx(initial)
    assert tuple(desired) == pytest.approx(initial)


def test_limit_velocity_tracks_speed_ceiling_over_multiple_updates():
    velocity = pg.Vector2()
    desired = pg.Vector2(300, 400)
    for update in range(1, 21):
        velocity = limit_velocity(
            velocity, desired, max_speed=5, max_acceleration=0.5, max_deceleration=1
        )
        assert velocity.length() == pytest.approx(min(5, update * 0.5))

    for expected in (4, 3, 2, 2):
        velocity = limit_velocity(
            velocity, desired, max_speed=2, max_acceleration=0.5, max_deceleration=1
        )
        assert velocity.length() == pytest.approx(expected)
        assert tuple(velocity.normalize()) == pytest.approx((0.6, 0.8))


def test_limit_velocity_reverses_only_after_braking_to_rest():
    velocity = pg.Vector2(5, 0)
    for speed in (4, 3, 2, 1, 0, -0.5, -1):
        velocity = limit_velocity(
            velocity, pg.Vector2(-5, 0), max_speed=5, max_acceleration=0.5, max_deceleration=1
        )
        assert tuple(velocity) == pytest.approx((speed, 0))


@pytest.mark.parametrize("field", ["max_speed", "max_acceleration", "max_deceleration"])
@pytest.mark.parametrize("invalid", [0, -1, float("nan"), float("inf"), -float("inf")])
def test_limit_velocity_rejects_invalid_limits(field, invalid):
    limits = {"max_speed": 5.0, "max_acceleration": 0.5, "max_deceleration": 1.0}
    limits[field] = invalid

    with pytest.raises(ValueError):
        limit_velocity(pg.Vector2(), pg.Vector2(5, 0), **limits)


@pytest.mark.parametrize("field", ["current_velocity", "desired_velocity"])
@pytest.mark.parametrize("component", [0, 1])
@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_limit_velocity_rejects_nonfinite_vectors(field, component, invalid):
    vectors = {"current_velocity": pg.Vector2(), "desired_velocity": pg.Vector2(5, 0)}
    vectors[field][component] = invalid

    with pytest.raises(ValueError):
        limit_velocity(**vectors, max_speed=5, max_acceleration=0.5, max_deceleration=1)


@pytest.mark.parametrize("acceleration, braking", [(0.5, 1), (5, 0.1), (0.1, 5)])
@pytest.mark.parametrize(
    "initial, requested", [((3, 4), (-4, 2)), ((5, 0), (0, 5)), ((5, 0), (-5, 0)), ((3, 4), (9, 4))]
)
def test_limit_velocity_shares_one_budget_for_braking_and_turning(
    initial, requested, acceleration, braking
):
    current = pg.Vector2(initial)
    desired = pg.Vector2(requested)
    result = limit_velocity(
        current, desired, max_speed=10, max_acceleration=acceleration, max_deceleration=braking
    )

    direction = current.normalize()
    change = result - current
    longitudinal = change.dot(direction)
    transverse = change - longitudinal * direction
    rate = braking if longitudinal < 0 else acceleration
    budget = (longitudinal / rate) ** 2 + (transverse.length() / acceleration) ** 2
    assert budget <= 1 + 1e-9
    assert change.length() <= max(acceleration, braking) + 1e-9
    assert result.length() <= 10 + 1e-9
    assert result.dot(direction) >= -1e-9
    assert result.distance_to(desired) < current.distance_to(desired)
    assert current == pg.Vector2(initial)
    assert desired == pg.Vector2(requested)


@pytest.mark.parametrize(
    "distance, expected_speed", [(0, 0), (5, 0), (10, 0), (20, 4), (25, 5), (100, 5)]
)
def test_arrival_velocity_requests_a_discrete_safe_approach_speed(distance, expected_speed):
    position = pg.Vector2()
    target = pg.Vector2(distance, 0)

    desired = arrival_velocity(position, target, max_speed=5, max_deceleration=1)

    assert tuple(desired) == pytest.approx((expected_speed, 0), abs=1e-9)
    assert position == pg.Vector2()
    assert target == pg.Vector2(distance, 0)
    assert desired is not position
    assert desired is not target


@pytest.mark.parametrize("offset", [(0, 0), (0.3, 0.4)])
def test_arrival_velocity_allows_zero_tolerance(offset):
    position = pg.Vector2(10, -20)
    desired = arrival_velocity(
        position, position + pg.Vector2(offset), max_speed=5, max_deceleration=1, tolerance=0
    )

    assert tuple(desired) == pytest.approx(offset, abs=1e-9)


@pytest.mark.parametrize(
    "field, invalid",
    [
        (field, invalid)
        for field in ("max_speed", "max_deceleration", "tolerance")
        for invalid in (-1, float("nan"), float("inf"), -float("inf"))
    ]
    + [("max_speed", 0), ("max_deceleration", 0)],
)
def test_arrival_velocity_rejects_invalid_limits_even_when_at_target(field, invalid):
    limits = {"max_speed": 5.0, "max_deceleration": 1.0, "tolerance": 10.0}
    limits[field] = invalid

    with pytest.raises(ValueError):
        arrival_velocity(pg.Vector2(), pg.Vector2(), **limits)


@pytest.mark.parametrize("field", ["position", "target"])
@pytest.mark.parametrize("component", [0, 1])
@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -float("inf")])
def test_arrival_velocity_rejects_nonfinite_positions(field, component, invalid):
    vectors = {"position": pg.Vector2(), "target": pg.Vector2(100, 0)}
    vectors[field][component] = invalid

    with pytest.raises(ValueError):
        arrival_velocity(vectors["position"], vectors["target"], max_speed=5, max_deceleration=1)


@pytest.mark.parametrize("acceleration, braking", [(0.5, 1), (0.1, 0.1), (0.1, 5), (5, 0.1)])
@pytest.mark.parametrize("max_speed", [1, 5, 50])
@pytest.mark.parametrize("distance", [20, 100, 1000])
@pytest.mark.parametrize("axis", [(1, 0), (0.6, 0.8), (-0.6, 0.8)])
def test_shared_motion_settles_without_oscillation_from_rest(
    acceleration, braking, max_speed, distance, axis
):
    direction = pg.Vector2(axis)
    position = pg.Vector2(37, -23)
    origin = position.copy()
    target = origin + distance * direction
    velocity = pg.Vector2()

    for _update in range(5000):
        desired = arrival_velocity(position, target, max_speed=max_speed, max_deceleration=braking)
        previous = velocity.copy()
        velocity = limit_velocity(
            previous,
            desired,
            max_speed=max_speed,
            max_acceleration=acceleration,
            max_deceleration=braking,
        )
        position += velocity
        assert (velocity - previous).length() <= max(acceleration, braking) + 1e-9
        assert velocity.length() <= max_speed + 1e-9
        assert velocity.dot(direction) >= -1e-9
        assert (position - origin).dot(direction) <= distance - 10 + 1e-9
        if position.distance_to(target) <= 10 + 1e-9 and velocity.length() <= 1e-9:
            break
    else:
        pytest.fail("Approach did not settle within the update budget")

    stopped_at = position.copy()
    for _update in range(5):
        desired = arrival_velocity(position, target, max_speed=max_speed, max_deceleration=braking)
        velocity = limit_velocity(
            velocity,
            desired,
            max_speed=max_speed,
            max_acceleration=acceleration,
            max_deceleration=braking,
        )
        position += velocity
        assert velocity.length() <= 1e-9
        assert position.distance_to(stopped_at) <= 1e-9


def test_shared_motion_brakes_inside_tolerance_without_position_correction():
    position = pg.Vector2()
    target = pg.Vector2(5, 0)
    velocity = pg.Vector2(5, 0)

    for speed in (4, 3, 2, 1, 0):
        desired = arrival_velocity(position, target, max_speed=5, max_deceleration=1)
        assert desired.length() == 0
        velocity = limit_velocity(
            velocity, desired, max_speed=5, max_acceleration=0.5, max_deceleration=1
        )
        previous_position = position.copy()
        position += velocity
        assert tuple(velocity) == pytest.approx((speed, 0))
        assert position == previous_position + velocity

    assert position == pg.Vector2(10, 0)
    assert position.x > target.x


# ---------------------------------------------------------------------------
# move_to (pure logic – no display required)
# ---------------------------------------------------------------------------


def test_move_to_far_target():
    """Returns new position and velocity when target is beyond tolerance"""
    curr_pos = pg.Vector2(0, 0)
    desired_pos = pg.Vector2(100, 0)
    new_pos, vel = move_to(curr_pos, desired_pos, desired_speed=10, tolerance=5)
    assert new_pos is not None
    assert new_pos == pg.Vector2(10, 0)
    assert vel == pg.Vector2(10, 0)


def test_move_to_within_tolerance():
    """Returns (None, zero vector) when target is within tolerance"""
    curr_pos = pg.Vector2(0, 0)
    desired_pos = pg.Vector2(5, 0)
    new_pos, vel = move_to(curr_pos, desired_pos, desired_speed=10, tolerance=10)
    assert new_pos is None
    assert vel == pg.Vector2(0, 0)


def test_move_to_exactly_at_tolerance():
    """Returns (None, zero vector) when distance equals tolerance (not strictly greater)"""
    curr_pos = pg.Vector2(0, 0)
    desired_pos = pg.Vector2(10, 0)  # distance == tolerance
    new_pos, vel = move_to(curr_pos, desired_pos, desired_speed=5, tolerance=10)
    assert new_pos is None
    assert vel == pg.Vector2(0, 0)


def test_move_to_same_position():
    """Returns (None, zero vector) when target equals current position"""
    curr_pos = pg.Vector2(50, 50)
    new_pos, vel = move_to(curr_pos, pg.Vector2(50, 50))
    assert new_pos is None
    assert vel == pg.Vector2(0, 0)


def test_move_to_diagonal():
    """Velocity is normalised to desired_speed in the correct direction"""
    curr_pos = pg.Vector2(0, 0)
    desired_pos = pg.Vector2(30, 40)  # distance = 50
    new_pos, vel = move_to(curr_pos, desired_pos, desired_speed=10, tolerance=5)
    assert new_pos is not None
    assert vel.x == pytest.approx(6.0)
    assert vel.y == pytest.approx(8.0)
    assert new_pos.x == pytest.approx(6.0)
    assert new_pos.y == pytest.approx(8.0)


def test_move_to_negative_direction():
    """Moves correctly toward a target in a negative direction"""
    curr_pos = pg.Vector2(100, 0)
    desired_pos = pg.Vector2(0, 0)
    new_pos, vel = move_to(curr_pos, desired_pos, desired_speed=10, tolerance=5)
    assert new_pos is not None
    assert vel == pg.Vector2(-10, 0)
    assert new_pos == pg.Vector2(90, 0)


def test_move_to_default_speed():
    """Default desired_speed is 10"""
    curr_pos = pg.Vector2(0, 0)
    desired_pos = pg.Vector2(100, 0)
    new_pos, vel = move_to(curr_pos, desired_pos)
    assert new_pos is not None
    assert vel == pg.Vector2(10, 0)


# ---------------------------------------------------------------------------
# Predator class (requires a display surface)
# ---------------------------------------------------------------------------


def test_predator_default_init(pygame_display):
    """Predator can be created with default arguments"""
    predator = Predator()
    assert predator.pos == pg.Vector2(0, 0)
    assert predator.vel == pg.Vector2(0, 0)
    assert predator.angle == 0


def test_predator_custom_init(pygame_display):
    """Predator stores the supplied position and velocity"""
    predator = Predator(pos=pg.Vector2(100, 200), vel=pg.Vector2(3, 4))
    assert predator.pos == pg.Vector2(100, 200)
    assert predator.vel == pg.Vector2(3, 4)


def test_predator_has_sprite_attributes(pygame_display):
    """Predator exposes the pygame Sprite interface"""
    predator = Predator(pos=pg.Vector2(50, 50))
    assert hasattr(predator, "image")
    assert hasattr(predator, "rect")


def test_predator_update_moves_toward_mouse(pygame_display):
    """Predator.update moves the predator toward the mouse position.

    With the dummy SDL driver the mouse is always at (0, 0). Starting the
    predator away from the origin ensures the 'move' branch is exercised.
    """
    predator = Predator(pos=pg.Vector2(400, 300))
    original_pos = pg.Vector2(predator.pos)
    predator.update()
    # prev_pos should be the position before the update
    assert predator.prev_pos == original_pos
    # The predator should have moved toward (0, 0)
    assert predator.pos != original_pos


def test_predator_update_no_move_when_at_mouse(pygame_display):
    """Predator.update does not move when already at the mouse position.

    With the dummy driver mouse is at (0, 0). A predator at the origin is
    within the default tolerance so pos should be unchanged.
    """
    predator = Predator(pos=pg.Vector2(0, 0))
    predator.update()
    assert predator.pos == pg.Vector2(0, 0)


def test_predator_update_moves_toward_explicit_target(pygame_display):
    """Predator.update accepts an explicit target position."""
    predator = Predator(pos=pg.Vector2(100, 100))

    predator.update(target_pos=pg.Vector2(200, 100))

    assert predator.pos == pg.Vector2(105, 100)
    assert predator.vel == pg.Vector2(5, 0)
