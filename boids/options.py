import configparser
import json

from boids.boid_vs_boundary import BoundaryType


class ScreenOptions:
    """Options for the simulation"""

    def __init__(self):
        # Load parameters from config file
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Get screen parameters from config file
        self.winsize = json.loads(config["screen"]["winsize"])
        self.fullscreen = config["screen"].getboolean("fullscreen")
        self.boundary_type = BoundaryType[config["screen"]["boundary_type"].upper()]


class BoidOptions:
    """Options for the Boids"""

    def __init__(self):
        # Load parameters from config file
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Get Boid parameters from config file
        self.num_boids = config["boids"].getint("num_boids")
        self.size = config["boids"].getint("size")
        self.max_speed = config["boids"].getfloat("max_speed")
        self.cohesion_factor = config["boids"].getfloat("cohesion_factor")
        self.separation = config["boids"].getfloat("separation")
        self.avoid_factor = config["boids"].getfloat("avoid_factor")
        self.alignment_factor = config["boids"].getfloat("alignment_factor")
        self.visual_range = config["boids"].getint("visual_range")
