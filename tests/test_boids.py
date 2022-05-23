"""Test the Boids class"""
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


def test_default_boid():
    """Test the default boid"""
    boid = Boid()
    assert boid.pos == pg.Vector2(0, 0)
    assert boid.vel == pg.Vector2(0, 0)
    assert boid.color == (255, 255, 255)
    assert boid.size == 10


def test_valid_boid_with_vector_init(boid_with_vector_init):
    """Initialize a boid with vector arguments"""
    boid = boid_with_vector_init
    assert boid.pos == pg.Vector2(1, 2)
    assert boid.vel == pg.Vector2(3, 4)
    assert boid.color == pg.Color(0, 0, 0)
    assert boid.size == 1


def test_valid_boid_with_tuple_init():
    """Initialize a Boid with tuple arguments"""
    boid = Boid(
        pos=(1, 2),
        vel=(3, 4),
        color=(0, 0, 0),
        size=1,
    )
    assert boid.pos == pg.Vector2(1, 2)
    assert boid.vel == pg.Vector2(3, 4)
    assert type(boid.pos) is pg.Vector2
    assert type(boid.vel) is pg.Vector2
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
    """Test that a Boid with an invalid color raises an error"""
    with pytest.raises(ValueError):
        Boid(
            pos=(1, 2),
            vel=(3, 4),
            color=color,
            size=1,
        )


def test_boid_with_invalid_size():
    """Test that a Boid with an invalid size raises an error"""
    with pytest.raises(ValueError):
        Boid(
            pos=(1, 2),
            vel=(3, 4),
            color=(0, 0, 0),
            size=-1,
        )


def test_boid_str(boid_with_vector_init):
    """Test the __str__ method"""
    assert (
        str(boid_with_vector_init)
        == "Boid(pos=[1, 2], vel=[3, 4], color=(0, 0, 0, 255), size=1)"
    )


def test_boid_move(boid_with_vector_init):
    """Test the move method"""
    boid_with_vector_init.move()
    assert boid_with_vector_init.pos == pg.Vector2(4, 6)
    assert boid_with_vector_init.vel == pg.Vector2(3, 4)


def test_boid_cohesion(boid_list):
    """Test the cohesion method"""
    boid_list[0].cohesion(boid_list, cohesion_factor=1)
    assert boid_list[0].vel == pg.Vector2(0, 10)


def test_boid_avoidance(boid_list):
    """Test the avoidance method"""
    boid_list[0].avoid_other_boids(
        boid_list,
        separation=20,
        avoid_factor=.1,
    )
    assert boid_list[0].vel == pg.Vector2(0, -2)
