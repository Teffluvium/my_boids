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
- `make install-hooks` - Install pre-commit hooks
- `make format` - Format code using ruff
- `make lint` - Check code for linting issues
- `make lint-fix` - Auto-fix linting issues where possible
- `make type-check` - Run mypy type checking
- `make test` - Run tests with coverage
- `make pre-commit` - Run pre-commit hooks on all files
- `make run` - Run the boids simulation
- `make clean` - Remove generated files and caches
- `make uninstall-hooks` - Uninstall pre-commit hooks
- `make all` - Run format, lint, type-check, and test in sequence
- `make help` - Show all available targets

### Pre-commit Hooks

The project uses pre-commit hooks to automatically check code quality before commits. To set up:

```bash
# Install pre-commit hooks
make install-hooks
```

Or manually:

```bash
uv run --with pre-commit pre-commit install
```

Once installed, the hooks will automatically run on every commit. To manually run all hooks:

```bash
make pre-commit
```

The following checks run automatically:

- Ruff linting and formatting
- Mypy type checking
- Trailing whitespace removal
- End-of-file fixes
- YAML, JSON, and TOML validation
- Large file detection
- Private key detection

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

## Experimental Flocking Algorithms

`FlockStepper` accepts an optional algorithm; omitting it uses `ClassicFlocking`.
`ClassicFlocking` and the `FlockingAlgorithm` protocol are available from
`my_boids.flock_rules`; the stepper is in `my_boids.flock_stepper`.
Individual functions such as `cohesion`, `avoid_other_boids`, `match_velocity`,
and `flock_rules` remain available for composing experiments.

For example, replace the classic composition with separation only:

```python
from collections.abc import Sequence

from my_boids.boids import Boid
from my_boids.flock_rules import avoid_other_boids
from my_boids.flock_stepper import FlockStepper
from my_boids.options import BoidOptions


class SeparationOnly:
    def __init__(self, strength: float = 0.1) -> None:
        self.strength = strength

    def neighbor_radius(self, options: BoidOptions) -> float:
        return options.separation

    def apply_to_boid(
        self, boid: Boid, neighbors: Sequence[Boid], *, options: BoidOptions
    ) -> None:
        avoid_other_boids(boid, neighbors, options.separation, self.strength)


stepper = FlockStepper(algorithm=SeparationOnly(strength=0.1), use_spatial_grid=True)
```

Call `stepper.apply()` with the same boids, predator position, and current option
objects as usual. Algorithm selection is programmatic at stepper construction;
there is no settings-menu or configuration-file selector.

- `neighbor_radius()` is called once per pass and must return a finite
  nonnegative radius, or `None` for the whole flock. Invalid radii raise
  `ValueError` before boids are mutated. Unbounded or state-dependent interactions
  should request the whole flock, which bypasses spatial pruning.
- Neighbors are identical across scan/grid modes: supplied flock order, self
  included, and Euclidean distance less than or equal to the declared radius.
  Radius zero includes coincident members. Apply any stricter rule thresholds
  inside the algorithm; wrapping does not imply toroidal neighbor distances.
- Algorithms may mutate only the subject boid's velocity. Do not move boids,
  change membership/options/neighbors, or retain neighborhoods as snapshots.
  Later boids observe earlier velocity updates and boundary wraps.
- The stepper still applies predator reaction, speed limiting, and boundary
  handling after the algorithm, and owns spatial-index maintenance and
  diagnostics. It does not own movement or collisions.

## Performance Monitoring

The simulation includes built-in performance monitoring that displays real-time metrics on screen:

- **FPS**: Frames per second
- **Frame Time**: Milliseconds per frame
- **Boids Count**: Number of active boids
- **Mode**: Current optimization mode (Brute Force or Spatial Grid)
- **Timing Breakdown**: Individual operation times (Update, Logic, Collision, Render)

### Performance Analysis

A comprehensive performance benchmark has been conducted comparing different optimization strategies. Key findings:

- **Brute Force (O(n²))**: Best performance for < 300 boids
- **Spatial Grid (O(n))**: Only beneficial at 500+ boids due to grid rebuilding overhead

See [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md) for detailed benchmark results and optimization recommendations.

### Running Benchmarks

To benchmark the simulation yourself:

```bash
uv run python benchmark_performance.py
```

This will test both brute force and spatial grid modes across multiple boid counts (50, 100, 200, 500) and display a detailed comparison table.

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
- Show performance metrics and the predator detection range circle? Accepts the same values as `fullscreen`. Defaults to `yes` when omitted
  \
  `show_metrics = yes`

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
- Radius of boids vision. Boids will not interact with other boids that exceed this radius
  \
  `visual_range = 50`
- Predator reaction mode. Use `avoid` for fleeing behaviour or `attract` to make boids chase the predator
  \
  `boid_avoid_mode = avoid`
- Predator attack mode. Use `mouse`, `center`, `nearest`, or `isolated` to steer the predator with the mouse cursor or target the flock center, closest boid, or most isolated boid
  \
  `predator_attack_mode = mouse`
- Distance at which the predator senses boids and boids react to the predator. In `center`, `nearest`, and `isolated` modes the predator only targets boids within this range; when it loses them it flies to where it last saw one, then wanders the screen until a boid comes back into range. `mouse` mode ignores the range
  \
  `predator_detection_range = 400.0`
- Peak strength of the boids' reaction to the predator. The reaction is strongest next to the predator and fades linearly to zero at the edge of the detection range
  \
  `predator_reaction_strength = 0.5`

## Additional References for Boids

- [Background and Update by Conrad Parker](http://www.red3d.com/cwr/boids/)
- [Conrad Parker psuedocode](http://www.kfish.org/boids/pseudocode.html): Original psuedocode and explanations
- [Smarter Every Day Git Repo](https://github.com/beneater/boids): JavaScript version of Boids
- [Wikipedia](https://en.wikipedia.org/wiki/Boids): Overview of Boids
