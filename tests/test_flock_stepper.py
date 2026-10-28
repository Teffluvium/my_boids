"""Behavioral coverage for the flock rules boundary."""

import random
from dataclasses import FrozenInstanceError

import pygame as pg
import pytest

from my_boids.boids import Boid
from my_boids.flock_stepper import FlockStats, FlockStepper
from my_boids.options import BoidOptions, BoundaryType, PredatorOptions, ScreenOptions


def test_rules_preserve_sequential_velocity_updates():
    boids = [Boid(pos=(100, 100), vel=(0, 0)), Boid(pos=(110, 100), vel=(2, 0))]
    options = BoidOptions(
        cohesion_factor=0.005, alignment_factor=0.01, avoid_factor=0.05, visual_range=100
    )

    FlockStepper().apply(
        boids,
        predator_pos=pg.Vector2(750, 550),
        boid_opts=options,
        predator_opts=PredatorOptions(predator_detection_range=100),
        screen_opts=ScreenOptions(),
    )

    assert tuple(boids[0].pos) == (100, 100)
    assert tuple(boids[1].pos) == (110, 100)
    assert tuple(boids[0].vel) == pytest.approx((-0.4255, 0), abs=1e-9, rel=1e-9)
    assert tuple(boids[1].vel) == pytest.approx((2.421245, 0), abs=1e-9, rel=1e-9)


@pytest.mark.parametrize("boundary", [BoundaryType.BOUNCE, BoundaryType.WRAP])
@pytest.mark.parametrize(
    "positions",
    [
        [(300, 300), (330, 300), (600, 500)],
        [(805, 300), (10, 300), (600, 500)],
        [(-20, -20), (0, 0), (20, 0), (40, 0), (50, 0)],
        [(0, 0), (799, 599)],
        [(400, 300)],
        [],
    ],
)
def test_backends_agree_over_multiple_frames(boundary, positions):
    full_scan = [Boid(pos=position, vel=(2, -1)) for position in positions]
    indexed = [Boid(pos=position, vel=(2, -1)) for position in positions]
    full_stepper = FlockStepper()
    grid_stepper = FlockStepper(use_spatial_grid=True)
    options = BoidOptions(visual_range=20, separation=50)
    screen_options = ScreenOptions(boundary_type=boundary)

    for _frame in range(20):
        for boids, stepper in ((full_scan, full_stepper), (indexed, grid_stepper)):
            for boid in boids:
                boid.update()
            stepper.apply(
                boids,
                predator_pos=pg.Vector2(750, 550),
                boid_opts=options,
                predator_opts=PredatorOptions(predator_detection_range=100),
                screen_opts=screen_options,
            )

        for expected, actual in zip(full_scan, indexed, strict=True):
            assert tuple(actual.pos) == pytest.approx(tuple(expected.pos), abs=1e-9, rel=1e-9)
            assert tuple(actual.vel) == pytest.approx(tuple(expected.vel), abs=1e-9, rel=1e-9)


@pytest.mark.parametrize("use_grid", [False, True])
def test_current_inputs_replace_prior_options_and_population(use_grid):
    stepper = FlockStepper(use_spatial_grid=use_grid)

    def apply(target: FlockStepper, boids: list[Boid], options: BoidOptions) -> None:
        target.apply(
            boids,
            predator_pos=pg.Vector2(750, 550),
            predator_opts=PredatorOptions(predator_detection_range=100),
            screen_opts=ScreenOptions(),
            boid_opts=options,
        )

    apply(
        stepper,
        [Boid(pos=(200, 200), vel=(0, 0)), Boid(pos=(205, 200), vel=(0, 0))],
        BoidOptions(visual_range=20),
    )
    prior_stats = stepper.stats()
    apply(stepper, [], BoidOptions(visual_range=100))
    assert stepper.stats() == FlockStats(use_grid, 0, 0 if use_grid else None)
    assert prior_stats.boids_processed == 2

    current = [Boid(pos=(400, 300), vel=(0, 0)), Boid(pos=(460, 300), vel=(0, 0))]
    reference = [Boid(pos=(400, 300), vel=(0, 0)), Boid(pos=(460, 300), vel=(0, 0))]
    options = BoidOptions(visual_range=100)
    apply(stepper, current, options)
    apply(FlockStepper(), reference, options)
    assert current[0].vel.x > 0
    for actual, expected in zip(current, reference, strict=True):
        assert tuple(actual.vel) == pytest.approx(tuple(expected.vel), abs=1e-9, rel=1e-9)

    options.visual_range = 20
    for boid in current:
        boid.vel.update(0, 0)
    apply(stepper, current, options)
    assert all(boid.vel == pg.Vector2() for boid in current)


