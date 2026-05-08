"""Predator target selection strategies."""

import pygame as pg

from my_boids.boids import Boid


def target_mouse_cursor() -> pg.Vector2:
    """Target the current mouse cursor position."""
    return pg.Vector2(pg.mouse.get_pos())


def target_flock_center(boids: list[Boid], fallback: pg.Vector2) -> pg.Vector2:
    """Target the flock centroid, or fallback when no boids remain."""
    if not boids:
        return pg.Vector2(fallback)

    total = pg.Vector2(0, 0)
    for boid in boids:
        total += boid.pos
    return total / len(boids)


def target_nearest_bird(
    predator_pos: pg.Vector2,
    boids: list[Boid],
    fallback: pg.Vector2,
) -> pg.Vector2:
    """Target the boid nearest to the predator, or fallback when no boids remain."""
    if not boids:
        return pg.Vector2(fallback)

    nearest_boid = min(boids, key=lambda boid: predator_pos.distance_to(boid.pos))
    return pg.Vector2(nearest_boid.pos)


def target_most_isolated_bird(boids: list[Boid], fallback: pg.Vector2) -> pg.Vector2:
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
