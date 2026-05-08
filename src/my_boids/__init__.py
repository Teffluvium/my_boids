"""Public API for the my_boids package."""

from my_boids.game import Game
from my_boids.options import (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    PREDATOR_ATTACK_MODES,
    PREDATOR_BEHAVIOR_MODES,
    PREDATOR_MODE_ATTRACT,
    PREDATOR_MODE_AVOID,
    BoidOptions,
    BoundaryType,
    PredatorAttackMode,
    PredatorBehaviorMode,
    PredatorOptions,
    ScreenOptions,
)
from my_boids.settings_ui import SettingsDialog

__all__ = [
    "Game",
    "SettingsDialog",
    "BoundaryType",
    "ScreenOptions",
    "BoidOptions",
    "PredatorOptions",
    "PredatorBehaviorMode",
    "PredatorAttackMode",
    "PREDATOR_MODE_AVOID",
    "PREDATOR_MODE_ATTRACT",
    "PREDATOR_BEHAVIOR_MODES",
    "PREDATOR_ATTACK_MODE_MOUSE",
    "PREDATOR_ATTACK_MODE_CENTER",
    "PREDATOR_ATTACK_MODE_NEAREST",
    "PREDATOR_ATTACK_MODE_ISOLATED",
    "PREDATOR_ATTACK_MODES",
]
