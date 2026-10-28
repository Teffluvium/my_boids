"""Predator target selection strategies."""

from collections.abc import Sequence

import pygame as pg

from my_boids.boids import Boid
from my_boids.options import (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_MOUSE,
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
    if mode == PREDATOR_ATTACK_MODE_MOUSE:
        return pg.Vector2(mouse_pos)
    if mode == PREDATOR_ATTACK_MODE_CENTER:
        return _target_flock_center(boids, predator_pos)
    if mode == PREDATOR_ATTACK_MODE_NEAREST:
        return _target_nearest_bird(predator_pos, boids, predator_pos)
    if mode == PREDATOR_ATTACK_MODE_ISOLATED:
        return _target_most_isolated_bird(boids, predator_pos)
    return pg.Vector2(mouse_pos)


def _target_flock_center(boids: Sequence[Boid], fallback: pg.Vector2) -> pg.Vector2:
    """Target the flock centroid, or fallback when no boids remain."""
    if not boids:
        return pg.Vector2(fallback)

    total = pg.Vector2(0, 0)
    for boid in boids:
        total += boid.pos
    return total / len(boids)


def _target_nearest_bird(
    predator_pos: pg.Vector2,
    boids: Sequence[Boid],
    fallback: pg.Vector2,
) -> pg.Vector2:
    """Target the nearest boid, or fallback when no boids remain."""
    if not boids:
        return pg.Vector2(fallback)

    nearest_boid = min(boids, key=lambda boid: predator_pos.distance_to(boid.pos))
    return pg.Vector2(nearest_boid.pos)


def _target_most_isolated_bird(boids: Sequence[Boid], fallback: pg.Vector2) -> pg.Vector2:
    """Target the boid with the largest nearest-neighbor distance."""
    if not boids:
        return pg.Vector2(fallback)
    if len(boids) == 1:
        return pg.Vector2(boids[0].pos)

    def nearest_neighbor_distance(target_boid: Boid) -> float:
        return min(
            target_boid.pos.distance_to(other_boid.pos)
            for other_boid in boids
            if other_boid is not target_boid
        )

    isolated_boid = max(boids, key=nearest_neighbor_distance)
    return pg.Vector2(isolated_boid.pos)
