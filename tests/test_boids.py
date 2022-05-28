"""Test the Boids class"""
import pygame as pg
import pytest
from boids.boids import Boid


@pytest.mark.skip(reason="Manual test fails; but VSCode test passes... WTF?")
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
    assert type(boid.pos) is pg.Vector2
    assert type(boid.vel) is pg.Vector2
    assert type(boid.color) is pg.Color
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


def test_boid_update(boid_with_vector_init):
    """Test the move method"""
    boid_with_vector_init.update()
    assert boid_with_vector_init.pos == pg.Vector2(4, 6)
    assert boid_with_vector_init.vel == pg.Vector2(3, 4)


@pytest.mark.parametrize(
    "boid,expected",
    [
        (Boid(vel=(0, 10)), pg.Vector2(0, 5)),
        (Boid(vel=(10, 0)), pg.Vector2(5, 0)),
        (Boid(vel=(0, -10)), pg.Vector2(0, -5)),
        (Boid(vel=(6, 8)), pg.Vector2(3, 4)),
        (Boid(vel=(-6, 8)), pg.Vector2(-3, 4)),
        (Boid(vel=(6, -8)), pg.Vector2(3, -4)),
        (Boid(vel=(-6, -8)), pg.Vector2(-3, -4)),
    ],
)
def test_boid_speed_limit(boid, expected):
    """Test the speed_limit method"""
    boid.speed_limit(max_speed=5)
    assert boid.vel == expected
