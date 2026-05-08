"""Steering and movement utility functions."""

import pygame as pg


def move_to(
    curr_pos: pg.Vector2,
    desired_pos: pg.Vector2,
    desired_speed: float = 10,
    tolerance: float = 10,
) -> tuple[pg.Vector2 | None, pg.Vector2]:
    """Move the object toward the desired position.

    Args:
        curr_pos (pg.Vector2): Current position vector
        desired_pos (pg.Vector2): Desired position vector
        desired_speed (float, optional): Desired speed toward new
            position. Defaults to 10.
        tolerance (float, optional): Minimum distance before calculating
            the new position. Defaults to 10.

    Returns:
        new_pos (pg.Vector2): New position vector. None if the object is
            within the tolerance.
        vel (pg.Vector2): Velocity vector
    """
    new_pos = None
    velocity = pg.Vector2(0, 0)

    # Distance from curr_pos to target_pos
    dist = curr_pos.distance_to(desired_pos)

    if dist > tolerance:
        # Velocity vector in direction of desired_pos
        velocity = (desired_pos - curr_pos).normalize() * desired_speed

        # Only update new position if distance is greater zero
        new_pos = curr_pos + velocity

    return new_pos, velocity
