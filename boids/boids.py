"""
Create a boid and define its movement rules
"""
from dataclasses import dataclass
from typing import Tuple

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
        if self.pos is not pg.Vector2:
            self.pos = pg.Vector2(self.pos)
        if self.vel is not pg.Vector2:
            self.vel = pg.Vector2(self.vel)

        # Ensure color is a tuple and has 3 or 4 elements
        if len(self.color) not in [3, 4]:
            raise ValueError("Color must be a tuple of 3 or 4elements")
        if self.color is not pg.Color:
            try:
                self.color = pg.Color(self.color)
            except TypeError as err:
                raise TypeError("Color must be a tuple of 3 elements") from err

        # Ensure color is bounded between 0 and 255
        if any(self.color) < 0:
            raise ValueError("Color values cannot be negative")
        if any(self.color) > 255:
            raise ValueError("Color values cannot be greater than 255")
        if self.size < 0:
            raise ValueError("Size cannot be negative")

    def move(self):
        """Move the boid"""
        # Update the position relative to the velocity
        self.pos += self.vel

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
    ):
        """Move the boid towards the perceived center of mass of the flock"""
        num_boids = len(boids)

        # Calculate the center of mass
        sum_of_x = sum(b.pos[0] for b in boids)
        sum_of_y = sum(b.pos[1] for b in boids)

        # Subtract the boid's own position contribution
        sum_of_x -= self.pos[0]
        sum_of_y -= self.pos[1]
        center_of_mass = pg.Vector2(
            sum_of_x / (num_boids - 1),
            sum_of_y / (num_boids - 1),
        )

        # Update the boid's velocity
        self.vel += (center_of_mass - self.pos) * cohesion_factor

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
    ):
        """Match the velocity of the boid with the velocity of the flock"""
        num_boids = len(boids)

        # Calculate the average velocity of the flock
        sum_of_x = sum(b.vel[0] for b in boids)
        sum_of_y = sum(b.vel[1] for b in boids)

        # Subtract the boid's own velocity contribution
        sum_of_x -= self.vel[0]
        sum_of_y -= self.vel[1]

        average_velocity = pg.Vector2(
            sum_of_x / (num_boids - 1),
            sum_of_y / (num_boids - 1),
        )

        # Update the boid's velocity
        self.vel += average_velocity * alignment_factor

    def speed_limit(self, max_speed: float = MAX_SPEED):
        """Limit the speed of the boid"""
        speed = self.vel.magnitude()
        # Apply a speed limit
        if speed > max_speed:
            self.vel *= max_speed / speed


if __name__ == "__main__":
    pass
    # a = Boid(pos=pg.Vector2(0, 0), vel=pg.Vector2(1, 1), color=(0, 0, 0), size=1)
    # b = Boid(pos=pg.Vector2(0, 1), vel=pg.Vector2(1, 1), color=(0, 0, 0), size=1)

    # print(a == b)
    # print(f"{a = }")
    # print(type(a.pos))
    # print(a.pos.distance_to(b.pos))

    # c = pg.Vector2(1, 1)
    # print(f"{c = }")
    # print(type(c))

    # d = pg.Vector2(c)
    # print(f"{d = }")
