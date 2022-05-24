"""Run the Boids Simulation"""
import configparser
import json
from typing import List, Tuple

import numpy as np
import pygame as pg

from boids.boids import Boid
from boids.movement import BoundaryType, move_boid

# Load parameters from config file
config = configparser.ConfigParser()
config.read("config.ini")

# Get screen parameters from config file
WINSIZE = json.loads(config["screen"]["winsize"])
USE_BOUNDARY_TYPE = BoundaryType[config["screen"]["boundary_type"].upper()]

# Get Boid parameters from config file
NUM_BOIDS = int(config["boids"]["num_boids"])
BOID_SIZE = int(config["boids"]["size"])
BOID_MAX_SPEED = float(config["boids"]["max_speed"])
BOID_COHESION_FACTOR = float(config["boids"]["cohesion_factor"])
BOID_SEPARATION = float(config["boids"]["separation"])
BOID_AVOID_FACTOR = float(config["boids"]["avoid_factor"])
BOID_ALIGNMENT_FACTOR = float(config["boids"]["alignment_factor"])
BOID_VISUAL_RANGE = 100


rng = np.random.default_rng()


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
            pos=pg.Vector2(rng.integers(0, high=WINSIZE, size=2).tolist()),
            vel=pg.Vector2(rng.uniform(-BOID_MAX_SPEED, BOID_MAX_SPEED, 2).tolist()),
            color=rng.integers(30, 255, 3).tolist(),
            size=BOID_SIZE,
        )
        boids_list.append(boid)

    return boids_list


def draw_boid(screen: Tuple[int, int], boid: Boid, color=None):
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
        center=boid.pos,
        radius=boid.size / 2,
    )
    # Draw the velociy vector
    pg.draw.line(
        screen,
        color=color,
        start_pos=boid.pos,
        end_pos=boid.pos + boid.vel,
    )


def update_boids(boids: List[Boid], screen):
    """Update the all of the boids"""
    for boid in boids:
        # Erease current boid
        draw_boid(screen, boid, color="black")

        # Apply movement rules to adjust velocity
        boid.cohesion(
            boids,
            cohesion_factor=BOID_COHESION_FACTOR,
            visual_range=BOID_VISUAL_RANGE,
        )
        boid.avoid_other_boids(
            boids,
            separation=BOID_SEPARATION,
            avoid_factor=BOID_AVOID_FACTOR,
        )
        boid.match_velocity(
            boids,
            alignment_factor=BOID_ALIGNMENT_FACTOR,
        )
        boid.speed_limit(max_speed=BOID_MAX_SPEED)

        # Move the boid (i.e., update position)
        move_boid(
            boid,
            boundary_type=USE_BOUNDARY_TYPE,
            window_size=WINSIZE,
        )

        # Draw the updated boid
        draw_boid(screen, boid)


def check_events() -> bool:
    """Check for events and return True if the game should be closed"""
    done = False
    for event in pg.event.get():
        # Close window or hit escape
        if event.type == pg.QUIT or (
            event.type == pg.KEYUP and event.key == pg.K_ESCAPE
        ):
            done = True
            break
        elif event.type == pg.KEYDOWN:
            pass
        # elif event.type == pg.MOUSEBUTTONDOWN:
        #     WINCENTER[:] = list(event.pos)

    return done


def main():
    """The Main Function"""
    # Initialize pygame
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("Boids")
    clock = pg.time.Clock()
    screen.fill((0, 0, 0))

    # Initialize the boids
    boids = init_boids(NUM_BOIDS)

    # Main game loop
    done = False
    while not done:
        # Update the flock of boids
        update_boids(boids, screen)

        pg.display.update()

        # Check for events
        done = check_events()

        clock.tick(50)


if __name__ == "__main__":
    pg.init()

    main()

    pg.quit()
