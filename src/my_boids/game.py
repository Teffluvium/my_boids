import numpy as np
import pygame as pg

from my_boids.boid_vs_boundary import boid_vs_boundary
from my_boids.boids import Boid
from my_boids.flock_rules import flock_rules, react_to_predator
from my_boids.options import BoidOptions, ScreenOptions
from my_boids.performance import PerformanceMonitor
from my_boids.predator import Predator
from my_boids.spatial_grid import SpatialGrid

rng = np.random.default_rng()


class Game:
    """This class represents an instance of the game. If we need to
    reset the game we'd just need to create a new instance of this
    class."""

    def __init__(
        self,
        screen_opts: ScreenOptions | None = None,
        boid_opts: BoidOptions | None = None,
        use_spatial_grid: bool = False,
        show_metrics: bool = True,
        enable_profiling: bool = True,
    ):
        """Constructor. Create all our attributes and initialize the game.

        Args:
            screen_opts (ScreenOptions | None): Screen configuration options.
            boid_opts (BoidOptions | None): Boid behavior configuration options.
            use_spatial_grid (bool): Whether to use spatial partitioning for
                performance optimization. Defaults to False because at typical
                scales (<300 boids), the overhead outweighs the benefits.
            show_metrics (bool): Whether to display performance metrics on screen.
                Defaults to True.
            enable_profiling (bool): Whether to enable performance profiling.
                Defaults to True.
        """
        self.screen_opts = screen_opts if screen_opts else ScreenOptions.from_config()
        self.boid_opts = boid_opts if boid_opts else BoidOptions.from_config()
        self.use_spatial_grid = use_spatial_grid
        self.show_metrics = show_metrics

        self.score = 0
        self.game_over = False

        # Create sprite lists
        self.boid_list: pg.sprite.Group[Boid] = pg.sprite.Group()
        self.all_sprites_list: pg.sprite.Group = pg.sprite.Group()

        # Create spatial grid for performance optimization
        # Cell size is set to visual range for optimal performance
        self.spatial_grid: SpatialGrid | None
        if self.use_spatial_grid:
            self.spatial_grid = SpatialGrid(cell_size=float(self.boid_opts.visual_range))
        else:
            self.spatial_grid = None

        # Create performance monitor
        self.performance = PerformanceMonitor(enabled=enable_profiling)

        # Initialize sprites
        self._initialize_sprites()

    def _create_boid(self) -> Boid:
        """Create a single boid with random position, velocity, and color.

        Returns:
            Boid: A newly created boid with random attributes.
        """
        screen_opts = self.screen_opts
        boid_opts = self.boid_opts

        # Generate random position and velocity
        pos_array = rng.integers(0, screen_opts.winsize, size=2)
        vel_array = rng.uniform(-boid_opts.max_speed, boid_opts.max_speed, size=2)
        color_array = rng.integers(30, 255, 3)

        boid = Boid(
            pos=pg.Vector2(float(pos_array[0]), float(pos_array[1])),
            vel=pg.Vector2(float(vel_array[0]), float(vel_array[1])),
            color=pg.Color(int(color_array[0]), int(color_array[1]), int(color_array[2])),
            size=20,
            width=20,
            height=20,
        )
        boid.speed_limit(boid_opts.max_speed)
        return boid

    def _create_predator(self) -> Predator:
        """Create a predator at the center of the screen.

        Returns:
            Predator: A newly created predator.
        """
        screen_opts = self.screen_opts
        return Predator(
            pos=pg.Vector2(float(screen_opts.winsize[0]) / 2, float(screen_opts.winsize[1]) / 2),
            vel=pg.Vector2(0, 0),
        )

    def _initialize_sprites(self) -> None:
        """Initialize all sprites (boids and predator) for the game."""
        # Create the boid sprites
        for _ in range(self.boid_opts.num_boids):
            boid = self._create_boid()
            self.boid_list.add(boid)
            self.all_sprites_list.add(boid)

        # Create the predator
        self.predator = self._create_predator()
        self.all_sprites_list.add(self.predator)

    def reset(self) -> None:
        """Reset the game to initial state."""
        # Reset game state
        self.score = 0
        self.game_over = False

        # Clear sprite lists
        self.boid_list.empty()
        self.all_sprites_list.empty()

        # Reinitialize sprites
        self._initialize_sprites()

    def process_events(self) -> bool:
        """Process all of the events. Return a "True" if we need
        to close the window."""

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
                return True
            if event.type == pg.MOUSEBUTTONDOWN and self.game_over:
                self.reset()
            if event.type == pg.KEYUP and event.key == pg.K_p:
                # Toggle predator behavior mode between avoid and attract
                if self.boid_opts.predator_behavior_mode == "avoid":
                    self.boid_opts.predator_behavior_mode = "attract"
                else:
                    self.boid_opts.predator_behavior_mode = "avoid"

        return False

    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
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
        """Update positions of all sprites."""
        self.all_sprites_list.update()

    def _apply_boid_movement_rules(self, boid: Boid) -> None:
        """Apply all movement rules to a single boid.

        Args:
            boid (Boid): The boid to apply rules to.
        """
        boid_opts = self.boid_opts
        screen_opts = self.screen_opts

        # Get nearby boids based on visual range
        if self.use_spatial_grid and self.spatial_grid:
            # Use spatial grid for efficient neighbor finding
            nearby_boids = self.spatial_grid.get_nearby_boids(
                boid.pos,
                search_radius=float(boid_opts.visual_range),
            )
        else:
            # Fall back to checking all boids
            nearby_boids = list(self.boid_list)

        # Apply movement rules for boids relative to the flock
        flock_rules(
            boid,
            nearby_boids,
            cohesion_factor=boid_opts.cohesion_factor,
            separation=boid_opts.separation,
            avoid_factor=boid_opts.avoid_factor,
            alignment_factor=boid_opts.alignment_factor,
            visual_range=float(boid_opts.visual_range),
        )

        # Apply predator reaction behavior
        react_to_predator(
            boid,
            self.predator,
            behavior_mode=boid_opts.predator_behavior_mode,
            detection_range=boid_opts.predator_detection_range,
            reaction_strength=boid_opts.predator_reaction_strength,
        )

        # Apply speed limit and boundary constraints
        boid.speed_limit(boid_opts.max_speed)
        boid_vs_boundary(
            boid,
            boundary_type=screen_opts.boundary_type,
            window_size=(screen_opts.winsize[0], screen_opts.winsize[1]),
        )

    def _apply_all_boid_rules(self) -> None:
        """Apply movement rules to all boids in the flock."""
        # Rebuild spatial grid if enabled
        if self.use_spatial_grid and self.spatial_grid:
            self.spatial_grid.clear()
            for boid in self.boid_list:
                self.spatial_grid.insert(boid)

        # Apply rules to each boid
        for boid in self.boid_list:
            self._apply_boid_movement_rules(boid)

    def _handle_predator_collisions(self) -> None:
        """Check for and handle collisions between the predator and boids."""
        # See if the predator has collided with any boids
        boid_hit_list = pg.sprite.spritecollide(
            self.predator,
            self.boid_list,
            True,  # Remove boids on collision
        )

        # Update score for each collision
        for _boid in boid_hit_list:
            self.score += 1
            print(self.score)

    def _check_game_over(self) -> None:
        """Check if the game should end (all boids eaten)."""
        if len(self.boid_list) == 0:
            self.game_over = True

    def display_score(self, screen: pg.Surface):
        """Display the score to the screen.

        Args:
            screen (pg.Surface): Screen on which to draw the text.
        """
        winsize = screen.get_size()
        font = pg.font.SysFont("serif", 25)
        text = font.render(
            f"Score: {self.score}",
            True,
            pg.Color("white"),
        )
        text_rect = text.get_rect()
        text_rect.topright = (winsize[0] - 10, 10)
        screen.blit(text, text_rect)

    def display_predator_mode(self, screen: pg.Surface):
        """Display the current predator behavior mode to the screen.

        Args:
            screen (pg.Surface): Screen on which to draw the text.
        """
        font = pg.font.SysFont("serif", 25)
        mode_text = self.boid_opts.predator_behavior_mode.upper()
        text = font.render(
            f"Predator Mode: {mode_text}",
            True,
            pg.Color("white"),
        )
        text_rect = text.get_rect()
        text_rect.topleft = (10, 10)
        screen.blit(text, text_rect)

    def display_game_over_text(self, screen: pg.Surface):
        """Display "Game Over" text to the screen.

        Args:
            screen (pg.Surface): Screen on which to draw the text.
        """
        winsize = screen.get_size()
        # font = pg.font.Font("Serif", 25)
        font = pg.font.SysFont("serif", 25)
        text = font.render(
            "Game Over, click to restart",
            True,
            pg.Color("white"),
        )
        text_rect = text.get_rect()
        text_rect.center = (winsize[0] // 2, winsize[1] // 2)
        screen.blit(text, text_rect)

    def display_metrics(self, screen: pg.Surface):
        """Display performance metrics on the screen.

        Args:
            screen (pg.Surface): Screen on which to draw the metrics.
        """
        font = pg.font.SysFont("monospace", 14)
        y_offset = 10

        # Get performance data
        fps = self.performance.get_fps()
        avg_frame_time = self.performance.get_avg_frame_time()

        # Create metrics lines
        metrics = [
            f"FPS: {fps:.1f}",
            f"Frame: {avg_frame_time:.2f}ms",
            f"Boids: {len(self.boid_list)}",
        ]

        # Add spatial grid stats if enabled
        if self.use_spatial_grid and self.spatial_grid:
            cell_count = self.spatial_grid.get_cell_count()
            metrics.append(f"Grid: {cell_count} cells")
            metrics.append("Mode: Spatial")
        else:
            metrics.append("Mode: Brute Force")

        # Add timing breakdown if available
        if self.performance.current_metrics:
            m = self.performance.current_metrics
            metrics.append(f"Update: {m.update_time * 1000:.2f}ms")
            metrics.append(f"Logic: {m.logic_time * 1000:.2f}ms")
            metrics.append(f"Collision: {m.collision_time * 1000:.2f}ms")
            metrics.append(f"Render: {m.render_time * 1000:.2f}ms")

        # Render each line
        for line in metrics:
            text = font.render(line, True, pg.Color("green"))
            screen.blit(text, (10, y_offset))
            y_offset += 18

    def display_frame(self, screen: pg.Surface):
        """Display everything to the screen for the game."""
        self.performance.start_operation()

        screen.fill(pg.Color("black"))

        if self.game_over:
            self.display_game_over_text(screen)

        if not self.game_over:
            self.all_sprites_list.draw(screen)
            self.display_score(screen)
            self.display_predator_mode(screen)

            # Display performance metrics if enabled
            if self.show_metrics:
                self.display_metrics(screen)

        pg.display.flip()
        self.performance.end_operation("render")
        self.performance.end_frame()
