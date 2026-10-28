# Performance Optimization Analysis

## FlockStepper Verification (2026-10-27)

Issue #36 moves rule orchestration and neighbor-index maintenance behind
`FlockStepper`. A seeded before/after check using the existing
`benchmark_simulation` harness found no meaningful spatial-backend slowdown:

| Starting Boids | Full Scan Before (ms) | Full Scan After (ms) | Grid Before (ms) | Grid After (ms) |
|----------------|-----------------------|----------------------|------------------|-----------------|
| 50 | 0.570 | 0.527 | 0.297 | 0.292 |
| 100 | 1.937 | 1.838 | 0.647 | 0.641 |
| 200 | 7.524 | 6.929 | 1.521 | 1.521 |

Conditions: macOS arm64, Python 3.12.11, pygame-ce 2.5.7, SDL dummy display/audio,
100 frames per run, no rendering, default predator settings, and the harness's
800x600 bounce boundary and 40-pixel visual range. Both NumPy's game generator
and Python's random module were reset to seed 36 before each run. Populations
are starting counts; collisions can remove boids during the run. The baseline
includes the separation search-radius correction but precedes the wrapping fix
and extraction. These are single-run smoke measurements, not statistically
significant speedup claims or a new backend-selection policy.

Reproduce the after measurements from the project root:

```sh
SDL_AUDIODRIVER=dummy uv run python - <<'PY'
import random
import numpy as np
import my_boids.game as game_module
from benchmark_performance import benchmark_simulation

for count in (50, 100, 200):
  for enabled in (False, True):
    game_module.rng = np.random.default_rng(36)
    random.seed(36)
    result = benchmark_simulation(count, enabled, frames_to_test=100)
    print(count, enabled, result.avg_frame_time_ms)
PY
```

The current options model caps populations at 200, so this check does not use
the harness's historical 500-boid main configuration. Grid queries sort only
local candidates into flock order; they do not scan the whole population for
each lookup. Dense flocks can still have quadratic behavior.

Verification: 168 tests passed, one pre-existing skip; Ruff lint, changed-file
format checks, and mypy passed. The stepper has 100% statement coverage in the
coverage run. Backend parity is checked across bounded multiframe fixtures with
absolute and relative tolerances of 1e-9, including sequential wraps and
separation exceeding visual range.

The remaining sections record earlier measurements and recommendations. Their
performance conclusions should not be read as results for this implementation.

## Executive Summary

Performance benchmarking revealed that **spatial partitioning is not universally beneficial**. At the current simulation scale (53 boids), the brute force approach is actually 3-4x faster than spatial partitioning.

## Benchmark Results

Testing was performed with 300 frames across different boid counts:

| Boids | Brute Force FPS | Spatial Grid FPS | Speedup | Result |
|-------|-----------------|------------------|----------|-----------------|
| 50 | 1,599 FPS | 436 FPS | 0.27x | 4x slower |
| 100 | 528 FPS | 172 FPS | 0.32x | 3x slower |
| 200 | 148 FPS | 79 FPS | 0.54x | 2x slower |
| 500 | 24 FPS | 23 FPS | 0.96x | About the same |

## Analysis

### Why Spatial Partitioning is Slower (at small scales)

1. **Grid Rebuilding Overhead**: The spatial grid is rebuilt every frame by:

   - Clearing the entire grid structure
   - Iterating through all boids
   - Computing cell coordinates for each boid
   - Inserting each boid into the grid

1. **Query Overhead**: Each neighbor query requires:

   - Computing which cells to check (9+ cells for typical visual range)
   - Iterating through multiple cell lists
   - Performing distance calculations to filter results

1. **Memory Allocation**: The grid uses a dictionary with list values, requiring:

   - Hash computations for cell coordinates
   - List allocations and appends
   - Dictionary resizing as cells are populated

### When Does Spatial Partitioning Help?

Based on the benchmark, the crossover point where spatial partitioning becomes beneficial is around **500+ boids**. The theoretical analysis:

- **Brute Force**: O(n²) - every boid checks every other boid

  - 50 boids: 2,500 comparisons
  - 100 boids: 10,000 comparisons
  - 500 boids: 250,000 comparisons

- **Spatial Grid**: O(n) average case, but with overhead

  - Grid building: O(n)
  - Query: O(1) average for fixed visual range
  - Total: O(n) + overhead

At small n, the constant overhead dominates. At large n, the O(n²) growth makes brute force prohibitive.

## Recommendations

### Immediate Actions

1. **Change Default**: Set `use_spatial_grid=False` for the default configuration (53 boids)
1. **Adaptive Mode**: Consider automatically enabling spatial grid only when boid count > 300
1. **User Control**: Keep the toggle available for testing and demonstration

### Code Changes

```python
# In Game.__init__
def __init__(
    self,
    use_spatial_grid: bool | None = None,  # None = auto-detect
    ...
):
    # Auto-detect if not specified
    if use_spatial_grid is None:
        use_spatial_grid = self.boid_opts.num_boids >= 300

    self.use_spatial_grid = use_spatial_grid
```

### Future Optimizations

1. **Incremental Grid Updates**: Instead of rebuilding the entire grid each frame, update only moved boids
1. **Fixed Grid Size**: Pre-allocate grid cells to avoid dictionary overhead
1. **Profiling**: The performance monitor now makes it easy to identify other bottlenecks
1. **Vectorization**: Use NumPy for batch position/velocity updates

## Visual Demonstration

The performance metrics display now shows:

- **FPS**: Real-time frames per second
- **Frame Time**: Milliseconds per frame
- **Mode**: "Spatial" or "Brute Force"
- **Timing Breakdown**: Update, Logic, Collision, and Render times

Run the simulation and press the spatial grid toggle to see the difference in real-time!

## Conclusion

This optimization work successfully:

- ✅ Implemented spatial partitioning with O(n) neighbor queries
- ✅ Added comprehensive unit tests (12 new tests)
- ✅ Integrated performance monitoring infrastructure
- ✅ Created benchmarking tools for quantitative analysis
- ⚠️ Discovered spatial partitioning hurts performance at current scale

The key insight: **Optimization without measurement is guesswork**. The spatial grid is a textbook optimization that actually makes things worse in this specific case. The performance monitoring infrastructure ensures we can make data-driven decisions.

## Files Created/Modified

- `src/my_boids/spatial_grid.py` - Spatial hash grid implementation
- `src/my_boids/performance.py` - Performance monitoring system
- `src/my_boids/game.py` - Integrated both systems
- `tests/test_spatial_grid.py` - 12 unit tests for spatial grid
- `tests/test_performance.py` - 13 unit tests for performance monitor
- `benchmark_performance.py` - Benchmark comparison script

Total: 113 tests passing, no linting errors, no type errors.
