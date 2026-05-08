"""Classes and helpers for configuration settings."""

from __future__ import annotations

import configparser
import json
import re
from enum import Enum, auto
from functools import lru_cache
from typing import Literal, Protocol, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BoundaryType(Enum):
    """Enum for boid behavior when they hit the boundary."""

    BOUNCE = auto()
    WRAP = auto()


PredatorBehaviorMode = Literal["avoid", "attract"]
PREDATOR_MODE_AVOID: PredatorBehaviorMode = "avoid"
PREDATOR_MODE_ATTRACT: PredatorBehaviorMode = "attract"
PREDATOR_BEHAVIOR_MODES: tuple[PredatorBehaviorMode, PredatorBehaviorMode] = (
    PREDATOR_MODE_AVOID,
    PREDATOR_MODE_ATTRACT,
)

PredatorAttackMode = Literal["mouse", "center", "nearest", "isolated"]
PREDATOR_ATTACK_MODE_MOUSE: PredatorAttackMode = "mouse"
PREDATOR_ATTACK_MODE_CENTER: PredatorAttackMode = "center"
PREDATOR_ATTACK_MODE_NEAREST: PredatorAttackMode = "nearest"
PREDATOR_ATTACK_MODE_ISOLATED: PredatorAttackMode = "isolated"
PREDATOR_ATTACK_MODES: tuple[
    PredatorAttackMode,
    PredatorAttackMode,
    PredatorAttackMode,
    PredatorAttackMode,
] = (
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_NEAREST,
    PREDATOR_ATTACK_MODE_ISOLATED,
)


@lru_cache(maxsize=1)
def load_config(config_path: str = "config.ini") -> configparser.ConfigParser:
    """Load and cache the configuration file."""
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def write_config(config_path: str, updates: dict[str, dict[str, str]]) -> None:
    """Persist config values while preserving layout and comments."""
    with open(config_path) as file_handle:
        lines = file_handle.readlines()

    section_pattern = re.compile(r"^\s*\[([^\]]+)\]\s*$")
    value_pattern = re.compile(r"^(\s*)(\w+)(\s*=\s*)([^\r\n]*)(\r?\n?)$")

    normalized_updates: dict[str, dict[str, str]] = {
        section.lower(): values.copy() for section, values in updates.items()
    }
    seen_sections: dict[str, bool] = dict.fromkeys(normalized_updates, False)
    written_keys: dict[str, set[str]] = {section: set[str]() for section in normalized_updates}

    current_section: str | None = None
    new_lines: list[str] = []

    for line in lines:
        section_match = section_pattern.match(line)
        if section_match is not None:
            current_section = section_match.group(1).lower()
            if current_section in seen_sections:
                seen_sections[current_section] = True
            new_lines.append(line)
            continue

        value_match = value_pattern.match(line)
        if value_match is None or current_section not in normalized_updates:
            new_lines.append(line)
            continue

        key = value_match.group(2)
        if key not in normalized_updates[current_section]:
            new_lines.append(line)
            continue

        indent = value_match.group(1)
        separator = value_match.group(3)
        trailing = value_match.group(4)
        line_ending = value_match.group(5)
        comment_match = re.match(r"^(.*?)(\s+[;#].*)?$", trailing)
        comment_text = ""
        if comment_match is not None and comment_match.group(2) is not None:
            comment_text = comment_match.group(2)

        value = normalized_updates[current_section][key]
        written_keys[current_section].add(key)
        new_lines.append(f"{indent}{key}{separator}{value}{comment_text}{line_ending}")

    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"

    for section, values in normalized_updates.items():
        missing_keys = [key for key in values if key not in written_keys[section]]
        if not missing_keys:
            continue

        if not seen_sections[section]:
            if new_lines and new_lines[-1].strip():
                new_lines.append("\n")
            new_lines.append(f"[{section}]\n")

        for key in missing_keys:
            new_lines.append(f"{key} = {values[key]}\n")

    with open(config_path, "w") as file_handle:
        file_handle.writelines(new_lines)

    load_config.cache_clear()


