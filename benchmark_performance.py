#!/usr/bin/env python3
"""Performance comparison script for boids simulation.

This script benchmarks the simulation with and without spatial partitioning
across different boid counts to demonstrate the performance improvements.
"""

from dataclasses import dataclass

import pygame as pg

from my_boids.boid_vs_boundary import BoundaryType
from my_boids.game import Game
from my_boids.options import BoidOptions, ScreenOptions


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run.

    Attributes:
        boid_count: Number of boids in the simulation.
        use_spatial_grid: Whether spatial grid was enabled.
        avg_fps: Average frames per second.
        avg_frame_time_ms: Average frame time in milliseconds.
        total_frames: Total number of frames processed.
    """

    boid_count: int
    use_spatial_grid: bool
    avg_fps: float
    avg_frame_time_ms: float
    total_frames: int


def benchmark_simulation(
    boid_count: int,
    use_spatial_grid: bool,
    frames_to_test: int = 300,
) -> BenchmarkResult:
    """Run a benchmark of the simulation.

    Args:
        boid_count: Number of boids to simulate.
        use_spatial_grid: Whether to use spatial partitioning.
        frames_to_test: Number of frames to run for benchmarking.

    Returns:
        BenchmarkResult: Performance metrics from the benchmark.
    """
    # Initialize pygame headless mode (no display)
    import os

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pg.init()
    _screen = pg.display.set_mode((800, 600))

    # Create options
    screen_opts = ScreenOptions(
        winsize=[800, 600],
        fullscreen=False,
        boundary_type=BoundaryType.BOUNCE,
    )
    boid_opts = BoidOptions(
        num_boids=boid_count,
        size=10,
        max_speed=5.0,
        cohesion_factor=0.005,
        separation=20,
        avoid_factor=0.05,
        alignment_factor=0.01,
        visual_range=40,
    )

    # Create game instance
    game = Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        use_spatial_grid=use_spatial_grid,
        show_metrics=False,
        enable_profiling=True,
    )

    # Run simulation for specified number of frames
    for _ in range(frames_to_test):
        game.performance.start_frame()
        game.run_logic()
        game.performance.end_frame()

    # Get performance metrics
    avg_fps = game.performance.get_fps()
    avg_frame_time = game.performance.get_avg_frame_time()

    # Cleanup
    pg.quit()

    return BenchmarkResult(
        boid_count=boid_count,
        use_spatial_grid=use_spatial_grid,
        avg_fps=avg_fps,
        avg_frame_time_ms=avg_frame_time,
        total_frames=frames_to_test,
    )


def print_results(results: list[BenchmarkResult]) -> None:
    """Print benchmark results in a formatted table.

    Args:
        results: List of benchmark results to display.
    """
    print("\nPerformance Comparison Results")
    print("=" * 80)
    print(f"{'Boids':<10} {'Mode':<15} {'Avg FPS':<12} {'Avg Frame (ms)':<15} {'Frames':<10}")
    print("-" * 80)

    for result in results:
        mode = "Spatial Grid" if result.use_spatial_grid else "Brute Force"
        print(
            f"{result.boid_count:<10} {mode:<15} "
            f"{result.avg_fps:<12.2f} {result.avg_frame_time_ms:<15.3f} "
            f"{result.total_frames:<10}"
        )

    print("=" * 80)


def calculate_speedup(results: list[BenchmarkResult]) -> None:
    """Calculate and display speedup from spatial partitioning.

    Args:
        results: List of benchmark results containing paired comparisons.
    """
    print("\nSpeedup Analysis")
    print("=" * 80)
    print(f"{'Boids':<10} {'Brute Force FPS':<18} {'Spatial Grid FPS':<18} {'Speedup':<10}")
    print("-" * 80)

    # Group results by boid count
    boid_counts = sorted({r.boid_count for r in results})

    for boid_count in boid_counts:
        brute_force = next(
            (r for r in results if r.boid_count == boid_count and not r.use_spatial_grid),
            None,
        )
        spatial = next(
            (r for r in results if r.boid_count == boid_count and r.use_spatial_grid),
            None,
        )

        if brute_force and spatial:
            speedup = spatial.avg_fps / brute_force.avg_fps
            print(
                f"{boid_count:<10} {brute_force.avg_fps:<18.2f} "
                f"{spatial.avg_fps:<18.2f} {speedup:<10.2f}x"
            )

    print("=" * 80)


def main():
    """Run performance benchmarks and display results."""
    print("Boids Simulation Performance Benchmark")
    print("Testing spatial partitioning vs brute force collision detection...")
    print()

    # Test configurations: different boid counts
    boid_counts = [50, 100, 200, 500]
    frames_per_test = 300

    results: list[BenchmarkResult] = []

    for boid_count in boid_counts:
        print(f"Testing {boid_count} boids (brute force)...", end=" ", flush=True)
        result = benchmark_simulation(
            boid_count=boid_count,
            use_spatial_grid=False,
            frames_to_test=frames_per_test,
        )
        results.append(result)
        print(f"Done! Avg FPS: {result.avg_fps:.2f}")

        print(f"Testing {boid_count} boids (spatial grid)...", end=" ", flush=True)
        result = benchmark_simulation(
            boid_count=boid_count,
            use_spatial_grid=True,
            frames_to_test=frames_per_test,
        )
        results.append(result)
        print(f"Done! Avg FPS: {result.avg_fps:.2f}")
        print()

    # Display results
    print_results(results)
    calculate_speedup(results)

    print("\nBenchmark complete!")


if __name__ == "__main__":
    main()
