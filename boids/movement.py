"""Movement functions and classes for the boids"""
from enum import Enum, auto

from boids.boids import Boid


class BoundaryType(Enum):
    """Enum for boid behavior when they hit the boundary"""

    BOUNCE = auto()
    WRAP = auto()


def move_boid(
    boid: Boid,
    boundary_type: BoundaryType,
    window_size: tuple[int, int],
):
    """Move the boid according to its velocity"""
    boid.move()

    # Select the boundary type
    if boundary_type == BoundaryType.WRAP:
        wrap_around_screen(boid, window_size)
    elif boundary_type == BoundaryType.BOUNCE:
        keep_within_bounds(boid, window_size)


def wrap_around_screen(boid: Boid, window_size: tuple[int, int]):
    """Make boids wrap around the screen"""
    boid.pos.update(
        boid.pos[0] % window_size[0],
        boid.pos[1] % window_size[1],
    )


def keep_within_bounds(boid: Boid, window_size: tuple[int, int]):
    """Keep boid within screen bounds"""
    margin = 30
    turn_factor = 1
    if boid.pos[0] < margin:
        boid.vel[0] += turn_factor
    elif boid.pos[0] > (window_size[0] - margin):
        boid.vel[0] -= turn_factor

    if boid.pos[1] < margin:
        boid.vel[1] += turn_factor
    elif boid.pos[1] > (window_size[1] - margin):
        boid.vel[1] -= turn_factor
