"""Classes to store configuration settings"""

import configparser
import json
from functools import lru_cache
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from my_boids.boid_vs_boundary import BoundaryType

PredatorBehaviorMode = Literal["avoid", "attract"]
PREDATOR_MODE_AVOID: PredatorBehaviorMode = "avoid"
PREDATOR_MODE_ATTRACT: PredatorBehaviorMode = "attract"
PREDATOR_BEHAVIOR_MODES: tuple[PredatorBehaviorMode, PredatorBehaviorMode] = (
    PREDATOR_MODE_AVOID,
    PREDATOR_MODE_ATTRACT,
)
PredatorAttackStrategy = Literal["mouse", "center", "nearest", "isolated"]
PREDATOR_ATTACK_MOUSE: PredatorAttackStrategy = "mouse"
PREDATOR_ATTACK_CENTER: PredatorAttackStrategy = "center"
PREDATOR_ATTACK_NEAREST: PredatorAttackStrategy = "nearest"
PREDATOR_ATTACK_ISOLATED: PredatorAttackStrategy = "isolated"
PREDATOR_ATTACK_STRATEGIES: tuple[
    PredatorAttackStrategy,
    PredatorAttackStrategy,
    PredatorAttackStrategy,
    PredatorAttackStrategy,
] = (
    PREDATOR_ATTACK_MOUSE,
    PREDATOR_ATTACK_CENTER,
    PREDATOR_ATTACK_NEAREST,
    PREDATOR_ATTACK_ISOLATED,
)


@lru_cache(maxsize=1)
def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    """Load and cache the configuration file.

    This function is cached to ensure the config file is only parsed once.

    Args:
        config_path (str): Path to the configuration file. Defaults to "config.ini".

    Returns:
        configparser.ConfigParser: Parsed configuration object.
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


class ScreenOptions(BaseModel):
    """Options for the simulation screen."""

    model_config = ConfigDict(validate_assignment=True)

    winsize: list[int] = Field(default=[800, 600])
    fullscreen: bool = Field(default=False)
    boundary_type: BoundaryType = Field(default=BoundaryType.BOUNCE)

    @field_validator("winsize")
    @classmethod
    def validate_winsize(cls, v: list[int]) -> list[int]:
        if len(v) != 2 or any(x <= 0 for x in v):
            raise ValueError("winsize must be a list of two positive integers [width, height]")
        return v

    @classmethod
    def get_defaults(cls) -> "ScreenOptions":
        """Return an instance populated with default field values."""
        return cls()

    @classmethod
    def from_config(cls, config_path: str = "config.ini") -> "ScreenOptions":
        """Create ScreenOptions from a configuration file.

        Args:
            config_path (str): Path to the configuration file. Defaults to "config.ini".

        Returns:
            ScreenOptions: Screen options loaded from the config file.
        """
        config = load_config(config_path)

        winsize = json.loads(config["screen"]["winsize"])
        fullscreen = config["screen"].getboolean("fullscreen", fallback=False)
        boundary_type = BoundaryType[config["screen"]["boundary_type"].upper()]

        return cls(winsize=winsize, fullscreen=fullscreen, boundary_type=boundary_type)


class BoidOptions(BaseModel):
    """Options for the Boids."""

    model_config = ConfigDict(validate_assignment=True)

    num_boids: int = Field(default=53, ge=1, le=200)
    size: int = Field(default=10, ge=5, le=20)
    max_speed: float = Field(default=20.0, ge=5.0, le=50.0)
    cohesion_factor: float = Field(default=0.01, ge=0.001, le=0.1)
    separation: float = Field(default=20.0, ge=10.0, le=50.0)
    avoid_factor: float = Field(default=0.05, ge=0.01, le=0.2)
    alignment_factor: float = Field(default=0.05, ge=0.01, le=0.2)
    visual_range: int = Field(default=40, ge=20, le=100)
    predator_behavior_mode: PredatorBehaviorMode = Field(default=PREDATOR_MODE_AVOID)
    predator_attack_strategy: PredatorAttackStrategy = Field(default=PREDATOR_ATTACK_MOUSE)
    predator_detection_range: float = Field(default=400.0, ge=100.0, le=600.0)
    predator_reaction_strength: float = Field(default=0.5, ge=0.1, le=2.0)

    @classmethod
    def get_defaults(cls) -> "BoidOptions":
        """Return an instance populated with default field values."""
        return cls()

    @classmethod
    def from_config(cls, config_path: str = "config.ini") -> "BoidOptions":
        """Create BoidOptions from a configuration file.

        Pydantic performs validation; raises ValidationError on bad values.

        Args:
            config_path (str): Path to the configuration file. Defaults to "config.ini".

        Returns:
            BoidOptions: Boid options loaded from the config file.
        """
        config = load_config(config_path)
        defaults = cls.get_defaults()

        mode_raw = config["boids"].get(
            "predator_behavior_mode", fallback=defaults.predator_behavior_mode
        )
        if mode_raw not in PREDATOR_BEHAVIOR_MODES:
            mode_raw = defaults.predator_behavior_mode

        attack_strategy_raw = config["boids"].get(
            "predator_attack_strategy", fallback=defaults.predator_attack_strategy
        )
        if attack_strategy_raw not in PREDATOR_ATTACK_STRATEGIES:
            attack_strategy_raw = defaults.predator_attack_strategy

        return cls(
            num_boids=config["boids"].getint("num_boids", fallback=defaults.num_boids),
            size=config["boids"].getint("size", fallback=defaults.size),
            max_speed=config["boids"].getfloat("max_speed", fallback=defaults.max_speed),
            cohesion_factor=config["boids"].getfloat(
                "cohesion_factor", fallback=defaults.cohesion_factor
            ),
            separation=config["boids"].getfloat("separation", fallback=defaults.separation),
            avoid_factor=config["boids"].getfloat("avoid_factor", fallback=defaults.avoid_factor),
            alignment_factor=config["boids"].getfloat(
                "alignment_factor", fallback=defaults.alignment_factor
            ),
            visual_range=config["boids"].getint("visual_range", fallback=defaults.visual_range),
            predator_behavior_mode=cast(PredatorBehaviorMode, mode_raw),
            predator_attack_strategy=cast(PredatorAttackStrategy, attack_strategy_raw),
            predator_detection_range=config["boids"].getfloat(
                "predator_detection_range", fallback=defaults.predator_detection_range
            ),
            predator_reaction_strength=config["boids"].getfloat(
                "predator_reaction_strength", fallback=defaults.predator_reaction_strength
            ),
        )
