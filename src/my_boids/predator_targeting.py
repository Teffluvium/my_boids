"""Predator target selection strategies."""

import math
from collections.abc import Sequence

import pygame as pg

from my_boids.boids import Boid
from my_boids.options import (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_NEAREST,
    PredatorAttackMode,
)


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
    if mode not in (
        PREDATOR_ATTACK_MODE_CENTER,
        PREDATOR_ATTACK_MODE_NEAREST,
        PREDATOR_ATTACK_MODE_ISOLATED,
    ):
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
