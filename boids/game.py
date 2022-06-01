import numpy as np
import pygame as pg

from boids.boid_vs_boundary import boid_vs_boundary
from boids.boids import Boid
from boids.flock_rules import avoid_other_boids, flock_rules
from boids.options import BoidOptions, ScreenOptions
from boids.predator import Predator

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
        self.boid_list = pg.sprite.Group()
        self.all_sprites_list = pg.sprite.Group()

        # Create the boid sprites
        for _ in range(boid_opts.num_boids):
            boid = Boid(
                pos=pg.Vector2(
                    rng.integers(
                        0,
                        screen_opts.winsize,
                        size=2,
                    ).tolist(),
                ),
                vel=pg.Vector2(
                    rng.uniform(
                        -boid_opts.max_speed,
                        boid_opts.max_speed,
                        size=2,
                    ).tolist(),
                ),
                color=rng.integers(30, 255, 3).tolist(),
                size=20,
                width=20,
                height=20,
            )
            boid.speed_limit(boid_opts.max_speed)

            self.boid_list.add(boid)
            self.all_sprites_list.add(boid)

        # Create the predator
        self.predator = Predator(
            pos=pg.Vector2(screen_opts.winsize) / 2,
            vel=pg.Vector2(0, 0),
        )
        self.all_sprites_list.add(self.predator)

    def process_events(self):
        """Process all of the events. Return a "True" if we need
        to close the window."""

        for event in pg.event.get():
            if event.type == pg.QUIT or (
                event.type == pg.KEYUP and event.key == pg.K_ESCAPE
            ):
                return True
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.__init__(
                        screen_opts=self.screen_opts,
                        boid_opts=self.boid_opts,
                    )

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
                    self.boid_list,
                    cohesion_factor=boid_opts.cohesion_factor,
                    separation=boid_opts.separation,
                    avoid_factor=boid_opts.avoid_factor,
                    alignment_factor=boid_opts.alignment_factor,
                    visual_range=boid_opts.visual_range,
                )

                # Apply movement rules for boids relative to the predator
                flock_rules(
                    boid,
                    [self.predator],
                    cohesion_factor=boid_opts.cohesion_factor * -2,
                    separation=boid_opts.separation * 2,
                    avoid_factor=boid_opts.avoid_factor * 1.2,
                    alignment_factor=boid_opts.alignment_factor * -1.5,
                    visual_range=boid_opts.visual_range * 10,
                )

                boid.speed_limit(boid_opts.max_speed)
                boid_vs_boundary(
                    boid,
                    boundary_type=screen_opts.boundary_type,
                    window_size=screen_opts.winsize,
                )

            # See if the predator boid has collided with anything.
            boid_hit_list = pg.sprite.spritecollide(
                self.predator,
                self.boid_list,
                True,
            )

            # Check the list of collisions.
            for boid in boid_hit_list:
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
