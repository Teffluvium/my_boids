"""Steering and movement utility functions."""

from math import ceil, hypot, isfinite

import pygame as pg


def limit_velocity(
    current_velocity: pg.Vector2,
    desired_velocity: pg.Vector2,
    *,
    max_speed: float,
    max_acceleration: float,
    max_deceleration: float,
) -> pg.Vector2:
    """Return a bounded velocity change without mutating either input."""
    if any(
        not isfinite(value) or value <= 0
        for value in (max_speed, max_acceleration, max_deceleration)
    ):
        raise ValueError("Motion limits must be finite and positive")
    if any(
        not isfinite(component)
        for vector in (current_velocity, desired_velocity)
        for component in vector
    ):
        raise ValueError("Velocity components must be finite")
    desired = desired_velocity.copy()
    if desired.length() > max_speed:
        desired.scale_to_length(max_speed)
    change = desired - current_velocity
    speed = current_velocity.length()
    if speed > max_speed:
        next_speed = max(desired.length(), speed - max_deceleration)
        return current_velocity * (next_speed / speed)
    if speed == 0:
        if change.length() > max_acceleration:
            change.scale_to_length(max_acceleration)
        return change

    direction = current_velocity / speed
    longitudinal = change.dot(direction)
    transverse = change - longitudinal * direction
    rate = max_deceleration if longitudinal < 0 else max_acceleration
    budget = hypot(longitudinal / rate, transverse.length() / max_acceleration)
    if budget == 0:
        return current_velocity.copy()
    fraction = min(1.0, 1.0 / budget)
    if longitudinal < -speed:
        fraction = min(fraction, speed / -longitudinal)
    return current_velocity + fraction * change


def arrival_velocity(
    position: pg.Vector2,
    target: pg.Vector2,
    *,
    max_speed: float,
    max_deceleration: float,
    tolerance: float = 10.0,
) -> pg.Vector2:
    """Request a speed that can brake to rest within the arrival region."""
    if any(not isfinite(value) or value <= 0 for value in (max_speed, max_deceleration)):
        raise ValueError("Motion limits must be finite and positive")
    if not isfinite(tolerance) or tolerance < 0:
        raise ValueError("Arrival tolerance must be finite and nonnegative")
    if any(not isfinite(component) for vector in (position, target) for component in vector):
        raise ValueError("Position components must be finite")
    offset = target - position
    distance = offset.length()
    remaining = max(distance - tolerance, 0.0)
    if remaining == 0:
        return pg.Vector2()

    lower, upper = 0.0, min(max_speed, remaining)
    for _iteration in range(64):
        candidate = (lower + upper) / 2
        steps = ceil(candidate / max_deceleration)
        stopping_distance = steps * candidate - max_deceleration * steps * (steps - 1) / 2
        if stopping_distance <= remaining:
            lower = candidate
        else:
            upper = candidate
    return offset * (lower / distance)


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
