"""Run the Boids Simulation"""
import configparser
import json
from typing import List, Tuple

import numpy as np
import pygame as pg

from boids.boids import Boid
from boids.movement import BoundaryType, move_boid


class ScreenOptions:
    """Options for the simulation"""

    def __init__(self):
        # Load parameters from config file
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Get screen parameters from config file
        self.winsize = json.loads(config["screen"]["winsize"])
        self.fullscreen = config["screen"].getboolean("fullscreen")
        self.boundary_type = BoundaryType[config["screen"]["boundary_type"].upper()]


class BoidOptions:
    """Options for the Boids"""

    def __init__(self):
        # Load parameters from config file
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Get Boid parameters from config file
        self.num_boids = config["boids"].getint("num_boids")
        self.size = config["boids"].getint("size")
        self.max_speed = config["boids"].getfloat("max_speed")
        self.cohesion_factor = config["boids"].getfloat("cohesion_factor")
        self.separation = config["boids"].getfloat("separation")
        self.avoid_factor = config["boids"].getfloat("avoid_factor")
        self.alignment_factor = config["boids"].getfloat("alignment_factor")
        self.visual_range = config["boids"].getint("visual_range")


rng = np.random.default_rng()


def init_boids() -> list:
    """Initialize the list of boids
    Assigns random positions, velocities, and colors

    Returns:
        list: list of boids
    """
    screen_opts = ScreenOptions()
    boid_opts = BoidOptions()
    boids_list = []
    for _ in range(boid_opts.num_boids):
        boid = Boid(
            pos=pg.Vector2(rng.integers(0, high=screen_opts.winsize, size=2).tolist()),
            vel=pg.Vector2(
                rng.uniform(-boid_opts.max_speed, boid_opts.max_speed, 2).tolist()
            ),
            color=rng.integers(30, 255, 3).tolist(),
            size=boid_opts.size,
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
    screen_opts = ScreenOptions()
    boid_opts = BoidOptions()
    for boid in boids:
        # Erease current boid
        draw_boid(screen, boid, color="black")

        # Apply movement rules to adjust velocity
        boid.cohesion(
            boids,
            cohesion_factor=boid_opts.cohesion_factor,
            visual_range=boid_opts.visual_range,
        )
        boid.avoid_other_boids(
            boids,
            separation=boid_opts.separation,
            avoid_factor=boid_opts.avoid_factor,
        )
        boid.match_velocity(
            boids,
            alignment_factor=boid_opts.alignment_factor,
        )
        boid.speed_limit(max_speed=boid_opts.max_speed)

        # Move the boid (i.e., update position)
        move_boid(
            boid,
            boundary_type=screen_opts.boundary_type,
            window_size=screen_opts.winsize,
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
    screen_opts = ScreenOptions()
    if screen_opts.fullscreen:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
    else:
        screen = pg.display.set_mode(screen_opts.winsize)

    pg.display.set_caption("Boids")
    clock = pg.time.Clock()
    screen.fill((0, 0, 0))

    # Initialize the boids
    boids = init_boids()

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
