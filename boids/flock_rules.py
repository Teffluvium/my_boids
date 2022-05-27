from typing import List

import pygame as pg

from boids.boids import Boid

COHESION_FACTOR = 0.005
SEPARATION = 20
AVOID_FACTOR = 0.05
ALIGNMENT_FACTOR = 0.01
VISUAL_RANGE = 100


def cohesion(
    boid: Boid,
    boids: List[Boid],
    cohesion_factor: float = COHESION_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Move the boid towards the perceived center of mass of the flock"""
    num_boids = 0

    # Add contribution from each boid in the flock, as long as they are
    # within the visual range
    sum_positions = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid.pos.distance_to(boid.pos) < visual_range:
            sum_positions += other_boid.pos
            num_boids += 1

    # There should at least 2 boids, yourself and another boid
    if num_boids >= 2:
        # Subract the boid's own position contribution
        sum_positions -= boid.pos

        # Calculate the center of mass
        center_of_mass = sum_positions / (num_boids - 1)

        # Update the boid's velocity
        boid.vel += (center_of_mass - boid.pos) * cohesion_factor


def avoid_other_boids(
    boid: Boid,
    boids: List[Boid],
    separation: float = SEPARATION,
    avoid_factor: float = AVOID_FACTOR,
):
    """Avoid other boids that are too close"""
    delta = pg.Vector2(0, 0)
    for other_boid in boids:
        # Skip checking the boid itself
        if other_boid is boid:
            continue

        # Calculate the distance between the boids
        distance = boid.pos.distance_to(other_boid.pos)

        # If the distance is less than the minimum, apply the avoidance
        if distance < separation:
            # Calculate the vector to the other boid
            delta += boid.pos - other_boid.pos

    # Apply the vector to the boid
    boid.vel += delta * avoid_factor


def match_velocity(
    boid: Boid,
    boids: List[Boid],
    alignment_factor: float = ALIGNMENT_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Match the velocity of the boid with the velocity of the flock"""
    num_boids = 0

    # Calculate the average velocity of the flock, as long as they are
    # within the visual range
    sum_velocity = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid.pos.distance_to(boid.pos) < visual_range:
            sum_velocity += other_boid.vel
            num_boids += 1

    # There should at least 2 boids, yourself and another boid
    if num_boids >= 2:
        # Subract the boid's own velocity contribution
        sum_velocity -= boid.vel

        # Calculate the average velocity of other boids
        average_velocity = sum_velocity / (num_boids - 1)

        # Update the boid's velocity
        boid.vel += (average_velocity - boid.vel) * alignment_factor


def flock_rules(
    boid: Boid,
    boids: List[Boid],
    cohesion_factor: float = COHESION_FACTOR,
    separation: float = SEPARATION,
    avoid_factor: float = AVOID_FACTOR,
    alignment_factor: float = ALIGNMENT_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Apply all of the flock rules to the boid"""
    cohesion(boid, boids, cohesion_factor, visual_range)
    avoid_other_boids(boid, boids, separation, avoid_factor)
    match_velocity(boid, boids, alignment_factor, visual_range)
