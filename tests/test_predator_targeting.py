"""Focused tests for predator target selection helpers."""

import random
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
from my_boids.predator_targeting import (
    PredatorTargeter,
    find_target_in_range,
    resolve_predator_target,
)


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


SCREEN = (400, 300)
RANGE = 100.0


def _targeter(seed: int = 1) -> PredatorTargeter:
    return PredatorTargeter(SCREEN, random.Random(seed))


def _next(
    targeter: PredatorTargeter,
    boids: list[Boid],
    predator_pos: pg.Vector2,
    mode: PredatorAttackMode = PREDATOR_ATTACK_MODE_NEAREST,
    mouse_pos: pg.Vector2 | None = None,
) -> pg.Vector2:
    return targeter.next_target(
        mode, boids, predator_pos, pg.Vector2() if mouse_pos is None else mouse_pos, RANGE
    )


def _on_screen(point: pg.Vector2) -> bool:
    return 0 <= point.x <= SCREEN[0] and 0 <= point.y <= SCREEN[1]


def test_targeter_hunts_boid_in_range():
    targeter = _targeter()
    assert _next(targeter, [_make_boid(50, 0)], pg.Vector2()) == pg.Vector2(50, 0)


def test_targeter_heads_to_last_seen_position_after_losing_target():
    targeter = _targeter()
    boid = _make_boid(50, 0)
    _next(targeter, [boid], pg.Vector2())
    boid.pos = pg.Vector2(390, 290)

    assert _next(targeter, [boid], pg.Vector2(10, 0)) == pg.Vector2(50, 0)


def test_targeter_wanders_on_screen_after_reaching_last_seen_position():
    targeter = _targeter()
    _next(targeter, [_make_boid(50, 0)], pg.Vector2())

    target = _next(targeter, [], pg.Vector2(45, 0))

    assert target != pg.Vector2(50, 0)
    assert _on_screen(target)


def test_targeter_keeps_wander_point_until_reached_then_picks_new_one():
    targeter = _targeter()
    first = _next(targeter, [], pg.Vector2())
    assert _next(targeter, [], pg.Vector2()) == first

    second = _next(targeter, [], pg.Vector2(first))

    assert second != first
    assert _on_screen(second)


def test_targeter_starts_wandering_when_nothing_seen():
    target = _next(_targeter(), [], pg.Vector2())
    assert _on_screen(target)


def test_targeter_wander_is_deterministic_for_seed():
    assert _next(_targeter(7), [], pg.Vector2()) == _next(_targeter(7), [], pg.Vector2())


def test_targeter_reacquires_boid_while_searching_or_wandering():
    targeter = _targeter()
    _next(targeter, [_make_boid(50, 0)], pg.Vector2())
    _next(targeter, [], pg.Vector2(10, 0))
    assert _next(targeter, [_make_boid(20, 20)], pg.Vector2(10, 0)) == pg.Vector2(20, 20)

    _next(targeter, [], pg.Vector2(20, 20))
    assert _next(targeter, [_make_boid(30, 30)], pg.Vector2(20, 20)) == pg.Vector2(30, 30)


def test_targeter_reset_forgets_last_seen_position():
    targeter = _targeter()
    _next(targeter, [_make_boid(50, 0)], pg.Vector2())

    targeter.reset()

    assert _next(targeter, [], pg.Vector2(200, 0)) != pg.Vector2(50, 0)


def test_targeter_mouse_mode_passes_through_without_changing_state():
    targeter = _targeter()
    _next(targeter, [_make_boid(50, 0)], pg.Vector2())

    mouse_pos = pg.Vector2(390, 290)
    assert _next(targeter, [], pg.Vector2(), PREDATOR_ATTACK_MODE_MOUSE, mouse_pos) == mouse_pos
    assert _next(targeter, [], pg.Vector2(200, 0)) == pg.Vector2(50, 0)
