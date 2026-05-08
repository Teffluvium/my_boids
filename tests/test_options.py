"""Tests for boids/options.py"""

from pathlib import Path

import pytest

from my_boids.boid_vs_boundary import BoundaryType
from my_boids.options import (
    PREDATOR_ATTACK_MOUSE,
    PREDATOR_ATTACK_NEAREST,
    BoidOptions,
    ScreenOptions,
    load_config,
)


def test_screen_options_winsize():
    """ScreenOptions reads window size from config"""
    opts = ScreenOptions.from_config()
    assert opts.winsize == [800, 600]


def test_screen_options_fullscreen():
    """ScreenOptions reads fullscreen flag from config"""
    opts = ScreenOptions.from_config()
    assert opts.fullscreen is False


def test_screen_options_boundary_type():
    """ScreenOptions reads and converts boundary_type from config"""
    opts = ScreenOptions.from_config()
    assert opts.boundary_type == BoundaryType.BOUNCE


def test_boid_options_num_boids():
    """BoidOptions reads num_boids from config"""
    opts = BoidOptions.from_config()
    assert opts.num_boids == 53


def test_boid_options_size():
    """BoidOptions reads size from config"""
    opts = BoidOptions.from_config()
    assert opts.size == 10


def test_boid_options_max_speed():
    """BoidOptions reads max_speed from config"""
    opts = BoidOptions.from_config()
    assert opts.max_speed == pytest.approx(20.0)


def test_boid_options_cohesion_factor():
    """BoidOptions reads cohesion_factor from config"""
    opts = BoidOptions.from_config()
    assert opts.cohesion_factor == pytest.approx(0.01)


def test_boid_options_separation():
    """BoidOptions reads separation from config"""
    opts = BoidOptions.from_config()
    assert opts.separation == pytest.approx(20.0)


def test_boid_options_avoid_factor():
    """BoidOptions reads avoid_factor from config"""
    opts = BoidOptions.from_config()
    assert opts.avoid_factor == pytest.approx(0.05)


def test_boid_options_alignment_factor():
    """BoidOptions reads alignment_factor from config"""
    opts = BoidOptions.from_config()
    assert opts.alignment_factor == pytest.approx(0.05)


def test_boid_options_visual_range():
    """BoidOptions reads visual_range from config"""
    opts = BoidOptions.from_config()
    assert opts.visual_range == 40


def test_boid_options_predator_attack_strategy():
    """BoidOptions reads predator attack strategy from config."""
    opts = BoidOptions.from_config()
    assert opts.predator_attack_strategy == PREDATOR_ATTACK_MOUSE


def test_boid_options_predator_attack_strategy_custom(tmp_path: Path):
    """BoidOptions reads a configured predator attack strategy."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("[boids]\npredator_attack_strategy = nearest\n")
    load_config.cache_clear()

    opts = BoidOptions.from_config(str(config_path))

    assert opts.predator_attack_strategy == PREDATOR_ATTACK_NEAREST
    load_config.cache_clear()


def test_boid_options_predator_attack_strategy_invalid_falls_back(tmp_path: Path):
    """Invalid predator attack strategy falls back to the default."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("[boids]\npredator_attack_strategy = ambush\n")
    load_config.cache_clear()

    opts = BoidOptions.from_config(str(config_path))

    assert opts.predator_attack_strategy == PREDATOR_ATTACK_MOUSE
    load_config.cache_clear()
