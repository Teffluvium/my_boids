"""Tests for boids/options.py"""

import pytest

from my_boids.boid_vs_boundary import BoundaryType
from my_boids.options import BoidOptions, ScreenOptions


def test_screen_options_winsize():
    """ScreenOptions reads window size from config"""
    opts = ScreenOptions()
    assert opts.winsize == [800, 600]


def test_screen_options_fullscreen():
    """ScreenOptions reads fullscreen flag from config"""
    opts = ScreenOptions()
    assert opts.fullscreen is False


def test_screen_options_boundary_type():
    """ScreenOptions reads and converts boundary_type from config"""
    opts = ScreenOptions()
    assert opts.boundary_type == BoundaryType.BOUNCE


def test_boid_options_num_boids():
    """BoidOptions reads num_boids from config"""
    opts = BoidOptions()
    assert opts.num_boids == 53


def test_boid_options_size():
    """BoidOptions reads size from config"""
    opts = BoidOptions()
    assert opts.size == 10


def test_boid_options_max_speed():
    """BoidOptions reads max_speed from config"""
    opts = BoidOptions()
    assert opts.max_speed == pytest.approx(20.0)


def test_boid_options_cohesion_factor():
    """BoidOptions reads cohesion_factor from config"""
    opts = BoidOptions()
    assert opts.cohesion_factor == pytest.approx(0.01)


def test_boid_options_separation():
    """BoidOptions reads separation from config"""
    opts = BoidOptions()
    assert opts.separation == pytest.approx(20.0)


def test_boid_options_avoid_factor():
    """BoidOptions reads avoid_factor from config"""
    opts = BoidOptions()
    assert opts.avoid_factor == pytest.approx(0.05)


def test_boid_options_alignment_factor():
    """BoidOptions reads alignment_factor from config"""
    opts = BoidOptions()
    assert opts.alignment_factor == pytest.approx(0.05)


def test_boid_options_visual_range():
    """BoidOptions reads visual_range from config"""
    opts = BoidOptions()
    assert opts.visual_range == 40