class ScreenOptions(BaseModel):
    """Options for the simulation screen."""

    model_config = ConfigDict(validate_assignment=True)

    winsize: list[int] = Field(default=[800, 600])
    fullscreen: bool = Field(default=False)
    boundary_type: BoundaryType = Field(default=BoundaryType.BOUNCE)

    @field_validator("winsize")
    @classmethod
    def validate_winsize(cls, value: list[int]) -> list[int]:
        if len(value) != 2 or any(item <= 0 for item in value):
            raise ValueError("winsize must be a list of two positive integers [width, height]")
        return value

    @classmethod
    def get_defaults(cls) -> ScreenOptions:
        return cls()

    @classmethod
    def from_config(cls, config_path: str = "config.ini") -> ScreenOptions:
        config = load_config(config_path)
        winsize = json.loads(config["screen"]["winsize"])
        fullscreen = config["screen"].getboolean("fullscreen", fallback=False)
        boundary_type = BoundaryType[config["screen"]["boundary_type"].upper()]
        return cls(winsize=winsize, fullscreen=fullscreen, boundary_type=boundary_type)


class BoidOptions(BaseModel):
    """Options for the boids."""

    model_config = ConfigDict(validate_assignment=True)

    num_boids: int = Field(default=53, ge=1, le=200)
    size: int = Field(default=10, ge=5, le=20)
    max_speed: float = Field(default=20.0, ge=5.0, le=50.0)
    cohesion_factor: float = Field(default=0.01, ge=0.001, le=0.1)
    separation: float = Field(default=20.0, ge=10.0, le=50.0)
    avoid_factor: float = Field(default=0.05, ge=0.01, le=0.2)
    alignment_factor: float = Field(default=0.05, ge=0.01, le=0.2)
    visual_range: int = Field(default=40, ge=20, le=100)

    @classmethod
    def get_defaults(cls) -> BoidOptions:
        return cls()

    @classmethod
    def from_config(cls, config_path: str = "config.ini") -> BoidOptions:
        config = load_config(config_path)
        defaults = cls.get_defaults()
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
        )


class PredatorOptions(BaseModel):
    """Options that control predator behavior."""

    model_config = ConfigDict(validate_assignment=True)

    predator_behavior_mode: PredatorBehaviorMode = Field(default=PREDATOR_MODE_AVOID)
    predator_attack_mode: PredatorAttackMode = Field(default=PREDATOR_ATTACK_MODE_MOUSE)
    predator_detection_range: float = Field(default=400.0, ge=100.0, le=600.0)
    predator_reaction_strength: float = Field(default=0.5, ge=0.1, le=2.0)

    @classmethod
    def get_defaults(cls) -> PredatorOptions:
        return cls()

    @classmethod
    def from_config(cls, config_path: str = "config.ini") -> PredatorOptions:
        config = load_config(config_path)
        defaults = cls.get_defaults()
        predator_section = config["predator"] if config.has_section("predator") else config["boids"]

        mode_raw = predator_section.get(
            "predator_behavior_mode", fallback=defaults.predator_behavior_mode
        )
        if mode_raw not in PREDATOR_BEHAVIOR_MODES:
            mode_raw = defaults.predator_behavior_mode

        attack_mode_raw = predator_section.get(
            "predator_attack_mode",
            fallback=predator_section.get(
                "predator_attack_strategy",
                fallback=defaults.predator_attack_mode,
            ),
        )
        if attack_mode_raw not in PREDATOR_ATTACK_MODES:
            attack_mode_raw = defaults.predator_attack_mode

        return cls(
            predator_behavior_mode=cast(PredatorBehaviorMode, mode_raw),
            predator_attack_mode=cast(PredatorAttackMode, attack_mode_raw),
            predator_detection_range=predator_section.getfloat(
                "predator_detection_range", fallback=defaults.predator_detection_range
            ),
            predator_reaction_strength=predator_section.getfloat(
                "predator_reaction_strength", fallback=defaults.predator_reaction_strength
            ),
        )


class GameProtocol(Protocol):
    """Minimal surface that SettingsDialog needs from Game."""

    boid_opts: BoidOptions
    predator_opts: PredatorOptions
    screen_opts: ScreenOptions

    def update_boid_options(self, opts: BoidOptions) -> None: ...

    def update_predator_options(self, opts: PredatorOptions) -> None: ...
