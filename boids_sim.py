"""Run the Boids Simulation"""
from enum import Enum, auto
import numpy as np
import pygame as pg

from boids.boids import Boid

# Constants
WINSIZE = [800, 600]
# WINCENTER = [320, 240]

# Number of boids
NUM_BOIDS = 7
# Size of the boids
BOID_SIZE = 5
# Maximum speed of the boids
BOID_MAX_SPEED = 3
# Amount that the boids move towards the center of the flock
BOID_COHESION_FACTOR = 0.001
# Desired separation between boids
BOID_SEPARATION = 20
# Amount that the boids move away from each other
BOID_AVOID_FACTOR = 0.01
# Amount that the boids try to match the velocity of the flock
BOID_ALIGNMENT_FACTOR = 0.01


class BoundaryType(Enum):
    """Enum for boid behavior when they hit the boundary"""
    BOUNCE = auto()
    WRAP = auto()


USE_BOUNDARY_TYPE = BoundaryType.BOUNCE

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
            vel=pg.Vector2(rng.integers(0, high=WINSIZE, size=2).tolist()),
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
        center=boid.pos,
        radius=boid.size,
    )
    # Draw the velociy vector
    pg.draw.line(
        screen,
        color=color,
        start_pos=boid.pos,
        end_pos=boid.pos + boid.vel,
    )


def move_boid(boid):
    """Move the boid according to its velocity"""
    boid.move()

    # Select the boundary type
    if USE_BOUNDARY_TYPE == BoundaryType.WRAP:
        wrap_around_screen(boid)
    elif USE_BOUNDARY_TYPE == BoundaryType.BOUNCE:
        keep_within_bounds(boid)


def wrap_around_screen(boid):
    """Make boids wrap around the screen"""
    boid.pos.update(
        boid.pos[0] % WINSIZE[0],
        boid.pos[1] % WINSIZE[1],
    )


def keep_within_bounds(boid):
    """Keep boid within screen bounds"""
    margin = 30
    turn_factor = 1
    if boid.pos[0] < margin:
        boid.vel[0] += turn_factor
    elif boid.pos[0] > (WINSIZE[0] - margin):
        boid.vel[0] -= turn_factor

    if boid.pos[1] < margin:
        boid.vel[1] += turn_factor
    elif boid.pos[1] > (WINSIZE[1] - margin):
        boid.vel[1] -= turn_factor


def update_boids(boids: list, screen):
    """Update the all of the boids"""
    for boid in boids:
        # Erease current boid
        draw_boid(screen, boid, color="black")

        # Apply movement rules
        boid.cohesion(boids, BOID_COHESION_FACTOR)
        boid.avoid_other_boids(boids, BOID_SEPARATION, BOID_AVOID_FACTOR)
        boid.match_velocity(boids, BOID_ALIGNMENT_FACTOR)
        boid.speed_limit(BOID_MAX_SPEED)

        move_boid(boid)

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
