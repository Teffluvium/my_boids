"""Test the Boids class"""
import pygame as pg
import pytest
from boids.boids import Boid
from boids.movement import wrap_around_screen


@pytest.fixture(name="window_size")
def fixture_window_size():
    """Return a window size"""
    return (800, 600)


@pytest.mark.parametrize(
    "pos, expected",
    [
        ((14, 0), (4, 0)),
        ((0, 14), (0, 4)),
        ((14, 14), (4, 4)),
        ((-1, 0), (9, 0)),
        ((0, -1), (0, 9)),
        ((-1, -1), (9, 9)),
        ((5, 5), (5, 5)),
    ],
)
def test_wrap_around_screen(pos, expected):
    """Make boids wrap around the screen"""
    boid = Boid(pos=pos)
    wrap_around_screen(boid, window_size=(10, 10))
    assert boid.pos == pg.Vector2(expected)
