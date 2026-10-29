"""Tests for boids/options.py"""

from collections.abc import Iterator
from pathlib import Path

import pytest

from my_boids.options import (
    BOID_AVOID_MODE_AVOID,
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    BoidOptions,
    BoundaryType,
    PredatorOptions,
    ScreenOptions,
    load_config,
)


@pytest.fixture(autouse=True)
def isolated_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    config_path = tmp_path / "config.ini"
    config_path.write_text(
        """[screen]
winsize = [800, 600]
fullscreen = no
boundary_type = BOUNCE

[boids]
num_boids = 53
size = 10
max_speed = 20.0
cohesion_factor = 0.01
separation = 20.0
avoid_factor = 0.05
alignment_factor = 0.05
visual_range = 40
boid_avoid_mode = avoid

[predator]
predator_attack_mode = center
"""
    )
    monkeypatch.chdir(tmp_path)
    load_config.cache_clear()
    yield
    load_config.cache_clear()


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


def test_screen_options_show_metrics_defaults_to_true():
    assert ScreenOptions().show_metrics is True


def test_screen_options_show_metrics_falls_back_to_true_when_missing():
    assert ScreenOptions.from_config().show_metrics is True


@pytest.mark.parametrize(("raw", "expected"), [("yes", True), ("no", False)])
def test_screen_options_reads_show_metrics(tmp_path: Path, raw: str, expected: bool):
    config_path = tmp_path / "metrics.ini"
    config_path.write_text(
        f"[screen]\nwinsize = [800, 600]\nboundary_type = BOUNCE\nshow_metrics = {raw}\n"
    )
    load_config.cache_clear()

    assert ScreenOptions.from_config(str(config_path)).show_metrics is expected
    load_config.cache_clear()


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


def test_boid_options_avoid_mode():
    """BoidOptions reads boid_avoid_mode from config."""
    opts = BoidOptions.from_config()
    assert opts.boid_avoid_mode == BOID_AVOID_MODE_AVOID


def test_boid_options_avoid_mode_legacy_fallback(tmp_path: Path):
    """Legacy predator_behavior_mode in [boids] remains supported."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("[boids]\npredator_behavior_mode = attract\n")
    load_config.cache_clear()

    opts = BoidOptions.from_config(str(config_path))

    assert opts.boid_avoid_mode == "attract"
    load_config.cache_clear()


def test_predator_options_attack_mode():
    """PredatorOptions reads predator attack mode from config."""
    opts = PredatorOptions.from_config()
    assert opts.predator_attack_mode == PREDATOR_ATTACK_MODE_CENTER


def test_predator_options_attack_mode_custom(tmp_path: Path):
    """PredatorOptions reads a configured predator attack mode."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("[predator]\npredator_attack_mode = nearest\n")
    load_config.cache_clear()

    opts = PredatorOptions.from_config(str(config_path))

    assert opts.predator_attack_mode == PREDATOR_ATTACK_MODE_NEAREST
    load_config.cache_clear()


def test_predator_options_attack_mode_invalid_falls_back(tmp_path: Path):
    """Invalid predator attack mode falls back to the default."""
    config_path = tmp_path / "config.ini"
    config_path.write_text("[predator]\npredator_attack_mode = ambush\n")
    load_config.cache_clear()

    opts = PredatorOptions.from_config(str(config_path))

    assert opts.predator_attack_mode == PREDATOR_ATTACK_MODE_MOUSE
    load_config.cache_clear()
