"""Tests for the settings dialog UI."""

from pathlib import Path

import pygame_gui
import pytest

from my_boids.boid_vs_boundary import BoundaryType
from my_boids.game import Game
from my_boids.options import (
    PREDATOR_ATTACK_CENTER,
    PREDATOR_ATTACK_NEAREST,
    PREDATOR_MODE_AVOID,
    BoidOptions,
    ScreenOptions,
)
from my_boids.settings_ui import SettingsDialog


@pytest.fixture(name="ui_game")
def fixture_ui_game(pygame_display):
    """Return a minimal game instance for settings UI tests."""
    screen_opts = ScreenOptions(
        winsize=[800, 600],
        fullscreen=False,
        boundary_type=BoundaryType.BOUNCE,
    )
    boid_opts = BoidOptions(
        num_boids=3,
        size=10,
        max_speed=5.0,
        cohesion_factor=0.005,
        separation=20,
        avoid_factor=0.05,
        alignment_factor=0.01,
        visual_range=100,
        predator_behavior_mode=PREDATOR_MODE_AVOID,
        predator_attack_strategy=PREDATOR_ATTACK_CENTER,
        predator_detection_range=400.0,
        predator_reaction_strength=0.5,
    )
    return Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        use_spatial_grid=False,
        show_metrics=False,
        enable_profiling=False,
    )


def _make_dialog(tmp_path: Path, ui_game: Game) -> SettingsDialog:
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
predator_behavior_mode = avoid
predator_attack_strategy = center
predator_detection_range = 400.0
predator_reaction_strength = 0.5
"""
    )
    ui_manager = pygame_gui.UIManager((800, 600))
    return SettingsDialog(ui_manager=ui_manager, config_path=str(config_path), game=ui_game)


def test_settings_dialog_collects_attack_strategy(tmp_path: Path, ui_game: Game):
    """Collected values include predator_attack_strategy from dropdown state."""
    dialog = _make_dialog(tmp_path, ui_game)
    dialog.open((800, 600))

    updated_opts = ui_game.boid_opts.model_copy(update={"predator_attack_strategy": "nearest"})
    dialog._populate(updated_opts, ui_game.screen_opts)

    values = dialog._collect_boid_values()
    assert values["predator_attack_strategy"] == PREDATOR_ATTACK_NEAREST

    dialog.close()


def test_settings_dialog_write_config_does_not_append_none(tmp_path: Path, ui_game: Game):
    """Config writes keep key/value lines clean when there is no inline comment."""
    dialog = _make_dialog(tmp_path, ui_game)
    dialog._write_config(ui_game.boid_opts)

    text = (tmp_path / "config.ini").read_text()
    assert "None" not in text
    assert "predator_attack_strategy = center" in text
    assert "num_boids = 3" in text
