from collections.abc import Callable

import numpy as np
import pygame as pg

from my_boids.boid_vs_boundary import boid_vs_boundary
from my_boids.boids import Boid
from my_boids.flock_rules import flock_rules, react_to_predator
from my_boids.hud import (
    draw_frame,
    draw_game_over,
    draw_metrics,
    draw_predator_attack_mode,
    draw_predator_mode,
    draw_score,
)
from my_boids.options import (
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    PREDATOR_MODE_ATTRACT,
    PREDATOR_MODE_AVOID,
    BoidOptions,
    PredatorAttackMode,
    PredatorOptions,
    ScreenOptions,
)
from my_boids.performance import PerformanceMonitor
from my_boids.predator import Predator
from my_boids.predator_targeting import (
    target_flock_center,
    target_most_isolated_bird,
    target_mouse_cursor,
    target_nearest_bird,
)
from my_boids.spatial_grid import SpatialGrid

rng = np.random.default_rng()


class Game:
    """Central controller for simulation state and orchestration."""

    def __init__(
        self,
        screen_opts: ScreenOptions | None = None,
        boid_opts: BoidOptions | None = None,
        predator_opts: PredatorOptions | None = None,
        use_spatial_grid: bool = False,
        show_metrics: bool = True,
        enable_profiling: bool = True,
    ):
        self.screen_opts = screen_opts if screen_opts else ScreenOptions.from_config()
        self.boid_opts = boid_opts if boid_opts else BoidOptions.from_config()
        self.predator_opts = predator_opts if predator_opts else PredatorOptions.from_config()
        self.use_spatial_grid = use_spatial_grid
        self.show_metrics = show_metrics

        self.score = 0
        self.game_over = False

        self.boid_list: pg.sprite.Group[Boid] = pg.sprite.Group()
        self.all_sprites_list: pg.sprite.Group = pg.sprite.Group()

        self.spatial_grid: SpatialGrid | None
        if self.use_spatial_grid:
            self.spatial_grid = SpatialGrid(cell_size=float(self.boid_opts.visual_range))
        else:
            self.spatial_grid = None

        self.performance = PerformanceMonitor(enabled=enable_profiling)

        self._initialize_sprites()
        self._predator_attack_mode_strategies = self._build_predator_attack_mode_strategies()

    def _build_predator_attack_mode_strategies(
        self,
    ) -> dict[PredatorAttackMode, Callable[[], pg.Vector2]]:
        """Build map of predator attack mode handlers."""
        return {
            PREDATOR_ATTACK_MODE_MOUSE: target_mouse_cursor,
            PREDATOR_ATTACK_MODE_CENTER: lambda: target_flock_center(
                list(self.boid_list), self.predator.pos
            ),
            PREDATOR_ATTACK_MODE_NEAREST: lambda: target_nearest_bird(
                self.predator.pos,
                list(self.boid_list),
                self.predator.pos,
            ),
            PREDATOR_ATTACK_MODE_ISOLATED: lambda: target_most_isolated_bird(
                list(self.boid_list), self.predator.pos
            ),
        }

    def _create_boid(self) -> Boid:
        screen_opts = self.screen_opts
        boid_opts = self.boid_opts

        pos_array = rng.integers(0, screen_opts.winsize, size=2)
        vel_array = rng.uniform(-boid_opts.max_speed, boid_opts.max_speed, size=2)
        color_array = rng.integers(30, 255, 3)

        boid = Boid(
            pos=pg.Vector2(float(pos_array[0]), float(pos_array[1])),
            vel=pg.Vector2(float(vel_array[0]), float(vel_array[1])),
            color=pg.Color(int(color_array[0]), int(color_array[1]), int(color_array[2])),
            size=boid_opts.size,
            width=boid_opts.size,
            height=boid_opts.size,
        )
        boid.speed_limit(boid_opts.max_speed)
        return boid

    def _create_predator(self) -> Predator:
        screen_opts = self.screen_opts
        return Predator(
            pos=pg.Vector2(float(screen_opts.winsize[0]) / 2, float(screen_opts.winsize[1]) / 2),
            vel=pg.Vector2(0, 0),
        )

    def _initialize_sprites(self) -> None:
        for _ in range(self.boid_opts.num_boids):
            boid = self._create_boid()
            self.boid_list.add(boid)
            self.all_sprites_list.add(boid)

        self.predator = self._create_predator()
        self.all_sprites_list.add(self.predator)

    def reset(self) -> None:
        self.score = 0
        self.game_over = False
        self.boid_list.empty()
        self.all_sprites_list.empty()
        self._initialize_sprites()

    def process_events(self, events: list | None = None) -> bool:
        if events is None:
            events = pg.event.get()

        for event in events:
            if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
                return True
            if event.type == pg.MOUSEBUTTONDOWN and self.game_over:
                self.reset()
            if event.type == pg.KEYUP and event.key == pg.K_p:
                if self.predator_opts.predator_behavior_mode == PREDATOR_MODE_AVOID:
                    self.predator_opts.predator_behavior_mode = PREDATOR_MODE_ATTRACT
                else:
                    self.predator_opts.predator_behavior_mode = PREDATOR_MODE_AVOID

        return False

    def update_boid_options(self, new_opts: BoidOptions) -> None:
        old_count = len(self.boid_list)
        old_size = self.boid_opts.size
        self.boid_opts = new_opts

        if new_opts.size != old_size:
            for boid in self.boid_list:
                size = new_opts.size
                boid.size = size
                boid.image = pg.Surface([size, size])
                boid.image.fill(pg.Color("black"))
                boid.image.set_colorkey(pg.Color("black"))
                pg.draw.ellipse(boid.image, boid.color, [0, 0, size, size])
                boid.rect = boid.image.get_rect()
                boid.rect.center = boid.pos.xy  # type: ignore[assignment]

        target_count = new_opts.num_boids
        if target_count > old_count:
            for _ in range(target_count - old_count):
                boid = self._create_boid()
                self.boid_list.add(boid)
                self.all_sprites_list.add(boid)
        elif target_count < old_count:
            for boid in list(self.boid_list)[target_count:]:
                boid.kill()

        if self.spatial_grid is not None:
            self.spatial_grid = SpatialGrid(cell_size=float(new_opts.visual_range))

    def update_predator_options(self, new_opts: PredatorOptions) -> None:
        self.predator_opts = new_opts

    def run_logic(self):
        if not self.game_over:
            self.performance.start_operation()
            self._update_sprites()
            self.performance.end_operation("update")

            self.performance.start_operation()
            self._apply_all_boid_rules()
            self.performance.end_operation("logic")

            self.performance.start_operation()
            self._handle_predator_collisions()
            self.performance.end_operation("collision")

            self._check_game_over()

    def _update_sprites(self) -> None:
        self.boid_list.update()
        self.predator.update(self._get_predator_target())

    def _get_predator_target(self) -> pg.Vector2:
        mode = self.predator_opts.predator_attack_mode
        strategy = self._predator_attack_mode_strategies.get(mode, target_mouse_cursor)
        return strategy()

    def _apply_boid_movement_rules(self, boid: Boid) -> None:
        boid_opts = self.boid_opts
        predator_opts = self.predator_opts
        screen_opts = self.screen_opts

        if self.use_spatial_grid and self.spatial_grid:
            nearby_boids = self.spatial_grid.get_nearby_boids(
                boid.pos,
                search_radius=float(boid_opts.visual_range),
            )
        else:
            nearby_boids = list(self.boid_list)

        flock_rules(
            boid,
            nearby_boids,
            cohesion_factor=boid_opts.cohesion_factor,
            separation=boid_opts.separation,
            avoid_factor=boid_opts.avoid_factor,
            alignment_factor=boid_opts.alignment_factor,
            visual_range=float(boid_opts.visual_range),
        )

        react_to_predator(
            boid,
            self.predator.pos,
            behavior_mode=predator_opts.predator_behavior_mode,
            detection_range=predator_opts.predator_detection_range,
            reaction_strength=predator_opts.predator_reaction_strength,
        )

        boid.speed_limit(boid_opts.max_speed)
        boid_vs_boundary(
            boid,
            boundary_type=screen_opts.boundary_type,
            window_size=(screen_opts.winsize[0], screen_opts.winsize[1]),
        )

    def _apply_all_boid_rules(self) -> None:
        if self.use_spatial_grid and self.spatial_grid:
            self.spatial_grid.clear()
            for boid in self.boid_list:
                self.spatial_grid.insert(boid)

        for boid in self.boid_list:
            self._apply_boid_movement_rules(boid)

    def _handle_predator_collisions(self) -> None:
        boid_hit_list = pg.sprite.spritecollide(
            self.predator,
            self.boid_list,
            True,
        )

        for _boid in boid_hit_list:
            self.score += 1

    def _check_game_over(self) -> None:
        if len(self.boid_list) == 0:
            self.game_over = True

    def display_score(self, screen: pg.Surface):
        draw_score(screen, self.score)

    def display_predator_mode(self, screen: pg.Surface):
        draw_predator_mode(screen, self.predator_opts.predator_behavior_mode)

    def display_predator_attack_mode(self, screen: pg.Surface):
        draw_predator_attack_mode(screen, self.predator_opts.predator_attack_mode)

    def display_game_over_text(self, screen: pg.Surface):
        draw_game_over(screen)

    def display_metrics(self, screen: pg.Surface):
        draw_metrics(
            screen,
            self.performance,
            len(self.boid_list),
            self.use_spatial_grid,
            self.spatial_grid,
        )

    def display_frame(self, screen: pg.Surface, flip: bool = True):
        self.performance.start_operation()
        draw_frame(
            screen,
            self.all_sprites_list,
            self.score,
            self.predator_opts.predator_behavior_mode,
            self.predator_opts.predator_attack_mode,
            self.game_over,
            self.performance,
            self.show_metrics,
            len(self.boid_list),
            self.use_spatial_grid,
            self.spatial_grid,
        )
        if flip:
            pg.display.flip()
        self.performance.end_operation("render")
        self.performance.end_frame()
