import pygame as pg
import pytest

from my_boids.boids import Boid
from my_boids.flock_rules import react_to_predator
from my_boids.predator import Predator


@pytest.fixture(name="test_boid")
def fixture_test_boid():
    """Return a test boid at position (100, 100)"""
    return Boid(
        pos=pg.Vector2(100, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )


@pytest.fixture(name="test_predator")
def fixture_test_predator(pygame_display):
    """Return a test predator at position (200, 100)"""
    return Predator(
        pos=pg.Vector2(200, 100),
        vel=pg.Vector2(0, 0),
    )


def test_avoid_mode_moves_boid_away(test_boid, test_predator):
    """Test that avoid mode moves the boid away from the predator"""
    initial_vel = test_boid.vel.copy()

    react_to_predator(
        test_boid,
        test_predator,
        behavior_mode="avoid",
        detection_range=400.0,
        reaction_strength=0.5,
    )

    # Boid should have moved in the opposite direction from predator
    # Since predator is at (200, 100) and boid at (100, 100),
    # boid should move in negative x direction
    assert test_boid.vel.x < initial_vel.x
    assert test_boid.vel.y == initial_vel.y  # No y component since they're aligned


def test_attract_mode_moves_boid_toward(test_boid, test_predator):
    """Test that attract mode moves the boid toward the predator"""
    initial_vel = test_boid.vel.copy()

    react_to_predator(
        test_boid,
        test_predator,
        behavior_mode="attract",
        detection_range=400.0,
        reaction_strength=0.5,
    )

    # Boid should have moved toward the predator
    # Since predator is at (200, 100) and boid at (100, 100),
    # boid should move in positive x direction
    assert test_boid.vel.x > initial_vel.x
    assert test_boid.vel.y == initial_vel.y  # No y component since they're aligned


def test_no_effect_beyond_detection_range(test_boid, test_predator):
    """Test that boid is not affected when predator is beyond detection range"""
    initial_vel = test_boid.vel.copy()

    # Distance between boid and predator is 100
    # Set detection range to less than that
    react_to_predator(
        test_boid,
        test_predator,
        behavior_mode="avoid",
        detection_range=50.0,  # Less than actual distance
        reaction_strength=0.5,
    )

    # Velocity should not have changed
    assert test_boid.vel == initial_vel


def test_force_stronger_when_closer():
    """Test that the reaction force is stronger when the predator is closer"""
    # Create two scenarios with different distances
    boid_close = Boid(
        pos=pg.Vector2(100, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )
    boid_far = Boid(
        pos=pg.Vector2(50, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )
    predator = Predator(
        pos=pg.Vector2(150, 100),
        vel=pg.Vector2(0, 0),
    )

    # Distance for boid_close: 50
    # Distance for boid_far: 100

    react_to_predator(
        boid_close,
        predator,
        behavior_mode="avoid",
        detection_range=400.0,
        reaction_strength=0.5,
    )

    react_to_predator(
        boid_far,
        predator,
        behavior_mode="avoid",
        detection_range=400.0,
        reaction_strength=0.5,
    )

    # Closer boid should have stronger force (larger velocity magnitude)
    assert boid_close.vel.magnitude() > boid_far.vel.magnitude()


def test_edge_case_same_position():
    """Test that function handles the edge case where boid and predator are at same position"""
    boid = Boid(
        pos=pg.Vector2(100, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )
    predator = Predator(
        pos=pg.Vector2(100, 100),  # Same as boid
        vel=pg.Vector2(0, 0),
    )

    # Should not crash or produce NaN values
    react_to_predator(
        boid,
        predator,
        behavior_mode="avoid",
        detection_range=400.0,
        reaction_strength=0.5,
    )

    # Velocity should have changed (function uses 0.1 as minimum distance)
    assert not (boid.vel.x == 0 and boid.vel.y == 0)
    # Should not have NaN values
    assert not (boid.vel.x != boid.vel.x or boid.vel.y != boid.vel.y)


def test_reaction_strength_scaling():
    """Test that reaction_strength parameter scales the force appropriately"""
    boid_weak = Boid(
        pos=pg.Vector2(100, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )
    boid_strong = Boid(
        pos=pg.Vector2(100, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )
    predator = Predator(
        pos=pg.Vector2(200, 100),
        vel=pg.Vector2(0, 0),
    )

    react_to_predator(
        boid_weak,
        predator,
        behavior_mode="avoid",
        detection_range=400.0,
        reaction_strength=0.1,
    )

    react_to_predator(
        boid_strong,
        predator,
        behavior_mode="avoid",
        detection_range=400.0,
        reaction_strength=1.0,
    )

    # Stronger reaction should result in larger velocity
    assert boid_strong.vel.magnitude() > boid_weak.vel.magnitude()
