import pygame as pg
import pytest

from my_boids.boids import Boid
from my_boids.flock_rules import react_to_predator
from my_boids.options import PREDATOR_MODE_ATTRACT, PREDATOR_MODE_AVOID


@pytest.fixture(name="test_boid")
def fixture_test_boid():
    """Return a test boid at position (100, 100)"""
    return Boid(
        pos=pg.Vector2(100, 100),
        vel=pg.Vector2(0, 0),
        color=pg.Color(0, 0, 0),
        size=1,
    )


def test_avoid_mode_moves_boid_away(test_boid):
    """Test that avoid mode moves the boid away from the predator"""
    initial_vel = test_boid.vel.copy()
    predator_pos = pg.Vector2(200, 100)

    react_to_predator(
        test_boid,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=400.0,
        reaction_strength=0.5,
    )

    assert test_boid.vel.x < initial_vel.x
    assert test_boid.vel.y == initial_vel.y


def test_attract_mode_moves_boid_toward(test_boid):
    """Test that attract mode moves the boid toward the predator"""
    initial_vel = test_boid.vel.copy()
    predator_pos = pg.Vector2(200, 100)

    react_to_predator(
        test_boid,
        predator_pos,
        behavior_mode=PREDATOR_MODE_ATTRACT,
        detection_range=400.0,
        reaction_strength=0.5,
    )

    assert test_boid.vel.x > initial_vel.x
    assert test_boid.vel.y == initial_vel.y


def test_no_effect_beyond_detection_range(test_boid):
    """Test that boid is not affected when predator is beyond detection range"""
    initial_vel = test_boid.vel.copy()
    predator_pos = pg.Vector2(200, 100)

    react_to_predator(
        test_boid,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=50.0,
        reaction_strength=0.5,
    )

    assert test_boid.vel == initial_vel


def test_force_stronger_when_closer():
    """Test that the reaction force is stronger when the predator is closer"""
    boid_close = Boid(
        pos=pg.Vector2(100, 100), vel=pg.Vector2(0, 0), color=pg.Color(0, 0, 0), size=1
    )
    boid_far = Boid(pos=pg.Vector2(50, 100), vel=pg.Vector2(0, 0), color=pg.Color(0, 0, 0), size=1)
    predator_pos = pg.Vector2(150, 100)

    react_to_predator(
        boid_close,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=400.0,
        reaction_strength=0.5,
    )
    react_to_predator(
        boid_far,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=400.0,
        reaction_strength=0.5,
    )

    assert boid_close.vel.magnitude() > boid_far.vel.magnitude()


def test_edge_case_same_position():
    """Test that function handles the edge case where boid and predator are at same position"""
    boid = Boid(pos=pg.Vector2(100, 100), vel=pg.Vector2(0, 0), color=pg.Color(0, 0, 0), size=1)
    predator_pos = pg.Vector2(100, 100)

    react_to_predator(
        boid,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=400.0,
        reaction_strength=0.5,
    )

    assert not (boid.vel.x == 0 and boid.vel.y == 0)
    assert not (boid.vel.x != boid.vel.x or boid.vel.y != boid.vel.y)


def test_reaction_strength_scaling():
    """Test that reaction_strength parameter scales the force appropriately"""
    boid_weak = Boid(
        pos=pg.Vector2(100, 100), vel=pg.Vector2(0, 0), color=pg.Color(0, 0, 0), size=1
    )
    boid_strong = Boid(
        pos=pg.Vector2(100, 100), vel=pg.Vector2(0, 0), color=pg.Color(0, 0, 0), size=1
    )
    predator_pos = pg.Vector2(200, 100)

    react_to_predator(
        boid_weak,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=400.0,
        reaction_strength=0.1,
    )
    react_to_predator(
        boid_strong,
        predator_pos,
        behavior_mode=PREDATOR_MODE_AVOID,
        detection_range=400.0,
        reaction_strength=1.0,
    )

    assert boid_strong.vel.magnitude() > boid_weak.vel.magnitude()
