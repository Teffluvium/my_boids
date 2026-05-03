import os

import pygame as pg
import pytest

from my_boids.boids import Boid


@pytest.fixture(scope="session", name="pygame_display")
def fixture_pygame_display():
    """Initialize pygame with a headless dummy display for tests that need it.

    This fixture starts a virtual display using SDL's dummy driver so that
    operations requiring an active display (e.g. Surface.convert, image.load,
    font rendering) work in headless CI environments.
    """
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pg.init()
    screen = pg.display.set_mode((800, 600))
    yield screen
    pg.quit()


@pytest.fixture(name="boid_with_vector_init")
def fixture_boid_with_vector_init():
    """Return a Boid initialized using vectors"""
    return Boid(
        pos=pg.Vector2(1, 2),
        vel=pg.Vector2(3, 4),
        color=pg.Color(0, 0, 0),
        size=1,
    )


@pytest.fixture(name="boid_list")
def fixture_boid_list():
    """Return a list of boids"""
    return [
        Boid(
            pos=(0, 0),
            vel=(0, 0),
            color=(0, 0, 0),
            size=1,
        ),
        Boid(
            pos=(-1, 10),
            vel=(4, 5),
            color=(0, 0, 0),
            size=1,
        ),
        Boid(
            pos=(1, 10),
            vel=(-4, 5),
            color=(0, 0, 0),
            size=1,
        ),
    ]
