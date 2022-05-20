"""Run the Boids Simulation"""
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
            position=pg.Vector2(rng.integers(0, high=WINSIZE, size=2).tolist()),
            velocity=pg.Vector2(rng.integers(0, high=WINSIZE, size=2).tolist()),
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
        end_pos=boid.position + boid.velocity,
    )


def move_boid(boid):
    """Move the boid according to its velocity"""
    boid.move()

    # Make boids wrap around the screen
    boid.position.update(
        boid.position[0] % WINSIZE[0],
        boid.position[1] % WINSIZE[1],
    )


def update_boids(boids: list, screen):
    """Update the all of the boids"""
    for boid in boids:
        # Erease current boid
        draw_boid(screen, boid, color="black")

        # Apply movement rules
        boid.fly_to_center_of_mass(boids, BOID_VELOCITY_FACTOR)
        boid.avoid_other_boids(boids, BOID_MIN_DISTANCE, BOID_AVOID_FACTOR)
        boid.match_velocity(boids, BOID_MATCHING_FACTOR)
        boid.speed_limit(BOID_MAXSPEED)

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
        elif event.type == pg.MOUSEBUTTONDOWN:
            WINCENTER[:] = list(event.pos)

    return done


def main():
    """The Main Function"""
    # Initialize pygame
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("Boids")
    clock = pg.time.Clock()
    screen.fill((0, 0, 0))

    # Initialize the boids
    boids = init_boids(NUMBOIDS)

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
