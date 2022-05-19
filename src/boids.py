from dataclasses import dataclass
from typing import Tuple

from math import cos, sin, radians, degrees, atan2, sqrt
import numpy as np

rng = np.random.default_rng()

@dataclass
class Boid:
    """A single boid in the flock"""
    position: Tuple[int, int] = (0, 0)
    velocity: Tuple[int, int] = (0, 0)
    color: Tuple[int, int, int] = (255, 0, 0)
    size: int = 1

    @property
    def angle(self):
        """Calculate the angle of the boid"""
        return np.rad2deg(np.arctan2(self.velocity[1], self.velocity[0]))

    @property
    def speed(self):
        """Calculate the speed of the boid"""
        return sqrt(
            sum(v ** 2 for v in self.velocity)
        )

    def move(self):
        """Move the boid"""
        # Update the position relative to the velocity
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1],
        )

    def __str__(self):
        return ", ".join(
            [
                f"Boid({self.position=}",
                f"{self.velocity=}",
                f"{self.color=}",
                f"{self.size=})",
            ]
        )

if __name__     == "__main__":
    a = Boid(position=(0, 0), velocity=(1, 1), color=(0, 0, 0), size=1)
    b = Boid(position=(0, 0), velocity=(1, 1), color=(0, 0, 0), size=1)
    
    print(a == b)