"""Tests for boids/predator.py"""

import pygame as pg
import pytest

from my_boids.predator import Predator, move_to

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
