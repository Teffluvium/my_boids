"""Classes to store configuration settings"""

import configparser
import json

from my_boids.boid_vs_boundary import BoundaryType


class ScreenOptions:
    """Options for the simulation"""

    winsize: list[int]
    fullscreen: bool
    boundary_type: BoundaryType

    def __init__(self):
        # Load parameters from config file
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Get screen parameters from config file
        self.winsize = json.loads(config["screen"]["winsize"])
        fullscreen_value = config["screen"].getboolean("fullscreen")
        assert fullscreen_value is not None
        self.fullscreen = fullscreen_value
        bound_type_str = config["screen"]["boundary_type"].upper()
        self.boundary_type = BoundaryType[bound_type_str]


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

    def __init__(self):
        # Load parameters from config file
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Get Boid parameters from config file
        num_boids = config["boids"].getint("num_boids")
        size = config["boids"].getint("size")
        max_speed = config["boids"].getfloat("max_speed")
        cohesion_factor = config["boids"].getfloat("cohesion_factor")
        separation = config["boids"].getfloat("separation")
        avoid_factor = config["boids"].getfloat("avoid_factor")
        alignment_factor = config["boids"].getfloat("alignment_factor")
        visual_range = config["boids"].getint("visual_range")

        # Assert values are not None and assign
        assert num_boids is not None
        assert size is not None
        assert max_speed is not None
        assert cohesion_factor is not None
        assert separation is not None
        assert avoid_factor is not None
        assert alignment_factor is not None
        assert visual_range is not None

        self.num_boids = num_boids
        self.size = size
        self.max_speed = max_speed
        self.cohesion_factor = cohesion_factor
        self.separation = separation
        self.avoid_factor = avoid_factor
        self.alignment_factor = alignment_factor
        self.visual_range = visual_range
