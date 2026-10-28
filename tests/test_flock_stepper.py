"""Behavioral coverage for the flock rules boundary."""

import random
from collections.abc import Sequence
from dataclasses import FrozenInstanceError

import pygame as pg
import pytest

from my_boids.boids import Boid
from my_boids.flock_rules import ClassicFlocking
from my_boids.flock_stepper import FlockStats, FlockStepper
from my_boids.options import BoidOptions, BoundaryType, PredatorOptions, ScreenOptions


@pytest.mark.parametrize("algorithm", [None, ClassicFlocking()])
@pytest.mark.parametrize("use_grid", [False, True])
def test_rules_preserve_sequential_velocity_updates(algorithm, use_grid):
    boids = [Boid(pos=(100, 100), vel=(0, 0)), Boid(pos=(110, 100), vel=(2, 0))]
    options = BoidOptions(
        cohesion_factor=0.005, alignment_factor=0.01, avoid_factor=0.05, visual_range=100
    )

    FlockStepper(algorithm=algorithm, use_spatial_grid=use_grid).apply(
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


class NeighborSignal:
    """Encode ordered neighbor positions and membership into observable velocity."""

    def __init__(self, radius: float | None, strength: float = 0.001) -> None:
        self.radius = radius
        self.strength = strength

    def neighbor_radius(self, options: BoidOptions) -> float | None:
        return self.radius

    def apply_to_boid(self, boid: Boid, neighbors: Sequence[Boid], *, options: BoidOptions) -> None:
        boid.vel += self.strength * pg.Vector2(
            sum((index + 1) * other.pos.x for index, other in enumerate(neighbors)),
            len(neighbors),
        )


@pytest.mark.parametrize("use_grid", [False, True])
@pytest.mark.parametrize("strength", [0.001, 0.002])
@pytest.mark.parametrize(
    "radius, positions, signal",
    [
        (100, [400, 500, 350, 505], (2450, 3)),
        (None, [400, 500, 350, 505], (4470, 4)),
        (0, [400, 400, 401], (1200, 2)),
        (1e-320, [400, 400, 401], (1200, 2)),
        (1e308, [400, 500, 350, 505], (4470, 4)),
        (0, [400], (400, 1)),
    ],
)
def test_custom_algorithm_receives_exact_ordered_neighbors(
    use_grid, strength, radius, positions, signal
):
    boids = [Boid(pos=(position, 300), vel=(0, 0)) for position in positions]
    stepper = FlockStepper(algorithm=NeighborSignal(radius, strength), use_spatial_grid=use_grid)

    stepper.apply(
        boids,
        predator_pos=pg.Vector2(750, 550),
        boid_opts=BoidOptions(visual_range=20),
        predator_opts=PredatorOptions(predator_detection_range=100),
        screen_opts=ScreenOptions(),
    )

    assert tuple(boids[0].vel) == pytest.approx(tuple(pg.Vector2(signal) * strength))
    assert [boid.pos.x for boid in boids] == positions
    assert stepper.stats().boids_processed == len(boids)
    assert stepper.stats().spatial_grid_enabled is use_grid


@pytest.mark.parametrize("use_grid", [False, True])
@pytest.mark.parametrize("radius", [-1, float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("empty", [False, True])
def test_invalid_algorithm_radius_is_rejected_before_mutation(use_grid, radius, empty):
    boids = [] if empty else [Boid(pos=(805, 300), vel=(10, 0))]
    algorithm = NeighborSignal(100)
    stepper = FlockStepper(algorithm=algorithm, use_spatial_grid=use_grid)

    def apply() -> None:
        stepper.apply(
            boids,
            predator_pos=pg.Vector2(750, 550),
            boid_opts=BoidOptions(),
            predator_opts=PredatorOptions(predator_detection_range=100),
            screen_opts=ScreenOptions(boundary_type=BoundaryType.WRAP),
        )

    apply()
    before = [(boid.pos.copy(), boid.vel.copy()) for boid in boids]
    prior_stats = stepper.stats()
    algorithm.radius = radius

    with pytest.raises(ValueError, match="radius"):
        apply()

    assert [(boid.pos, boid.vel) for boid in boids] == before
    assert stepper.stats() == prior_stats


@pytest.mark.parametrize("use_grid", [False, True])
@pytest.mark.parametrize("radius", [None, 0, 100])
def test_custom_algorithm_handles_empty_population(use_grid, radius):
    stepper = FlockStepper(algorithm=NeighborSignal(radius), use_spatial_grid=use_grid)

    stepper.apply(
        [],
        predator_pos=pg.Vector2(750, 550),
        boid_opts=BoidOptions(),
        predator_opts=PredatorOptions(),
        screen_opts=ScreenOptions(),
    )

    assert stepper.stats() == FlockStats(use_grid, 0, 0 if use_grid else None)


@pytest.mark.parametrize("use_grid", [False, True])
@pytest.mark.parametrize(
    "radius, positions, expected_velocities, expected_positions",
    [
        (20, [400, 410], [5, 8.5], [400, 410]),
        (20, [805, 10], [3, 7.5], [5, 10]),
        (20, [-5, 790], [3, 7.5], [795, 790]),
        (None, [805, 10], [5, 8.5], [5, 10]),
    ],
)
def test_custom_algorithm_observes_sequential_updates_and_wraps(
    use_grid, radius, positions, expected_velocities, expected_positions
):
    class SequentialAlignment(NeighborSignal):
        def apply_to_boid(
            self, boid: Boid, neighbors: Sequence[Boid], *, options: BoidOptions
        ) -> None:
            boid.vel += self.strength * sum((other.vel for other in neighbors), pg.Vector2())

    boids = [
        Boid(pos=(position, 300), vel=(velocity, 0))
        for position, velocity in zip(positions, [2, 4], strict=True)
    ]
    FlockStepper(
        algorithm=SequentialAlignment(radius, strength=0.5), use_spatial_grid=use_grid
    ).apply(
        boids,
        predator_pos=pg.Vector2(750, 550),
        boid_opts=BoidOptions(),
        predator_opts=PredatorOptions(predator_detection_range=100),
        screen_opts=ScreenOptions(boundary_type=BoundaryType.WRAP),
    )

    assert [boid.vel.x for boid in boids] == pytest.approx(expected_velocities)
    assert [boid.vel.y for boid in boids] == [0, 0]
    assert [boid.pos.x for boid in boids] == expected_positions


@pytest.mark.parametrize("use_grid", [False, True])
def test_custom_algorithm_radius_uses_current_options_once_per_pass(use_grid):
    requested_ranges: list[int] = []

    class CurrentRangeSignal(NeighborSignal):
        def neighbor_radius(self, options: BoidOptions) -> float:
            requested_ranges.append(options.visual_range)
            return options.visual_range

    stepper = FlockStepper(algorithm=CurrentRangeSignal(None), use_spatial_grid=use_grid)
    options = BoidOptions(visual_range=20)
    boids = [Boid(pos=(400, 300), vel=(0, 0)), Boid(pos=(460, 300), vel=(0, 0))]

    def apply() -> None:
        stepper.apply(
            boids,
            predator_pos=pg.Vector2(750, 550),
            boid_opts=options,
            predator_opts=PredatorOptions(predator_detection_range=100),
            screen_opts=ScreenOptions(),
        )

    apply()
    assert tuple(boids[0].vel) == pytest.approx((0.4, 0.001))
    options.visual_range = 100
    for boid in boids:
        boid.vel.update(0, 0)
    apply()
    assert tuple(boids[0].vel) == pytest.approx((1.32, 0.002))

    boids.clear()
    apply()
    assert stepper.stats() == FlockStats(use_grid, 0, 0 if use_grid else None)
    options = BoidOptions(visual_range=20)
    boids = [Boid(pos=(200, 300), vel=(0, 0)), Boid(pos=(220, 300), vel=(0, 0))]
    apply()
    assert tuple(boids[0].vel) == pytest.approx((0.64, 0.002))
    assert requested_ranges == [20, 100, 100, 20]


@pytest.mark.parametrize("use_grid", [False, True])
@pytest.mark.parametrize(
    "visual_range, separation, distance, expected",
    [
        (20, 50, 20, (-1, 3)),
        (20, 50, 50, (0, 2)),
        (100, 20, 100, (0, 2)),
        (100, 20, 20, (0.119, 1.88219)),
    ],
)
def test_classic_rules_preserve_strict_distance_thresholds(
    use_grid, visual_range, separation, distance, expected
):
    boids = [Boid(pos=(400, 300), vel=(0, 0)), Boid(pos=(400 + distance, 300), vel=(2, 0))]
    FlockStepper(use_spatial_grid=use_grid).apply(
        boids,
        predator_pos=pg.Vector2(750, 550),
        boid_opts=BoidOptions(
            cohesion_factor=0.005,
            alignment_factor=0.01,
            avoid_factor=0.05,
            visual_range=visual_range,
            separation=separation,
        ),
        predator_opts=PredatorOptions(predator_detection_range=100),
        screen_opts=ScreenOptions(),
    )

    assert [boid.vel.x for boid in boids] == pytest.approx(expected, abs=1e-9, rel=1e-9)
    assert [boid.vel.y for boid in boids] == [0, 0]


@pytest.mark.parametrize(
    "algorithm_factory",
    [
        ClassicFlocking,
        lambda: NeighborSignal(100),
        lambda: NeighborSignal(None),
        lambda: NeighborSignal(0),
    ],
    ids=["classic", "local", "whole-flock", "coincident"],
)
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
def test_backends_agree_over_multiple_frames(algorithm_factory, boundary, positions):
    full_scan = [Boid(pos=position, vel=(2, -1)) for position in positions]
    indexed = [Boid(pos=position, vel=(2, -1)) for position in positions]
    full_stepper = FlockStepper(algorithm=algorithm_factory())
    grid_stepper = FlockStepper(algorithm=algorithm_factory(), use_spatial_grid=True)
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
