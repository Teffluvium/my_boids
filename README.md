# My Boids

Python implementation of Boids using the PyGame engine for the visualization.

## 1. Installation

### Virtual Environment

Create a Python virtual environment and activate it.

```bash
python -m venv .venv
```

#### Activate the virtual environment

Windows virtual environment activation

```bash
.venv/Scripts/activate
```

Mac or Linux virtural environment activation

```bash
source .venv/bin/activate
```

#### Install requirements

This simulation requires the numpy and pygame packages.  These can be installed via `pip` andn the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

## 2. Running the Simulation

Run the script `boids_sim.py` to see the Boids in action.

## 3. Simulation Settings

Adjust the parameters in the `[screen]` section of `config.ini` to change some general game settings:

- Screen dimensions in pixels: [width, height]
    \
    `winsize = [800, 600]`
- Select the boundary type at the edge of the screen: either WRAP or BOUNCE
    \
    `boundary_type = BOUNCE`

Adjust the `[boid]` parameters at in the file `config.ini` to modify the boid behaviour in the simulation:

- Number of boids
    \
    `num_boids = 7`
- Size of the boids
    \
    `size = 5`
- Maximum speed of the boids
    \
    `max_speed = 3`
- Amount that the boids move towards the center of the flock
    \
    `cohesion_factor = 0.001`
- Desired separation between boids
    \
    `separation = 20`
- Amount that the boids move away from each other
    \
    `avoid_factor = 0.01`
- Amount that the boids try to match the velocity of the flock

    `alignment_factor = 0.01`

## 4. Additional references for Boids

- [Background and Update by Conrad Parker](http://www.red3d.com/cwr/boids/)
- [Conrad Parker psuedocode](http://www.kfish.org/boids/pseudocode.html): Original psuedocode and explanations
- [Smarter Every Day Git Repo](https://github.com/beneater/boids): JavaScript version of Boids
- [Wikipedia](https://en.wikipedia.org/wiki/Boids): Overview of Boids
