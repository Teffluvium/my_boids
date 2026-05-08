"""Define rules for boid behavior in a flock."""

import random

import pygame as pg

from my_boids.boids import Boid
from my_boids.options import PREDATOR_MODE_AVOID, PredatorBehaviorMode

COHESION_FACTOR = 0.005
SEPARATION = 20
AVOID_FACTOR = 0.05
ALIGNMENT_FACTOR = 0.01
VISUAL_RANGE = 100


def cohesion(
    boid: Boid,
    boids: list[Boid],
    cohesion_factor: float = COHESION_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Move the boid towards the perceived center of mass of the flock."""
    num_boids = 0
    sum_positions = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid.pos.distance_to(boid.pos) < visual_range:
            sum_positions += other_boid.pos
            num_boids += 1

    if num_boids >= 2:
        sum_positions -= boid.pos
        center_of_mass = sum_positions / (num_boids - 1)
        boid.vel += (center_of_mass - boid.pos) * cohesion_factor


def avoid_other_boids(
    boid: Boid,
    boids: list[Boid],
    separation: float = SEPARATION,
    avoid_factor: float = AVOID_FACTOR,
):
    """Avoid other boids that are too close."""
    delta = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid is boid:
            continue
        distance = boid.pos.distance_to(other_boid.pos)
        if distance < separation:
            delta += boid.pos - other_boid.pos
    boid.vel += delta * avoid_factor


def match_velocity(
    boid: Boid,
    boids: list[Boid],
    alignment_factor: float = ALIGNMENT_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Match the velocity of the boid with the velocity of the flock."""
    num_boids = 0
    sum_velocity = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid.pos.distance_to(boid.pos) < visual_range:
            sum_velocity += other_boid.vel
            num_boids += 1

    if num_boids >= 2:
        sum_velocity -= boid.vel
        average_velocity = sum_velocity / (num_boids - 1)
        boid.vel += (average_velocity - boid.vel) * alignment_factor


def flock_rules(
    boid: Boid,
    boids: list[Boid],
    cohesion_factor: float = COHESION_FACTOR,
    separation: float = SEPARATION,
    avoid_factor: float = AVOID_FACTOR,
    alignment_factor: float = ALIGNMENT_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Apply all flocking rules to the boid."""
    cohesion(boid, boids, cohesion_factor, visual_range)
    avoid_other_boids(boid, boids, separation, avoid_factor)
    match_velocity(boid, boids, alignment_factor, visual_range)


def react_to_predator(
    boid: Boid,
    predator_pos: pg.Vector2,
    behavior_mode: PredatorBehaviorMode,
    detection_range: float,
    reaction_strength: float,
):
    """Update a boid's velocity based on predator position."""
    distance = boid.pos.distance_to(predator_pos)
    if distance > detection_range:
        return

    if distance < 0.1:
        angle = random.uniform(0, 2 * 3.14159)
        direction = pg.Vector2(1, 0).rotate_rad(angle)
        boid.vel += direction * reaction_strength
        return

    if behavior_mode == PREDATOR_MODE_AVOID:
        direction = (boid.pos - predator_pos).normalize()
    else:
        direction = (predator_pos - boid.pos).normalize()

    force_magnitude = reaction_strength / (distance + 1) ** 2
    boid.vel += direction * force_magnitude
