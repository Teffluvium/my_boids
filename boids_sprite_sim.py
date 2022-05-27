"""
Boid simulation using PyGame and Sprites
"""

from typing import List

import numpy as np
import pygame as pg

from boids.boid_vs_boundary import BoundaryType, boid_vs_boundary
from boids.boids import Boid
from boids.flock_rules import flock_rules

# --- Global constants ---
SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

# Boid Constants
SIZE = 10
MAX_SPEED = 10
COHESION_FACTOR = 0.005
SEPARATION = 20
AVOID_FACTOR = 0.05
ALIGNMENT_FACTOR = 0.01
VISUAL_RANGE = 100


rng = np.random.default_rng()


# --- Classes ---


class Player(pg.sprite.Sprite):
    """This class represents the player."""

    def __init__(self):
        super().__init__()
        self.image = pg.Surface([20, 20])
        self.image.fill(pg.Color("red"))
        self.rect = self.image.get_rect()

    def update(self):
        """Update the player location."""
        pos = pg.mouse.get_pos()
        self.rect.center = pos


class Game(object):
    """This class represents an instance of the game. If we need to
    reset the game we'd just need to create a new instance of this
    class."""

    def __init__(self):
        """Constructor. Create all our attributes and initialize
        the game."""

        self.score = 0
        self.game_over = False

        # Create sprite lists
        self.block_list = pg.sprite.Group()
        self.all_sprites_list = pg.sprite.Group()

        # Create the boid sprites
        for i in range(50):
            boid = Boid(
                pos=pg.Vector2(
                    rng.integers(0, [SCREEN_WIDTH, SCREEN_HEIGHT], size=2).tolist()
                ),
                vel=pg.Vector2(rng.uniform(-3, 3, 2).tolist()),
                color=rng.integers(30, 255, 3).tolist(),
                size=20,
                width=20,
                height=20,
            )

            self.block_list.add(boid)
            self.all_sprites_list.add(boid)

        # Create the player
        self.player = Player()
        self.all_sprites_list.add(self.player)

    def process_events(self):
        """Process all of the events. Return a "True" if we need
        to close the window."""

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return True
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.game_over:
                    self.__init__()

        return False

    def run_logic(self):
        """
        This method is run each time through the frame. It
        updates positions and checks for collisions.
        """
        if not self.game_over:
            # Move all the sprites
            self.all_sprites_list.update()

            # TODO: Apply screen edge behavior and movement rules here
            # Incluedes: cohesion, avoid_other_boids, match_velocity, setting boundary_type, and move_boid
            for boid in self.block_list:
                flock_rules(
                    boid,
                    self.block_list,
                    cohesion_factor=COHESION_FACTOR,
                    separation=SEPARATION,
                    avoid_factor=AVOID_FACTOR,
                    alignment_factor=ALIGNMENT_FACTOR,
                    visual_range=VISUAL_RANGE,
                )
                boid.speed_limit(MAX_SPEED)
                boundary_type = BoundaryType.BOUNCE
                boid_vs_boundary(
                    boid,
                    boundary_type,
                    window_size=(SCREEN_WIDTH, SCREEN_HEIGHT),
                )

            # See if the player boid has collided with anything.
            blocks_hit_list = pg.sprite.spritecollide(
                self.player, self.block_list, True
            )

            # Check the list of collisions.
            for boid in blocks_hit_list:
                self.score += 1
                print(self.score)
                # You can do something with "boid" here.

            if len(self.block_list) == 0:
                self.game_over = True

    def display_frame(self, screen):
        """Display everything to the screen for the game."""
        screen.fill(pg.Color("white"))

        if self.game_over:
            # font = pg.font.Font("Serif", 25)
            font = pg.font.SysFont("serif", 25)
            text = font.render("Game Over, click to restart", True, pg.Color("black"))
            center_x = (SCREEN_WIDTH // 2) - (text.get_width() // 2)
            center_y = (SCREEN_HEIGHT // 2) - (text.get_height() // 2)
            screen.blit(text, [center_x, center_y])

        if not self.game_over:
            self.all_sprites_list.draw(screen)

        pg.display.flip()


def main():
    """Main program function."""
    # Initialize Pygame and set up the window
    pg.init()

    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pg.display.set_mode(size)

    pg.display.set_caption("My Game")
    pg.mouse.set_visible(False)

    # Create our objects and set the data
    done = False
    clock = pg.time.Clock()

    # Create an instance of the Game class
    game = Game()

    # Main game loop
    while not done:

        # Process events (keystrokes, mouse clicks, etc)
        done = game.process_events()

        # Update object positions, check for collisions
        game.run_logic()

        # Draw the current frame
        game.display_frame(screen)

        # Pause for the next frame
        clock.tick(60)

    # Close window and exit
    pg.quit()


# Call the main function, start up the game
if __name__ == "__main__":
    main()
