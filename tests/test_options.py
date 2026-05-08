"""Tests for my_boids.options."""

from pathlib import Path

import pytest

from my_boids.options import (
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    BoidOptions,
    BoundaryType,
    PredatorOptions,
    ScreenOptions,
    load_config,
    write_config,
)


def test_screen_options_winsize():
    opts = ScreenOptions.from_config()
    assert opts.winsize == [800, 600]


def test_screen_options_fullscreen():
    opts = ScreenOptions.from_config()
    assert opts.fullscreen is False


def test_screen_options_boundary_type():
    opts = ScreenOptions.from_config()
    assert opts.boundary_type == BoundaryType.BOUNCE


def test_boid_options_num_boids():
    opts = BoidOptions.from_config()
    assert opts.num_boids == 53


def test_boid_options_size():
    opts = BoidOptions.from_config()
    assert opts.size == 10


def test_boid_options_max_speed():
    opts = BoidOptions.from_config()
    assert opts.max_speed == pytest.approx(20.0)


def test_boid_options_cohesion_factor():
    opts = BoidOptions.from_config()
    assert opts.cohesion_factor == pytest.approx(0.01)


def test_boid_options_separation():
    opts = BoidOptions.from_config()
    assert opts.separation == pytest.approx(20.0)


def test_boid_options_avoid_factor():
    opts = BoidOptions.from_config()
    assert opts.avoid_factor == pytest.approx(0.05)


def test_boid_options_alignment_factor():
    opts = BoidOptions.from_config()
    assert opts.alignment_factor == pytest.approx(0.05)


def test_boid_options_visual_range():
    opts = BoidOptions.from_config()
    assert opts.visual_range == 40


def test_predator_options_attack_mode():
    opts = PredatorOptions.from_config()
    assert opts.predator_attack_mode == PREDATOR_ATTACK_MODE_NEAREST


def test_predator_options_attack_mode_custom(tmp_path: Path):
    config_path = tmp_path / "config.ini"
    config_path.write_text("[predator]\npredator_attack_mode = nearest\n")
    load_config.cache_clear()

    opts = PredatorOptions.from_config(str(config_path))

    assert opts.predator_attack_mode == PREDATOR_ATTACK_MODE_NEAREST
    load_config.cache_clear()


def test_predator_options_attack_mode_invalid_falls_back(tmp_path: Path):
    config_path = tmp_path / "config.ini"
    config_path.write_text("[predator]\npredator_attack_mode = ambush\n")
    load_config.cache_clear()

    opts = PredatorOptions.from_config(str(config_path))

    assert opts.predator_attack_mode == PREDATOR_ATTACK_MODE_MOUSE
    load_config.cache_clear()


def test_write_config_appends_missing_section(tmp_path: Path):
    config_path = tmp_path / "config.ini"
    config_path.write_text("[boids]\nnum_boids = 10\n")

    write_config(
        str(config_path),
        {
            "boids": {"num_boids": "12"},
            "predator": {"predator_attack_mode": "nearest"},
        },
    )

    text = config_path.read_text()
    assert "num_boids = 12" in text
    assert "[predator]" in text
    assert "predator_attack_mode = nearest" in text
