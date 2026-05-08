"""Tests for boundary handling."""

import pygame as pg
import pytest

from my_boids.boid_vs_boundary import boid_vs_boundary, keep_within_bounds, wrap_around_screen
from my_boids.boids import Boid
from my_boids.options import BoundaryType


@pytest.fixture(name="window_size")
def fixture_window_size():
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
    boid = Boid(pos=pos)
    wrap_around_screen(boid, window_size=(10, 10))
    assert boid.pos == pg.Vector2(expected)


@pytest.mark.parametrize(
    "pos, vel, expected",
    [
        ((0, 0), (0, 0), (1, 1)),
        ((9, 9), (0, 0), (1, 1)),
        ((15, 15), (0, 0), (0, 0)),
        ((0, 30), (0, 0), (1, -1)),
        ((9, 21), (0, 0), (1, -1)),
        ((30, 0), (0, 0), (-1, 1)),
        ((21, 9), (0, 0), (-1, 1)),
        ((30, 30), (0, 0), (-1, -1)),
        ((21, 21), (0, 0), (-1, -1)),
    ],
)
def test_keep_within_bounds(pos, vel, expected):
    boid = Boid(pos=pos, vel=vel)
    keep_within_bounds(
        boid,
        window_size=(30, 30),
        margin=10,
        turn_factor=1,
    )
    assert boid.vel == pg.Vector2(expected)


def test_boid_vs_boundary_with_wrap():
    boid = Boid(pos=(14, 14))
    boid_vs_boundary(boid, BoundaryType.WRAP, (10, 10))
    assert boid.pos == pg.Vector2(4, 4)


def test_boid_vs_boundary_with_bounce():
    boid = Boid(pos=(21, 21))
    boid_vs_boundary(
        boid,
        BoundaryType.BOUNCE,
        window_size=(30, 30),
        margin=10,
        turn_factor=1,
    )
    assert boid.vel == pg.Vector2(-1, -1)
