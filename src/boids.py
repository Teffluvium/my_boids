from dataclasses import dataclass
from math import sqrt
from typing import Tuple

import numpy as np
from pygame.math import Vector2

rng = np.random.default_rng()


@dataclass
class Boid:
    """A single boid in the flock"""

    position: Vector2 = Vector2(0, 0)
    velocity: Vector2 = Vector2(0, 0)
    color: Tuple[int, int, int] = (255, 0, 0)
    size: int = 1

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


if __name__ == "__main__":
    a = Boid(position=Vector2(0, 0), velocity=(1, 1), color=(0, 0, 0), size=1)
    b = Boid(position=Vector2(0, 1), velocity=(1, 1), color=(0, 0, 0), size=1)

    print(a == b)
    print(f"{a = }")
    print(type(a.position))
    print(a.position.distance_to(b.position))

    c = Vector2(1, 1)
    print(f"{c = }")
    print(type(c))

    d = Vector2(c)
    print(f"{d = }")
