"""Predator target selection strategies."""

import math
import random
from collections.abc import Sequence

import pygame as pg

from my_boids.boids import Boid
from my_boids.options import (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_NEAREST,
    PredatorAttackMode,
)

_RANGED_MODES: tuple[PredatorAttackMode, ...] = (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_NEAREST,
    PREDATOR_ATTACK_MODE_ISOLATED,
)
# Matches move_to's default tolerance so arrival agrees with when the predator stops.
ARRIVAL_TOLERANCE = 10.0


class PredatorTargeter:
    """Choose predator targets: hunt in range, search the last-seen spot, then wander."""

    def __init__(self, screen_size: tuple[int, int], rng: random.Random | None = None) -> None:
        self._screen_size = screen_size
        self._rng = random.Random() if rng is None else rng
        self._last_seen: pg.Vector2 | None = None
        self._wander_point: pg.Vector2 | None = None

    def next_target(
        self,
        mode: PredatorAttackMode,
        boids: Sequence[Boid],
        predator_pos: pg.Vector2,
        mouse_pos: pg.Vector2,
        detection_range: float,
    ) -> pg.Vector2:
        if mode not in _RANGED_MODES:
            return pg.Vector2(mouse_pos)

        target = find_target_in_range(mode, boids, predator_pos, mouse_pos, detection_range)
        if target is not None:
            self._last_seen = pg.Vector2(target)
            self._wander_point = None
            return target

        if self._last_seen is not None:
            if predator_pos.distance_to(self._last_seen) > ARRIVAL_TOLERANCE:
                return pg.Vector2(self._last_seen)
            self._last_seen = None

        if (
            self._wander_point is None
            or predator_pos.distance_to(self._wander_point) <= ARRIVAL_TOLERANCE
        ):
            self._wander_point = pg.Vector2(
                self._rng.uniform(0, self._screen_size[0]),
                self._rng.uniform(0, self._screen_size[1]),
            )
        return pg.Vector2(self._wander_point)

    def reset(self) -> None:
        self._last_seen = None
        self._wander_point = None


def resolve_predator_target(
    mode: PredatorAttackMode,
    boids: Sequence[Boid],
    predator_pos: pg.Vector2,
    mouse_pos: pg.Vector2,
) -> pg.Vector2:
    """Resolve a predator target from the current mode and simulation inputs."""
    target = find_target_in_range(mode, boids, predator_pos, mouse_pos, math.inf)
    return pg.Vector2(predator_pos) if target is None else target


def find_target_in_range(
    mode: PredatorAttackMode,
    boids: Sequence[Boid],
    predator_pos: pg.Vector2,
    mouse_pos: pg.Vector2,
    detection_range: float,
) -> pg.Vector2 | None:
    """Return the mode's target among boids within range, or None if none are in range."""
    if mode not in _RANGED_MODES:
        return pg.Vector2(mouse_pos)

    in_range = [boid for boid in boids if predator_pos.distance_to(boid.pos) <= detection_range]
    if not in_range:
        return None
    if mode == PREDATOR_ATTACK_MODE_CENTER:
        return _target_flock_center(in_range)
    if mode == PREDATOR_ATTACK_MODE_NEAREST:
        return _target_nearest_bird(predator_pos, in_range)
    return _target_most_isolated_bird(in_range, boids)


def _target_flock_center(boids: Sequence[Boid]) -> pg.Vector2:
    total = pg.Vector2(0, 0)
    for boid in boids:
        total += boid.pos
    return total / len(boids)


def _target_nearest_bird(predator_pos: pg.Vector2, boids: Sequence[Boid]) -> pg.Vector2:
    nearest_boid = min(boids, key=lambda boid: predator_pos.distance_to(boid.pos))
    return pg.Vector2(nearest_boid.pos)


def _target_most_isolated_bird(candidates: Sequence[Boid], flock: Sequence[Boid]) -> pg.Vector2:
    """Pick the candidate whose nearest neighbour in the whole flock is farthest away."""

    def nearest_neighbor_distance(target_boid: Boid) -> float:
        return min(
            (
                target_boid.pos.distance_to(other_boid.pos)
                for other_boid in flock
                if other_boid is not target_boid
            ),
            default=math.inf,
        )

    isolated_boid = max(candidates, key=nearest_neighbor_distance)
    return pg.Vector2(isolated_boid.pos)
