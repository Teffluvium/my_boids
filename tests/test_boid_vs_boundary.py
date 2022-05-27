"""Test the Boids class"""
import pygame as pg
import pytest
from boids.boid_vs_boundary import (
    BoundaryType,
    boid_vs_boundary,
    keep_within_bounds,
    wrap_around_screen,
)
from boids.boids import Boid


@pytest.fixture(name="window_size")
def fixture_window_size():
    """Return a window size"""
    return (800, 600)


@pytest.mark.parametrize(
    "pos, expected",
    [
        ((14, 0), (4, 0)),  # Bottom right -> bottom left
        ((0, 14), (0, 4)),  # Top left -> bottom left
        ((14, 14), (4, 4)),  # Top right -> bottom left
        ((-1, 0), (9, 0)),  # Bottom left -> bottom right
        ((0, -1), (0, 9)),  # Bottom left -> top left
        ((-1, -1), (9, 9)),  # Bottom left -> top right
        ((5, 5), (5, 5)),  # Center -> center
    ],
)
def test_wrap_around_screen(pos, expected):
    """Make boids wrap around the screen"""
    boid = Boid(pos=pos)
    wrap_around_screen(boid, window_size=(10, 10))
    assert boid.pos == pg.Vector2(expected)


@pytest.mark.parametrize(
    "pos, vel, expected",
    [
        ((0, 0), (0, 0), (1, 1)),  # Bottom left corner
        ((9, 9), (0, 0), (1, 1)),  # Bottom left margin
        ((15, 15), (0, 0), (0, 0)),  # Center
        ((0, 30), (0, 0), (1, -1)),  # Top left corner
        ((9, 21), (0, 0), (1, -1)),  # Top left margin
        ((30, 0), (0, 0), (-1, 1)),  # Bottom right corner
        ((21, 9), (0, 0), (-1, 1)),  # Bottom right margin
        ((30, 30), (0, 0), (-1, -1)),  # Top right corner
        ((21, 21), (0, 0), (-1, -1)),  # Top right margin
    ],
)
def test_keep_within_bounds(pos, vel, expected):
    """Make boids wrap around the screen"""
    boid = Boid(pos=pos, vel=vel)
    print(f"orig: {boid.pos} {boid.vel}")
    keep_within_bounds(
        boid,
        window_size=(30, 30),
        margin=10,
        turn_factor=1,
    )
    print(f"new:  {boid.pos} {boid.vel}")
    assert boid.vel == pg.Vector2(expected)


def test_boid_vs_boundary_with_wrap():
    """Move a boid with wrap around"""
    boid = Boid(pos=(14, 14))  # Top right corner outside of the window
    boundary_type = BoundaryType.WRAP
    window_size = (10, 10)

    boid_vs_boundary(boid, boundary_type, window_size)
    # Position shold get wrapped to the bottom left
    assert boid.pos == pg.Vector2(4, 4)


def test_boid_vs_boundary_with_bounce():
    """Move a boid with bounce"""
    boid = Boid(pos=(21, 21))  # Top right corner inside of the margin
    boundary_type = BoundaryType.BOUNCE

    boid_vs_boundary(
        boid,
        boundary_type,
        window_size=(30, 30),
        margin=10,
        turn_factor=1,
    )
    # Velocity should point to the south west
    assert boid.vel == pg.Vector2(-1, -1)
