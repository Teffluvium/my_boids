"""Movement functions and classes for the boids"""
from enum import Enum, auto
from typing import Tuple

from boids.boids import Boid


class BoundaryType(Enum):
    """Enum for boid behavior when they hit the boundary"""

    BOUNCE = auto()
    WRAP = auto()


def move_boid(
    boid: Boid,
    boundary_type: BoundaryType,
    window_size: Tuple[int, int],
    margin: int = 30,
    turn_factor: float = 1,
) -> None:
    """Move a boid and keep it within the windows according to the boundary type.

    Args:
        boid (Boid): Its a Boid
        boundary_type (BoundaryType): What to do when the boid hits the edge
        window_size (Tuple[int, int]): Window size in pixels
    """

    # Move the boid according to its velocity
    boid.move()

    # Select the boundary type and adjust the boid's position and/or velocity
    if boundary_type == BoundaryType.WRAP:
        wrap_around_screen(
            boid,
            window_size,
        )
    elif boundary_type == BoundaryType.BOUNCE:
        keep_within_bounds(
            boid,
            window_size,
            margin=margin,
            turn_factor=turn_factor,
        )


def wrap_around_screen(boid: Boid, window_size: Tuple[int, int]) -> None:
    """Wrap boid around to opposite side of the window.

    Note: This function compares the postion of the boid to the window size
        and adjusts the position, leaving the velocity unchanged.

    Args:
        boid (Boid): Its a Boid
        window_size (Tuple[int, int]): Window size in pixels
    """
    boid.pos.update(
        boid.pos[0] % window_size[0],
        boid.pos[1] % window_size[1],
    )


def keep_within_bounds(
    boid: Boid,
    window_size: Tuple[int, int],
    margin: int = 30,
    turn_factor: float = 1,
) -> None:
    """Adjust the boid's velocity to keep it within the window.

    Note: This function compares the postion of the boid to the window size
        and adjusts the velocity, leaving the position unchanged.

    Args:
        boid (Boid): Its a Boid
        window_size (Tuple[int, int]): Window size in pixels
        margin (int, optional): Buffer of pixels from the edges of the
            window. Defaults to 30.
        turn_factor (float, optional): Adjust the velocity by this factor.
            Defaults to 1.
    """

    def adjust_vel(pos, vel, window_size) -> float:
        """Adjust velocity component to keep boid within bounds"""
        if pos < margin:
            vel += turn_factor
        elif pos > window_size - margin:
            vel -= turn_factor

        return vel

    # Calculate the new velocity
    vel = [0.0, 0.0]
    vel[0] = adjust_vel(boid.pos[0], boid.vel[0], window_size[0])
    vel[1] = adjust_vel(boid.pos[1], boid.vel[1], window_size[1])

    # Update the boid's velocity
    boid.vel.update(vel)
