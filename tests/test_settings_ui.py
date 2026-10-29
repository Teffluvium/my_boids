"""Tests for the settings dialog UI."""

from pathlib import Path

import pygame_gui
import pytest

from my_boids.game import Game
from my_boids.options import (
    BOID_AVOID_MODE_AVOID,
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_NEAREST,
    BoidOptions,
    BoundaryType,
    PredatorOptions,
    ScreenOptions,
)
from my_boids.settings_service import SettingsSaveError
from my_boids.settings_ui import SettingsDialog


@pytest.fixture(name="ui_game")
def fixture_ui_game(pygame_display):
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
        boid_avoid_mode=BOID_AVOID_MODE_AVOID,
    )
    predator_opts = PredatorOptions(
        predator_attack_mode=PREDATOR_ATTACK_MODE_CENTER,
        predator_detection_range=400.0,
        predator_reaction_strength=0.5,
    )
    return Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        predator_opts=predator_opts,
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
boid_avoid_mode = avoid

[predator]
predator_attack_mode = center
predator_detection_range = 400.0
predator_reaction_strength = 0.5
"""
    )
    ui_manager = pygame_gui.UIManager((800, 600))
    return SettingsDialog(ui_manager=ui_manager, config_path=str(config_path), game=ui_game)


def test_settings_dialog_collects_attack_strategy(tmp_path: Path, ui_game: Game):
    dialog = _make_dialog(tmp_path, ui_game)
    dialog.open((800, 600))

    updated_predator = ui_game.predator_opts.model_copy(update={"predator_attack_mode": "nearest"})
    dialog._populate(ui_game.boid_opts, updated_predator, ui_game.screen_opts)

    values = dialog._collect_predator_values()
    assert values["predator_attack_mode"] == PREDATOR_ATTACK_MODE_NEAREST

    dialog.close()


def test_settings_dialog_stays_open_when_save_fails(
    tmp_path: Path, ui_game: Game, monkeypatch: pytest.MonkeyPatch
):
    dialog = _make_dialog(tmp_path, ui_game)
    dialog.open((800, 600))
    displayed_errors: list[str] = []
    monkeypatch.setattr(
        "my_boids.settings_ui.save_settings",
        lambda **_kwargs: (_ for _ in ()).throw(
            SettingsSaveError("apply", "runtime update failed", persisted=True)
        ),
    )
    monkeypatch.setattr(dialog, "_show_error", displayed_errors.append)

    dialog._handle_save()

    assert dialog.is_open()
    assert displayed_errors == ["Saved, but not fully applied: runtime update failed"]
    dialog.close()