@pytest.mark.parametrize("use_grid", [False, True])
def test_diagnostics_are_immutable_last_pass_snapshots(use_grid):
    stepper = FlockStepper(use_spatial_grid=use_grid)
    initial = stepper.stats()
    assert initial == FlockStats(use_grid, 0, 0 if use_grid else None)
    boids = [Boid(pos=(100, 100), vel=(0, 0)), Boid(pos=(200, 200), vel=(0, 0))]
    stepper.apply(
        boids,
        predator_pos=pg.Vector2(750, 550),
        boid_opts=BoidOptions(visual_range=20),
        predator_opts=PredatorOptions(),
        screen_opts=ScreenOptions(),
    )
    completed = stepper.stats()
    boids.clear()

    assert initial.boids_processed == 0
    assert completed == FlockStats(use_grid, 2, 2 if use_grid else None)
    assert stepper.stats() == completed
    with pytest.raises(FrozenInstanceError):
        completed.__setattr__("boids_processed", 99)


@pytest.mark.parametrize("use_grid", [False, True])
def test_speed_limit_precedes_boundary_steering(use_grid):
    boid = Boid(pos=(5, 300), vel=(10, 0))
    FlockStepper(use_spatial_grid=use_grid).apply(
        [boid],
        predator_pos=pg.Vector2(750, 550),
        boid_opts=BoidOptions(max_speed=5),
        predator_opts=PredatorOptions(predator_detection_range=100),
        screen_opts=ScreenOptions(),
    )

    assert tuple(boid.pos) == (5, 300)
    assert tuple(boid.vel) == (6, 0)


@pytest.mark.parametrize("use_grid", [False, True])
@pytest.mark.parametrize("mode, direction", [("avoid", 1), ("attract", -1)])
def test_predator_reaction_at_detection_threshold(use_grid, mode, direction):
    boid = Boid(pos=(400, 300), vel=(0, 0))
    FlockStepper(use_spatial_grid=use_grid).apply(
        [boid],
        predator_pos=pg.Vector2(300, 300),
        boid_opts=BoidOptions(boid_avoid_mode=mode),
        predator_opts=PredatorOptions(predator_detection_range=100, predator_reaction_strength=0.5),
        screen_opts=ScreenOptions(),
    )

    assert tuple(boid.vel) == pytest.approx((direction * 0.5 / 101**2, 0), abs=1e-9, rel=1e-9)


def test_coincident_predator_reaction_consumes_same_random_draws_for_both_backends():
    original_random_state = random.getstate()
    velocities = []
    random_states = []
    try:
        for use_grid in (False, True):
            random.seed(36)
            boids = [Boid(pos=(400, 300), vel=(0, 0)), Boid(pos=(400, 300), vel=(0, 0))]
            FlockStepper(use_spatial_grid=use_grid).apply(
                boids,
                predator_pos=pg.Vector2(400, 300),
                boid_opts=BoidOptions(),
                predator_opts=PredatorOptions(),
                screen_opts=ScreenOptions(),
            )
            velocities.append([tuple(boid.vel) for boid in boids])
            random_states.append(random.getstate())
        for expected, actual in zip(velocities[0], velocities[1], strict=True):
            assert actual == pytest.approx(expected, abs=1e-9, rel=1e-9)
        assert random_states[0] == random_states[1]
        assert velocities[0][0] != (0, 0)
    finally:
        random.setstate(original_random_state)
