"""Focused tests for predator target selection helpers."""

from typing import cast

import pygame as pg

from my_boids.boids import Boid
from my_boids.options import (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    PredatorAttackMode,
)
from my_boids.predator_targeting import find_target_in_range, resolve_predator_target


def _make_boid(x_pos: float, y_pos: float) -> Boid:
    return Boid(pos=pg.Vector2(x_pos, y_pos), vel=pg.Vector2(0, 0), color=pg.Color("white"), size=5)


def test_mouse_mode_returns_supplied_mouse_position():
    mouse_pos = pg.Vector2(123, 456)
    assert (
        resolve_predator_target(PREDATOR_ATTACK_MODE_MOUSE, [], pg.Vector2(0, 0), mouse_pos)
        == mouse_pos
    )


def test_center_mode_returns_predator_position_for_empty_flock():
    fallback = pg.Vector2(50, 25)
    assert (
        resolve_predator_target(PREDATOR_ATTACK_MODE_CENTER, [], fallback, pg.Vector2()) == fallback
    )


def test_center_mode_returns_flock_centroid():
    boids = [_make_boid(0, 0), _make_boid(6, 0), _make_boid(6, 6)]
    assert resolve_predator_target(
        PREDATOR_ATTACK_MODE_CENTER, boids, pg.Vector2(99, 99), pg.Vector2()
    ) == pg.Vector2(4, 2)


def test_nearest_mode_returns_predator_position_for_empty_flock():
    fallback = pg.Vector2(10, 20)
    assert (
        resolve_predator_target(PREDATOR_ATTACK_MODE_NEAREST, [], fallback, pg.Vector2())
        == fallback
    )


def test_nearest_mode_returns_closest_boid_position():
    boids = [_make_boid(100, 100), _make_boid(7, 9), _make_boid(50, 50)]
    predator_pos = pg.Vector2(10, 10)
    assert resolve_predator_target(
        PREDATOR_ATTACK_MODE_NEAREST, boids, predator_pos, pg.Vector2()
    ) == pg.Vector2(7, 9)


def test_isolated_mode_returns_predator_position_for_empty_flock():
    fallback = pg.Vector2(5, 7)
    assert (
        resolve_predator_target(PREDATOR_ATTACK_MODE_ISOLATED, [], fallback, pg.Vector2())
        == fallback
    )


def test_isolated_mode_returns_single_boid():
    boids = [_make_boid(20, 30)]
    assert resolve_predator_target(
        PREDATOR_ATTACK_MODE_ISOLATED, boids, pg.Vector2(), pg.Vector2()
    ) == pg.Vector2(20, 30)


def test_isolated_mode_returns_boid_with_largest_nearest_neighbor_gap():
    boids = [_make_boid(0, 0), _make_boid(2, 0), _make_boid(100, 100)]
    assert resolve_predator_target(
        PREDATOR_ATTACK_MODE_ISOLATED, boids, pg.Vector2(), pg.Vector2()
    ) == pg.Vector2(100, 100)


def test_unknown_mode_returns_supplied_mouse_position():
    unknown_mode = cast(PredatorAttackMode, "unknown")
    mouse_pos = pg.Vector2(123, 456)
    assert resolve_predator_target(unknown_mode, [], pg.Vector2(), mouse_pos) == mouse_pos


def test_nearest_mode_preserves_first_boid_on_distance_tie():
    first = _make_boid(-1, 0)
    second = _make_boid(1, 0)
    assert (
        resolve_predator_target(
            PREDATOR_ATTACK_MODE_NEAREST,
            [first, second],
            pg.Vector2(),
            pg.Vector2(),
        )
        == first.pos
    )


def test_find_in_range_mouse_mode_ignores_range():
    mouse_pos = pg.Vector2(900, 900)
    assert (
        find_target_in_range(PREDATOR_ATTACK_MODE_MOUSE, [], pg.Vector2(), mouse_pos, 10.0)
        == mouse_pos
    )


def test_find_in_range_nearest_skips_out_of_range_boids():
    boids = [_make_boid(500, 0), _make_boid(80, 0)]
    assert find_target_in_range(
        PREDATOR_ATTACK_MODE_NEAREST, boids, pg.Vector2(), pg.Vector2(), 100.0
    ) == pg.Vector2(80, 0)


def test_find_in_range_nearest_includes_boid_on_range_boundary():
    boids = [_make_boid(100, 0)]
    assert find_target_in_range(
        PREDATOR_ATTACK_MODE_NEAREST, boids, pg.Vector2(), pg.Vector2(), 100.0
    ) == pg.Vector2(100, 0)


def test_find_in_range_center_uses_only_in_range_boids():
    boids = [_make_boid(10, 0), _make_boid(30, 0), _make_boid(900, 900)]
    assert find_target_in_range(
        PREDATOR_ATTACK_MODE_CENTER, boids, pg.Vector2(), pg.Vector2(), 100.0
    ) == pg.Vector2(20, 0)


def test_find_in_range_isolated_measures_isolation_against_whole_flock():
    # (90, 0) looks alone among in-range boids but has a neighbour just outside range.
    near_pair = [_make_boid(0, 10), _make_boid(0, 30)]
    crowded = _make_boid(90, 0)
    neighbour_out_of_range = _make_boid(105, 0)
    boids = [*near_pair, crowded, neighbour_out_of_range]
    assert find_target_in_range(
        PREDATOR_ATTACK_MODE_ISOLATED, boids, pg.Vector2(), pg.Vector2(), 100.0
    ) == pg.Vector2(0, 10)


def test_find_in_range_isolated_single_boid_in_range():
    boids = [_make_boid(20, 0)]
    assert find_target_in_range(
        PREDATOR_ATTACK_MODE_ISOLATED, boids, pg.Vector2(), pg.Vector2(), 100.0
    ) == pg.Vector2(20, 0)


def test_find_in_range_returns_none_when_no_boids_in_range():
    boids = [_make_boid(500, 500)]
    for mode in (
        PREDATOR_ATTACK_MODE_NEAREST,
        PREDATOR_ATTACK_MODE_CENTER,
        PREDATOR_ATTACK_MODE_ISOLATED,
    ):
        assert find_target_in_range(mode, boids, pg.Vector2(), pg.Vector2(), 100.0) is None


def test_find_in_range_returns_none_for_empty_flock():
    assert (
        find_target_in_range(PREDATOR_ATTACK_MODE_NEAREST, [], pg.Vector2(), pg.Vector2(), 100.0)
        is None
    )
