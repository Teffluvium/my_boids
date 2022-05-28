import pygame as pg
import pytest
from boids.boids import Boid


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
