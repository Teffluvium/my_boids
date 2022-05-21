# My Boids

Python implementation of Boids using the PyGame engine for the visualization.

## Installation and Running


### Installation
Create a Python virtual environment and activate it.
```
python -m venv .venv
```

Windows virtual environment activation
```
.venv/Scripts/activate
```

Mac or Linux virtural environment activation
```
source .venv/bin/activate
```

Install the required packages
```
pip install -r requirements.txt
```

### Running the Simulation

Run the script `boids_sim.py` to see the Boids in action.


## Simulation Performance
Adjust the following configuration parameters at the top of the `boids_sim.py` file to modify the simulation behavior:

- Number of boids <br>
    `NUM_BOIDS = 7`
- Size of the boids <br>
    `BOID_SIZE = 5`
- Maximum speed of the boids <br>
    `BOID_MAXSPEED = 3`
- Amount that the boids move towards the center of the flock <br>
    `BOID_COHESION_FACTOR = 0.001`
- Desired separation between boids <br>
    `BOID_SEPARATION = 20`
- Amount that the boids move away from each other <br>
    `BOID_AVOID_FACTOR = 0.01`
- Amount that the boids try to match the velocity of the flock <br>
    `BOID_ALIGNMENT_FACTOR = 0.01`

## Additional references for Boids
- [Background and Update by Conrad Parker](http://www.red3d.com/cwr/boids/)
- [Conrad Parker psuedocode](http://www.kfish.org/boids/pseudocode.html): Original psuedocode and explanations
- [Smarter Every Day Git Repo](https://github.com/beneater/boids): JavaScript version of Boids
- [Wikipedia](https://en.wikipedia.org/wiki/Boids): Overview of Boids