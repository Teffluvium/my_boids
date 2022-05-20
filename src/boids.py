"""
Create a boid and define its movement rules
"""
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from pygame.math import Vector2  # pylint: disable=no-name-in-module

rng = np.random.default_rng()

# Boid Constants
SIZE = 5
MAX_SPEED = 3
VELOCITY_FACTOR = 0.001  # How much to update the boid's velocity
MIN_DISTANCE = 20
AVOID_FACTOR = 0.01
MATCHING_FACTOR = 0.01


@dataclass
class Boid:
    """A single boid in the flock"""

    position: Vector2 = Vector2(0, 0)
    velocity: Vector2 = Vector2(0, 0)
    color: Tuple[int, int, int] = (255, 0, 0)
    size: int = SIZE

    @property
    def angle(self):
        """Calculate the angle of the boid"""
        return np.rad2deg(np.arctan2(self.velocity[1], self.velocity[0]))

    def move(self):
        """Move the boid"""
        # Update the position relative to the velocity
        self.position += self.velocity

    def __str__(self):
        return ", ".join(
            [
                f"Boid({self.position=}",
                f"{self.velocity=}",
                f"{self.color=}",
                f"{self.size=})",
            ]
        )

    def fly_to_center_of_mass(
        self, boids: list, velocity_factor: float = VELOCITY_FACTOR
    ):
        """Move the boid towards the perceived center of mass of the flock"""
        num_boids = len(boids)

        # Calculate the center of mass
        sum_of_x = sum(b.position[0] for b in boids)
        sum_of_x -= self.position[0]
        sum_of_y = sum(b.position[1] for b in boids)
        sum_of_y -= self.position[1]
        center_of_mass = Vector2(sum_of_x / (num_boids - 1), sum_of_y / (num_boids - 1))

        delta = (center_of_mass - self.position) * velocity_factor

        # Update the boid's velocity
        self.velocity += delta

    def avoid_other_boids(
        self, boids: list, min_distance: float = 20, avoid_factor: float = AVOID_FACTOR
    ):
        """Avoid other boids that are too close"""
        delta = Vector2(0, 0)
        for other_boid in boids:
            # Skip checking the boid itself
            if other_boid is self:
                continue

            # Calculate the distance between the boids
            distance = self.position.distance_to(other_boid.position)

            # If the distance is less than the minimum, apply the avoidance
            if distance < min_distance:
                # Calculate the vector to the other boid
                delta += self.position - other_boid.position

            # Apply the vector to the boid
            self.velocity += delta * avoid_factor

    def match_velocity(self, boids: list, matching_factor: float = MATCHING_FACTOR):
        """Match the velocity of the boid with the velocity of the flock"""
        num_boids = len(boids)

        # Calculate the average velocity of the flock
        sum_of_x = sum(b.velocity[0] for b in boids)
        sum_of_x -= self.velocity[0]
        sum_of_y = sum(b.velocity[1] for b in boids)
        sum_of_y -= self.velocity[1]
        average_velocity = Vector2(
            sum_of_x / (num_boids - 1), sum_of_y / (num_boids - 1)
        )

        # Update the boid's velocity
        self.velocity += average_velocity * matching_factor

    def speed_limit(self, max_speed: float = MAX_SPEED):
        """Limit the speed of the boid"""
        speed = self.velocity.magnitude()
        # Apply a speed limit
        if speed > max_speed:
            self.velocity *= max_speed / speed


if __name__ == "__main__":
    a = Boid(position=Vector2(0, 0), velocity=Vector2(1, 1), color=(0, 0, 0), size=1)
    b = Boid(position=Vector2(0, 1), velocity=Vector2(1, 1), color=(0, 0, 0), size=1)

    print(a == b)
    print(f"{a = }")
    print(type(a.position))
    print(a.position.distance_to(b.position))

    c = Vector2(1, 1)
    print(f"{c = }")
    print(type(c))

    d = Vector2(c)
    print(f"{d = }")
