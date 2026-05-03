import numpy as np
import pygame as pg

from my_boids.boid_vs_boundary import boid_vs_boundary
from my_boids.boids import Boid
from my_boids.flock_rules import flock_rules
from my_boids.options import BoidOptions, ScreenOptions
from my_boids.predator import Predator

rng = np.random.default_rng()


class Game:
    """This class represents an instance of the game. If we need to
    reset the game we'd just need to create a new instance of this
    class."""

    def __init__(
        self,
        screen_opts: ScreenOptions = ScreenOptions(),
        boid_opts: BoidOptions = BoidOptions(),
    ):
        """Constructor. Create all our attributes and initialize the game."""
        self.screen_opts = screen_opts
        self.boid_opts = boid_opts

        self.score = 0
        self.game_over = False

        # Create sprite lists
        self.boid_list: pg.sprite.Group[Boid] = pg.sprite.Group()
        self.all_sprites_list: pg.sprite.Group = pg.sprite.Group()

        # Create the boid sprites
        for _ in range(boid_opts.num_boids):
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

            self.boid_list.add(boid)
            self.all_sprites_list.add(boid)

        # Create the predator
        self.predator = Predator(
            pos=pg.Vector2(float(screen_opts.winsize[0]) / 2, float(screen_opts.winsize[1]) / 2),
            vel=pg.Vector2(0, 0),
        )
        self.all_sprites_list.add(self.predator)

    def reset(self) -> None:
        """Reset the game to initial state."""
        # Store options
        screen_opts = self.screen_opts
        boid_opts = self.boid_opts
        
        # Reset game state
        self.score = 0
        self.game_over = False
        
        # Clear sprite lists
        self.boid_list.empty()
        self.all_sprites_list.empty()
        
        # Create new boids
        for _ in range(boid_opts.num_boids):
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

            self.boid_list.add(boid)
            self.all_sprites_list.add(boid)

        # Create new predator
        self.predator = Predator(
            pos=pg.Vector2(float(screen_opts.winsize[0]) / 2, float(screen_opts.winsize[1]) / 2),
            vel=pg.Vector2(0, 0),
        )
        self.all_sprites_list.add(self.predator)

    def process_events(self) -> bool:
        """Process all of the events. Return a "True" if we need
        to close the window."""

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
                return True
            if event.type == pg.MOUSEBUTTONDOWN and self.game_over:
                self.reset()

        return False

    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        screen_opts = self.screen_opts
        boid_opts = self.boid_opts
        if not self.game_over:
            # Move all the sprites
            self.all_sprites_list.update()

            # Apply movement rules to all boids
            for boid in self.boid_list:
                # Apply movement rules for boids relative to the flock
                flock_rules(
                    boid,
                    list(self.boid_list),
                    cohesion_factor=boid_opts.cohesion_factor,
                    separation=boid_opts.separation,
                    avoid_factor=boid_opts.avoid_factor,
                    alignment_factor=boid_opts.alignment_factor,
                    visual_range=float(boid_opts.visual_range),
                )

                # Apply movement rules for boids relative to the predator
                # Note: Predator is treated as a boid for avoidance purposes
                flock_rules(
                    boid,
                    [boid for boid in [self.predator] if isinstance(boid, Boid)],  # type: ignore[misc]
                    cohesion_factor=boid_opts.cohesion_factor * -2,
                    separation=boid_opts.separation * 2,
                    avoid_factor=boid_opts.avoid_factor * 1.2,
                    alignment_factor=boid_opts.alignment_factor * -1.5,
                    visual_range=float(boid_opts.visual_range) * 10,
                )

                boid.speed_limit(boid_opts.max_speed)
                boid_vs_boundary(
                    boid,
                    boundary_type=screen_opts.boundary_type,
                    window_size=(screen_opts.winsize[0], screen_opts.winsize[1]),
                )

            # See if the predator boid has collided with anything.
            boid_hit_list = pg.sprite.spritecollide(
                self.predator,
                self.boid_list,
                True,
            )

            # Check the list of collisions.
            for _boid in boid_hit_list:
                self.score += 1
                print(self.score)
                # You can do something with "boid" here.
                # Print debugging info
                # print(
                #     "\n".join(
                #         [
                #             f"{self.predator.prev_pos  = }",
                #             f"{self.predator.pos       = }",
                #             f"{self.predator.vel       = }",
                #             f"{self.predator.angle     = :.2f}",
                #         ]
                #     )
                # )

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

    def display_frame(self, screen: pg.Surface):
        """Display everything to the screen for the game."""
        screen.fill(pg.Color("black"))

        if self.game_over:
            self.display_game_over_text(screen)

        if not self.game_over:
            self.all_sprites_list.draw(screen)
            self.display_score(screen)

        pg.display.flip()
