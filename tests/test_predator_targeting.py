"""Focused tests for predator target selection helpers."""

import pygame as pg

from my_boids.boids import Boid
from my_boids.predator_targeting import (
    target_flock_center,
    target_most_isolated_bird,
    target_mouse_cursor,
    target_nearest_bird,
)


def _make_boid(x_pos: float, y_pos: float) -> Boid:
    return Boid(pos=pg.Vector2(x_pos, y_pos), vel=pg.Vector2(0, 0), color=pg.Color("white"), size=5)


def test_target_mouse_cursor_uses_current_mouse_position(monkeypatch):
    monkeypatch.setattr(pg.mouse, "get_pos", lambda: (123, 456))
    assert target_mouse_cursor() == pg.Vector2(123, 456)


def test_target_flock_center_returns_fallback_for_empty_flock():
    fallback = pg.Vector2(50, 25)
    assert target_flock_center([], fallback) == fallback


def test_target_flock_center_returns_centroid_for_multiple_boids():
    boids = [_make_boid(0, 0), _make_boid(6, 0), _make_boid(6, 6)]
    assert target_flock_center(boids, pg.Vector2(99, 99)) == pg.Vector2(4, 2)


def test_target_nearest_bird_returns_fallback_when_no_boids():
    fallback = pg.Vector2(10, 20)
    assert target_nearest_bird(pg.Vector2(0, 0), [], fallback) == fallback


def test_target_nearest_bird_returns_closest_boid_position():
    boids = [_make_boid(100, 100), _make_boid(7, 9), _make_boid(50, 50)]
    predator_pos = pg.Vector2(10, 10)
    assert target_nearest_bird(predator_pos, boids, pg.Vector2(0, 0)) == pg.Vector2(7, 9)


def test_target_most_isolated_bird_returns_fallback_for_empty_flock():
    fallback = pg.Vector2(5, 7)
    assert target_most_isolated_bird([], fallback) == fallback


def test_target_most_isolated_bird_returns_single_boid_when_only_one_exists():
    boids = [_make_boid(20, 30)]
    assert target_most_isolated_bird(boids, pg.Vector2(0, 0)) == pg.Vector2(20, 30)


def test_target_most_isolated_bird_returns_boid_with_largest_nearest_neighbor_gap():
    boids = [_make_boid(0, 0), _make_boid(2, 0), _make_boid(100, 100)]
    assert target_most_isolated_bird(boids, pg.Vector2(0, 0)) == pg.Vector2(100, 100)
