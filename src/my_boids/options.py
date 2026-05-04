"""Classes to store configuration settings"""

import configparser
import json
from dataclasses import dataclass
from functools import lru_cache

from my_boids.boid_vs_boundary import BoundaryType


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


@dataclass
class ScreenOptions:
    """Options for the simulation screen"""

    winsize: list[int]
    fullscreen: bool
    boundary_type: BoundaryType

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
        fullscreen = config["screen"].getboolean("fullscreen")
        assert fullscreen is not None, "fullscreen config value cannot be None"
        boundary_type_str = config["screen"]["boundary_type"].upper()
        boundary_type = BoundaryType[boundary_type_str]

        return cls(
            winsize=winsize,
            fullscreen=fullscreen,
            boundary_type=boundary_type,
        )


@dataclass
class BoidOptions:
    """Options for the Boids"""

    num_boids: int
    size: int
    max_speed: float
    cohesion_factor: float
    separation: float
    avoid_factor: float
    alignment_factor: float
    visual_range: int
    predator_behavior_mode: str
    predator_detection_range: float
    predator_reaction_strength: float

    @classmethod
    def from_config(cls, config_path: str = "config.ini") -> "BoidOptions":
        """Create BoidOptions from a configuration file.

        Args:
            config_path (str): Path to the configuration file. Defaults to "config.ini".

        Returns:
            BoidOptions: Boid options loaded from the config file.
        """
        config = load_config(config_path)

        num_boids = config["boids"].getint("num_boids")
        size = config["boids"].getint("size")
        max_speed = config["boids"].getfloat("max_speed")
        cohesion_factor = config["boids"].getfloat("cohesion_factor")
        separation = config["boids"].getfloat("separation")
        avoid_factor = config["boids"].getfloat("avoid_factor")
        alignment_factor = config["boids"].getfloat("alignment_factor")
        visual_range = config["boids"].getint("visual_range")
        predator_behavior_mode = config["boids"]["predator_behavior_mode"]
        predator_detection_range = config["boids"].getfloat("predator_detection_range")
        predator_reaction_strength = config["boids"].getfloat("predator_reaction_strength")

        # Validate that all values were successfully parsed
        assert num_boids is not None, "num_boids config value cannot be None"
        assert size is not None, "size config value cannot be None"
        assert max_speed is not None, "max_speed config value cannot be None"
        assert cohesion_factor is not None, "cohesion_factor config value cannot be None"
        assert separation is not None, "separation config value cannot be None"
        assert avoid_factor is not None, "avoid_factor config value cannot be None"
        assert alignment_factor is not None, "alignment_factor config value cannot be None"
        assert visual_range is not None, "visual_range config value cannot be None"
        assert predator_behavior_mode in [
            "avoid",
            "attract",
        ], "predator_behavior_mode must be 'avoid' or 'attract'"
        assert predator_detection_range is not None, (
            "predator_detection_range config value cannot be None"
        )
        assert predator_reaction_strength is not None, (
            "predator_reaction_strength config value cannot be None"
        )

        return cls(
            num_boids=num_boids,
            size=size,
            max_speed=max_speed,
            cohesion_factor=cohesion_factor,
            separation=separation,
            avoid_factor=avoid_factor,
            alignment_factor=alignment_factor,
            visual_range=visual_range,
            predator_behavior_mode=predator_behavior_mode,
            predator_detection_range=predator_detection_range,
            predator_reaction_strength=predator_reaction_strength,
        )
