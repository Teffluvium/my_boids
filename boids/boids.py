"""
Create a boid and define its movement rules
"""
from dataclasses import dataclass

import numpy as np
import pygame as pg

rng = np.random.default_rng()

# Boid Constants
SIZE = 10
MAX_SPEED = 3
COHESION_FACTOR = 0.001
SEPARATION = 20
AVOID_FACTOR = 0.01
ALIGNMENT_FACTOR = 0.01
VISUAL_RANGE = 100


@dataclass
class Boid:
    """A single boid in the flock"""

    pos: pg.Vector2 = pg.Vector2(0, 0)
    vel: pg.Vector2 = pg.Vector2(0, 0)
    color: pg.Color = pg.Color(255, 255, 255)
    size: int = SIZE

    def __post_init__(self):
        """Validate parameters"""
        # Ensure that position and velocity are Vector2 objects
        if not isinstance(self.pos, pg.Vector2):
            self.pos = pg.Vector2(self.pos)
        if not isinstance(self.vel, pg.Vector2):
            self.vel = pg.Vector2(self.vel)

        # Ensure color is a tuple and has 3 or 4 elements
        if self.color is not pg.Color:
            self.color = pg.Color(self.color)

        # Check size is a positive
        if self.size < 0:
            raise ValueError("Size cannot be negative")

    def move(self):
        """Move the boid"""
        # Update the position relative to the velocity
        self.pos += self.vel  # type: ignore

    def __str__(self):
        return ", ".join(
            [
                f"Boid(pos={self.pos}",
                f"vel={self.vel}",
                f"color={self.color}",
                f"size={self.size})",
            ]
        )

    def cohesion(
        self,
        boids: list,
        cohesion_factor: float = COHESION_FACTOR,
        visual_range: float = VISUAL_RANGE,
    ):
        """Move the boid towards the perceived center of mass of the flock"""
        num_boids = 0

        # Add contribution from each boid in the flock, as long as they are
        # within the visual range
        sum_positions = pg.Vector2(0, 0)
        for boid in boids:
            if boid.pos.distance_to(self.pos) < visual_range:
                sum_positions += boid.pos
                num_boids += 1

        # There should at least 2 boids, yourself and another boid
        if num_boids >= 2:
            # Subract the boid's own position contribution
            sum_positions -= self.pos

            # Calculate the center of mass
            center_of_mass = sum_positions / (num_boids - 1)

            # Update the boid's velocity
            self.vel += (center_of_mass - self.pos) * cohesion_factor  # type: ignore

    def avoid_other_boids(
        self,
        boids: list,
        separation: float = SEPARATION,
        avoid_factor: float = AVOID_FACTOR,
    ):
        """Avoid other boids that are too close"""
        delta = pg.Vector2(0, 0)
        for other_boid in boids:
            # Skip checking the boid itself
            if other_boid is self:
                continue

            # Calculate the distance between the boids
            distance = self.pos.distance_to(other_boid.pos)

            # If the distance is less than the minimum, apply the avoidance
            if distance < separation:
                # Calculate the vector to the other boid
                delta += self.pos - other_boid.pos

        # Apply the vector to the boid
        self.vel += delta * avoid_factor

    def match_velocity(
        self,
        boids: list,
        alignment_factor: float = ALIGNMENT_FACTOR,
        visual_range: float = VISUAL_RANGE,
    ):
        """Match the velocity of the boid with the velocity of the flock"""
        num_boids = 0

        # Calculate the average velocity of the flock, as long as they are
        # within the visual range
        sum_velocity = pg.Vector2(0, 0)
        for boid in boids:
            if boid.pos.distance_to(self.pos) < visual_range:
                sum_velocity += boid.vel
                num_boids += 1

        # There should at least 2 boids, yourself and another boid
        if num_boids >= 2:
            # Subract the boid's own velocity contribution
            sum_velocity -= self.vel

            # Calculate the average velocity of other boids
            average_velocity = sum_velocity / (num_boids - 1)

            # Update the boid's velocity
            self.vel += (average_velocity - self.vel) * alignment_factor  # type: ignore

    def speed_limit(self, max_speed: float = MAX_SPEED):
        """Limit the speed of the boid"""
        speed = self.vel.magnitude()
        # Apply a speed limit
        if speed > max_speed:
            self.vel.scale_to_length(max_speed)


if __name__ == "__main__":
    """The Main"""
    print("Boids")
