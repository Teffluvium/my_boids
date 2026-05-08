"""Movement functions and classes for the boids."""

from my_boids.boids import Boid
from my_boids.options import BoundaryType


def boid_vs_boundary(
    boid: Boid,
    boundary_type: BoundaryType,
    window_size: tuple[int, int],
    margin: int = 30,
    turn_factor: float = 1,
) -> None:
    """Adjust boid position or velocity based on configured boundary behavior."""
    if boundary_type == BoundaryType.WRAP:
        wrap_around_screen(boid, window_size)
    elif boundary_type == BoundaryType.BOUNCE:
        keep_within_bounds(
            boid,
            window_size,
            margin=margin,
            turn_factor=turn_factor,
        )


def wrap_around_screen(boid: Boid, window_size: tuple[int, int]) -> None:
    """Wrap boid around to opposite side of the window."""
    boid.pos.update(
        boid.pos[0] % window_size[0],
        boid.pos[1] % window_size[1],
    )


def keep_within_bounds(
    boid: Boid,
    window_size: tuple[int, int],
    margin: int = 30,
    turn_factor: float = 1,
) -> None:
    """Adjust boid velocity to keep it within the window."""
    if boid.pos.x < margin:
        boid.vel.x += turn_factor
    elif boid.pos.x > window_size[0] - margin:
        boid.vel.x -= turn_factor

    if boid.pos.y < margin:
        boid.vel.y += turn_factor
    elif boid.pos.y > window_size[1] - margin:
        boid.vel.y -= turn_factor
