import pygame as pg
import pytest
from boids.flock_rules import avoid_other_boids, cohesion, flock_rules, match_velocity


@pytest.mark.parametrize(
    "index, visual_range, expected",
    [
        (0, 100, (0, 10)),  # boid_list[0] All boids are within visual range
        (1, 100, (5.5, 0)),  # boid_list[1] All boids is within visual range
        (1, 5, (6, 5)),  # boid_list[1] One boid is within visual range
    ],
)
def test_boid_cohesion(boid_list, index, visual_range, expected):
    """Test the cohesion method"""
    boid = boid_list[index]
    cohesion(
        boid,
        boid_list,
        cohesion_factor=1,
        visual_range=visual_range,
    )
    assert boid.vel == pg.Vector2(expected)


def test_boid_avoidance(boid_list):
    """Test the avoidance method"""
    boid = boid_list[0]
    avoid_other_boids(
        boid,
        boid_list,
        separation=20,
        avoid_factor=0.1,
    )
    assert boid.vel == pg.Vector2(0, -2)


@pytest.mark.parametrize(
    "index, visual_range, expected",
    [
        (0, 100, (0, 5)),  # boid_list[0] All boids are within visual range
        (1, 100, (-2, 2.5)),  # boid_list[1] All boids is within visual range
        (1, 5, (-4, 5)),  # boid_list[1] One boid is within visual range
    ],
)
def test_boid_match_velocity(boid_list, index, visual_range, expected):
    """Test the match_velocity method"""
    boid = boid_list[index]
    match_velocity(
        boid,
        boid_list,
        alignment_factor=1,
        visual_range=visual_range,
    )
    assert boid.vel == pg.Vector2(expected)


def test_boid_flock_rules(boid_list):
    """Test the flock_rules method"""
    boid = boid_list[0]
    flock_rules(
        boid,
        boid_list,
        cohesion_factor=1,
        separation=20,
        alignment_factor=1,
        avoid_factor=0.1,
        visual_range=100,
    )
    assert boid.vel == pg.Vector2(0, 5)
