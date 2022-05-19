# import math
from math import sqrt

import numpy as np
import pygame as pg

from boids import Boid

# Constants
WINSIZE = [1000, 1000]
# WINSIZE = [640, 480]
WINCENTER = [320, 240]
NUMBOIDS = 5

BOID_SIZE = 5
BOID_MAXSPEED = 3
BOID_VELOCITY_FACTOR = 0.001  # How much to update the boid's velocity
BOID_MIN_DISTANCE = 20
BOID_AVOID_FACTOR = 0.01
BOID_MATCHING_FACTOR = 0.01


rng = np.random.default_rng()

# Create global variable for the boids
boids = []


def init_boids(num_boids: int) -> list:
    """Initialize the list of boids
    Assigns random positions, velocities, and colors

    Args:
        num_boids (int): number of boids to initialize

    Returns:
        list: list of boids
    """
    boids_list = []
    for _ in range(num_boids):
        boid = Boid(
            position=rng.integers(0, high=WINSIZE, size=2).tolist(),
            velocity=rng.integers(0, high=WINSIZE, size=2).tolist(),
            color=rng.integers(20, 255, 3).tolist(),
            size=BOID_SIZE,
        )
        boids_list.append(boid)

    return boids_list


def draw_boid(screen, boid, color=None):
    """Draw the boid on the screen"""
    # Draw the boids
    override_color = bool(color)

    # Override color if provided
    if not override_color:
        color = boid.color

    # Draw the boid
    pg.draw.circle(
        screen,
        color=color,
        center=boid.position,
        radius=boid.size,
    )
    # Draw the velociy vector
    pg.draw.line(
        screen,
        color=color,
        start_pos=boid.position,
        end_pos=(
            boid.position[0] + boid.velocity[0],
            boid.position[1] + boid.velocity[1],
        ),
    )


def move_boid(boid):
    """Move the boid according to its velocity"""
    boid.move()

    # Make boids wrap around the screen
    boid.position = (
        boid.position[0] % WINSIZE[0],
        boid.position[1] % WINSIZE[1],
    )


def fly_to_center_of_mass(boid):
    """Move the boid towards the perceived center of mass of the flock"""
    global boids

    # Calculate the center of mass
    sum_of_x = sum(b.position[0] for b in boids)
    sum_of_x -= boid.position[0]
    sum_of_y = sum(b.position[1] for b in boids)
    sum_of_y -= boid.position[1]
    center_of_mass = (sum_of_x / (NUMBOIDS - 1), sum_of_y / (NUMBOIDS - 1))

    delta_x = (center_of_mass[0] - boid.position[0]) * BOID_VELOCITY_FACTOR
    delta_y = (center_of_mass[1] - boid.position[1]) * BOID_VELOCITY_FACTOR

    # Update the boid's velocity
    boid.velocity[0] += delta_x
    boid.velocity[1] += delta_y


def avoid_other_boids(boid):
    """Avoid other boids that are too close"""
    global boids

    delta_x = 0
    delta_y = 0
    for other_boid in boids:
        # Skip checking the boid itself
        if other_boid is boid:
            continue

        # Calculate the distance between the boids
        distance = sqrt(
            (boid.position[0] - other_boid.position[0]) ** 2
            + (boid.position[1] - other_boid.position[1]) ** 2
        )

        # If the distance is less than the minimum, apply the avoidance
        if distance < BOID_MIN_DISTANCE:
            # Calculate the vector to the other boid
            delta_x += boid.position[0] - other_boid.position[0]
            delta_y += boid.position[1] - other_boid.position[1]

        # Apply the vector to the boid
        boid.velocity[0] += delta_x * BOID_AVOID_FACTOR
        boid.velocity[1] += delta_y * BOID_AVOID_FACTOR


def match_velocity(boid):
    """Match the velocity of the boid with the velocity of the flock"""
    global boids

    # Calculate the average velocity of the flock
    sum_of_x = sum(b.velocity[0] for b in boids)
    sum_of_x -= boid.velocity[0]
    sum_of_y = sum(b.velocity[1] for b in boids)
    sum_of_y -= boid.velocity[1]
    average_velocity = (sum_of_x / (NUMBOIDS - 1), sum_of_y / (NUMBOIDS - 1))

    # Update the boid's velocity
    boid.velocity[0] += average_velocity[0] * BOID_MATCHING_FACTOR
    boid.velocity[1] += average_velocity[1] * BOID_MATCHING_FACTOR


def clamp_speed(boid):
    speed = boid.speed
    # Apply a speed limit
    if speed > BOID_MAXSPEED:
        boid.velocity = [
            boid.velocity[0] * BOID_MAXSPEED / speed,
            boid.velocity[1] * BOID_MAXSPEED / speed,
        ]


def main():
    # Initialize the boids
    global boids
    boids = init_boids(NUMBOIDS)
    # [print(b) for b in boids]

    # Initialize pygame
    pg.init()
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("Boids")
    clock = pg.time.Clock()

    screen.fill((0, 0, 0))

    # Main game loop
    done = False
    while not done:
        for boid in boids:
            # Erease current boid
            draw_boid(screen, boid, color="black")

            # Apply movement rules
            fly_to_center_of_mass(boid)
            avoid_other_boids(boid)
            match_velocity(boid)
            clamp_speed(boid)

            move_boid(boid)

            # Draw the updated boid
            draw_boid(screen, boid)

        pg.display.update()
        for event in pg.event.get():
            # Close window or hit escape
            if event.type == pg.QUIT or (
                event.type == pg.KEYUP and event.key == pg.K_ESCAPE
            ):
                done = True
                break
            elif event.type == pg.KEYDOWN:
                pass
            elif event.type == pg.MOUSEBUTTONDOWN:
                WINCENTER[:] = list(event.pos)
        clock.tick(50)
    pg.quit()


if __name__ == "__main__":
    main()
