"""Apply flock rules while owning neighbor selection and index lifecycle."""

from collections.abc import Sequence
from dataclasses import dataclass

import pygame as pg

from my_boids.boid_vs_boundary import boid_vs_boundary
from my_boids.boids import Boid
from my_boids.flock_rules import flock_rules, react_to_predator
from my_boids.options import BoidOptions, BoundaryType, PredatorOptions, ScreenOptions
from my_boids.spatial_grid import SpatialGrid


@dataclass(frozen=True)
class FlockStats:
    """Immutable diagnostics for the last completed rules pass."""

    spatial_grid_enabled: bool
    boids_processed: int
    occupied_cells: int | None


class FlockStepper:
    """Mutate boids sequentially without owning their population or movement."""

    def __init__(self, *, use_spatial_grid: bool = False) -> None:
        self._use_spatial_grid = use_spatial_grid
        self._grid: SpatialGrid | None = None
        self._stats = FlockStats(use_spatial_grid, 0, 0 if use_spatial_grid else None)

    def apply(
        self,
        boids: Sequence[Boid],
        *,
        predator_pos: pg.Vector2,
        boid_opts: BoidOptions,
        predator_opts: PredatorOptions,
        screen_opts: ScreenOptions,
    ) -> None:
        """Apply rules in supplied order using current membership and options."""
        grid = None
        if self._use_spatial_grid:
            cell_size = float(boid_opts.visual_range)
            if self._grid is None or self._grid.cell_size != cell_size:
                self._grid = SpatialGrid(cell_size=cell_size)
            grid = self._grid
            grid.clear()
            for boid in boids:
                grid.insert(boid)

        order = {boid: index for index, boid in enumerate(boids)} if grid is not None else {}
        search_radius = max(float(boid_opts.visual_range), boid_opts.separation)
        for boid in boids:
            if grid is None:
                neighbors = list(boids)
            else:
                neighbors = grid.get_nearby_boids(boid.pos, search_radius)
                neighbors.sort(key=order.__getitem__)

            flock_rules(
                boid,
                neighbors,
                cohesion_factor=boid_opts.cohesion_factor,
                separation=boid_opts.separation,
                avoid_factor=boid_opts.avoid_factor,
                alignment_factor=boid_opts.alignment_factor,
                visual_range=float(boid_opts.visual_range),
            )
            react_to_predator(
                boid,
                predator_pos,
                behavior_mode=boid_opts.boid_avoid_mode,
                detection_range=predator_opts.predator_detection_range,
                reaction_strength=predator_opts.predator_reaction_strength,
            )
            boid.speed_limit(boid_opts.max_speed)
            previous_pos = (
                boid.pos.copy()
                if grid is not None and screen_opts.boundary_type == BoundaryType.WRAP
                else None
            )
            boid_vs_boundary(
                boid,
                boundary_type=screen_opts.boundary_type,
                window_size=(screen_opts.winsize[0], screen_opts.winsize[1]),
            )
            if grid is not None and previous_pos is not None and boid.pos != previous_pos:
                grid.relocate(boid, previous_pos)

        self._stats = FlockStats(
            self._use_spatial_grid,
            len(boids),
            grid.get_cell_count() if grid is not None else None,
        )

    def stats(self) -> FlockStats:
        """Return last-pass diagnostics, not the live population after collisions."""
        return self._stats
