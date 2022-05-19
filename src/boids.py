from dataclasses import dataclass
from typing import Tuple


@dataclass
class Boid:
    """A single boid in the flock"""
    position: Tuple[int, int] = (0, 0)
    speed: float = 5
    direction: float = 0
    color: Tuple[int, int, int] = (255, 0, 0)
    size: int = 1

    def __str__(self):
        return ", ".join(
            [
                f"Boid({self.position=}",
                f"{self.direction=:.2f}",
                f"{self.speed=:.2f}",
                f"{self.color=}",
                f"{self.size=})",
            ]
        )
