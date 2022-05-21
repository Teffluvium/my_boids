import configparser
import json

from boids.movement import BoundaryType

config = configparser.ConfigParser()
config.read('config.ini')

# Get screen parameters from config
WINSIZE = json.loads(config['screen']['winsize'])
USE_BOUNDARY_TYPE = BoundaryType[config['screen']['boundary_type'].upper()]

# Get Boid parameters from config
NUM_BOIDS = int(config['boids']['num_boids'])
BOID_SIZE = int(config['boids']['size'])
BOID_MAX_SPEED = float(config['boids']['max_speed'])
BOID_COHESION_FACTOR = float(config['boids']['cohesion_factor'])
BOID_SEPARATION = float(config['boids']['separation'])
BOID_AVOID_FACTOR = float(config['boids']['avoid_factor'])
BOID_ALIGNMENT_FACTOR = float(config['boids']['alignment_factor'])


