import pygame as pg
import pytest
from boids.boids import Boid


@pytest.fixture
def boid_with_vector_init():
    return Boid(
        pos=pg.Vector2(1, 2),
        vel=pg.Vector2(3, 4),
        color=pg.Color(0, 0, 0),
        size=1,
    )


def test_default_boid():
    boid = Boid()
    assert boid.pos == pg.math.Vector2(0, 0)
    assert boid.vel == pg.math.Vector2(0, 0)
    assert boid.color == (255, 255, 255)
    assert boid.size == 10


def test_valid_boid_with_vector_init():
    boid = Boid(
        pos=pg.Vector2(1, 2),
        vel=pg.Vector2(3, 4),
        color=pg.Color(0, 0, 0),
        size=1,
    )
    assert boid.pos == pg.Vector2(1, 2)
    assert boid.vel == pg.Vector2(3, 4)
    assert boid.color == pg.Color(0, 0, 0)
    assert boid.size == 1


def test_valid_boid_with_tuple_init():
    boid = Boid(
        pos=(1, 2),
        vel=(3, 4),
        color=(0, 0, 0),
        size=1,
    )
    assert boid.pos == pg.Vector2(1, 2)
    assert boid.vel == pg.Vector2(3, 4)
    assert boid.color == pg.Color(0, 0, 0)
    assert boid.size == 1


@pytest.mark.parametrize(
    "color",
    (
        (0, 0),  # Too few elements
        (-1, 0, 0),  # Negative element
        (0, 0, 256),  # Element too large
        (0, 0, 0, 0, 0),  # Too many elements
    ),
)
def test_boid_with_invalid_color(color):
    with pytest.raises(ValueError):
        Boid(
            pos=(1, 2),
            vel=(3, 4),
            color=color,
            size=1,
        )


def test_boid_with_invalid_size():
    with pytest.raises(ValueError):
        Boid(
            pos=(1, 2),
            vel=(3, 4),
            color=(0, 0, 0),
            size=-1,
        )


def test_boid_str(boid_with_vector_init):
    assert (
        str(boid_with_vector_init)
        == "Boid(pos=[1, 2], vel=[3, 4], color=(0, 0, 0, 255), size=1)"
    )
