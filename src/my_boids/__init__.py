"""Public API for the my_boids package."""

from my_boids.game import Game
from my_boids.options import (
    BOID_AVOID_MODE_ATTRACT,
    BOID_AVOID_MODE_AVOID,
    BOID_AVOID_MODES,
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    PREDATOR_ATTACK_MODES,
    BoidAvoidMode,
    BoidOptions,
    BoundaryType,
    PredatorAttackMode,
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
    "BoidAvoidMode",
    "PredatorAttackMode",
    "BOID_AVOID_MODE_AVOID",
    "BOID_AVOID_MODE_ATTRACT",
    "BOID_AVOID_MODES",
    "PREDATOR_ATTACK_MODE_MOUSE",
    "PREDATOR_ATTACK_MODE_CENTER",
    "PREDATOR_ATTACK_MODE_NEAREST",
    "PREDATOR_ATTACK_MODE_ISOLATED",
    "PREDATOR_ATTACK_MODES",
]
