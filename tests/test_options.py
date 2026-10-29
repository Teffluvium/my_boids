"""Tests for boids/options.py"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

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


@pytest.mark.parametrize("model, speed", [(BoidOptions, 20.0), (PredatorOptions, 5.0)])
def test_motion_options_have_independent_defaults(model, speed):
    options = model.get_defaults()

    assert options.max_speed == speed
    assert options.max_acceleration == 0.5
    assert options.max_deceleration == 1.0


@pytest.mark.parametrize(
    "model, expected", [(BoidOptions, (8.25, 0.31, 0.14)), (PredatorOptions, (6.75, 0.62, 0.23))]
)
def test_motion_options_load_only_their_own_section(tmp_path: Path, model, expected):
    config_path = tmp_path / "motion.ini"
    config_path.write_text(
        "[boids]\nmax_speed = 8.25\nmax_acceleration = 0.31\nmax_deceleration = 0.14\n"
        "[predator]\nmax_speed = 6.75\nmax_acceleration = 0.62\nmax_deceleration = 0.23\n"
    )

    options = model.from_config(str(config_path))

    assert (options.max_speed, options.max_acceleration, options.max_deceleration) == pytest.approx(
        expected
    )


@pytest.mark.parametrize("model, minimum_speed", [(BoidOptions, 5), (PredatorOptions, 1)])
@pytest.mark.parametrize("field", ["max_speed", "max_acceleration", "max_deceleration"])
@pytest.mark.parametrize("fraction", [0, 0.371, 1])
def test_motion_options_accept_endpoints_and_fractional_values(
    model, minimum_speed, field, fraction
):
    lower, upper = (minimum_speed, 50) if field == "max_speed" else (0.1, 5)
    value = lower + fraction * (upper - lower)
    options = model(**{field: value})

    assert getattr(options, field) == pytest.approx(value)
    setattr(options, field, value)
    assert getattr(options, field) == pytest.approx(value)


@pytest.mark.parametrize("model, minimum_speed", [(BoidOptions, 5), (PredatorOptions, 1)])
@pytest.mark.parametrize("field", ["max_speed", "max_acceleration", "max_deceleration"])
@pytest.mark.parametrize("kind", ["below", "above", "zero", "negative", "nan", "inf", "-inf"])
def test_motion_options_reject_invalid_construction_and_assignment(
    model, minimum_speed, field, kind
):
    lower, upper = (minimum_speed, 50) if field == "max_speed" else (0.1, 5)
    invalid = {
        "below": lower - 0.01,
        "above": upper + 0.01,
        "zero": 0,
        "negative": -1,
        "nan": float("nan"),
        "inf": float("inf"),
        "-inf": -float("inf"),
    }[kind]

    with pytest.raises(ValidationError):
        model(**{field: invalid})

    options = model()
    original = options.model_dump()
    with pytest.raises(ValidationError):
        setattr(options, field, invalid)
    assert options.model_dump() == original


@pytest.mark.parametrize("has_predator_section", [False, True])
def test_missing_predator_motion_values_do_not_inherit_boid_limits(
    tmp_path: Path, has_predator_section
):
    config_path = tmp_path / "legacy.ini"
    config_path.write_text(
        "[boids]\nmax_speed = 42\nmax_acceleration = 4\nmax_deceleration = 3\n"
        "predator_attack_strategy = nearest\n"
        + ("[predator]\npredator_attack_strategy = nearest\n" if has_predator_section else "")
    )

    options = PredatorOptions.from_config(str(config_path))

    assert (options.max_speed, options.max_acceleration, options.max_deceleration) == (5, 0.5, 1)
    assert options.predator_attack_mode == "nearest"


@pytest.mark.parametrize("model, speed", [(BoidOptions, 20), (PredatorOptions, 5)])
def test_missing_motion_config_keys_use_defaults(tmp_path: Path, model, speed):
    config_path = tmp_path / "defaults.ini"
    config_path.write_text("[boids]\n[predator]\n")

    options = model.from_config(str(config_path))

    assert (options.max_speed, options.max_acceleration, options.max_deceleration) == (
        speed,
        0.5,
        1,
    )
