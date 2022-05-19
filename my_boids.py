import math

import numpy as np
from boid import Boid

import pygame as pg
import pygame.gfxdraw

# Constants
WINSIZE = [640, 480]
WINCENTER = [320, 240]
NUMBOIDS = 3

rng = np.random.default_rng(12345)


def pol2cart(rho, phi):
    x = rho * math.cos(math.radians(phi))
    y = rho * math.sin(math.radians(phi))
    return (x, y)


def init_boids(num_boids: int) -> list:
    """Initialize the list of boids

    Args:
        num_boids (int): number of boids to initialize

    Returns:
        list: list of boids
    """
    boids_list = []
    for n in range(num_boids):
        boid = Boid(
            position=rng.integers(0, high=WINSIZE, size=2).tolist(),
            direction=rng.uniform(0, 360),
            speed=5,
            color=rng.integers(10, 255, 3).tolist(),
            size=2,
        )
        boids_list.append(boid)
    return boids_list


def draw_boids(screen, boids, color="black"):
    # Draw the boids
    for boid in boids:
        if color == "black":
            boid_color = boid.color
        else:
            boid_color = color

        pg.draw.circle(
            screen,
            color=boid_color,
            center=boid.position,
            radius=boid.size,
        )
        dir_x, dir_y = pol2cart(boid.speed + boid.size, boid.direction)
        pg.draw.line(
            screen,
            boid_color,
            boid.position,
            (boid.position[0] + dir_x, boid.position[1] + dir_y),
        )


def main():
    # Initialize the boids
    boids = init_boids(NUMBOIDS)
    [print(b) for b in boids]

    # Initialize pygame
    pg.init()
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("Boids")
    clock = pg.time.Clock()

    screen.fill((0, 0, 0))

    # Main game loop
    done = False
    while not done:
        draw_boids(screen, boids, color="black")
        # move_boids(boids)
        draw_boids(screen, boids)
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
