# My Boids

Python implementation of Boids using the PyGame engine for the visualization.

## Requirements

- Python 3.12 or higher
- [UV](https://github.com/astral-sh/uv) package manager

## Installation

### Install UV

If you don't have UV installed, install it first:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Project Dependencies

UV will automatically create a virtual environment and install all dependencies:

```bash
uv sync
```

Alternatively, you can use the Makefile:

```bash
make install
```

## Running the Simulation

You can run the simulation using any of these methods:

**Using UV:**
```bash
uv run my-boids
```

**Using the Makefile:**
```bash
make run
```

**Direct script execution (legacy):**
```bash
python boids_sim.py
```

## Development

This project uses UV for dependency management, ruff for linting and formatting, and mypy for type checking.

### Makefile Targets

The project includes a Makefile with common development tasks:

- `make install` - Install dependencies using UV
- `make format` - Format code using ruff
- `make lint` - Check code for linting issues
- `make lint-fix` - Auto-fix linting issues where possible
- `make type-check` - Run mypy type checking
- `make test` - Run tests with coverage
- `make run` - Run the boids simulation
- `make clean` - Remove generated files and caches
- `make all` - Run format, lint, type-check, and test in sequence
- `make help` - Show all available targets

### Manual Commands

If you prefer to run commands directly:

**Format code:**
```bash
uv run ruff format .
```

**Lint code:**
```bash
uv run ruff check .
```

**Fix linting issues:**
```bash
uv run ruff check --fix .
```

**Run type checking:**
```bash
uv run mypy src/my_boids tests
```

**Run tests:**
```bash
uv run pytest tests/ --cov=my_boids --cov-report=html --cov-report=term
```

## Simulation Settings

Adjust the parameters in the `[screen]` section of `config.ini` to change some general game settings:

- Screen dimensions in pixels: [width, height]
    \
    `winsize = [800, 600]`
- Use fullscreen mode? Will accept values of 'yes'/'no', 'on'/'off', 'true'/'false' and '1'/'0'
    \
    `fullscreen = no`
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
    \
    `alignment_factor = 0.01`
- Radius of boids vision.  Boids will not interact with other boids that exceed this radius
    \
    `visual_range = 50`

## Additional References for Boids

- [Background and Update by Conrad Parker](http://www.red3d.com/cwr/boids/)
- [Conrad Parker psuedocode](http://www.kfish.org/boids/pseudocode.html): Original psuedocode and explanations
- [Smarter Every Day Git Repo](https://github.com/beneater/boids): JavaScript version of Boids
- [Wikipedia](https://en.wikipedia.org/wiki/Boids): Overview of Boids
