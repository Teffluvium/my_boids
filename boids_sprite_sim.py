"""
Boid simulation using PyGame and Sprites
"""

from enum import Enum, auto
from typing import List, Tuple

import numpy as np
import pygame as pg

from boids.boids import Boid
from boids.movement import BoundaryType, move_boid

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


def cohesion(
    boid: Boid,
    boids: List[Boid],
    cohesion_factor: float = COHESION_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Move the boid towards the perceived center of mass of the flock"""
    num_boids = 0

    # Add contribution from each boid in the flock, as long as they are
    # within the visual range
    sum_positions = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid.pos.distance_to(boid.pos) < visual_range:
            sum_positions += other_boid.pos
            num_boids += 1

    # There should at least 2 boids, yourself and another boid
    if num_boids >= 2:
        # Subract the boid's own position contribution
        sum_positions -= boid.pos

        # Calculate the center of mass
        center_of_mass = sum_positions / (num_boids - 1)

        # Update the boid's velocity
        boid.vel += (center_of_mass - boid.pos) * cohesion_factor


def avoid_other_boids(
    boid: Boid,
    boids: List[Boid],
    separation: float = SEPARATION,
    avoid_factor: float = AVOID_FACTOR,
):
    """Avoid other boids that are too close"""
    delta = pg.Vector2(0, 0)
    for other_boid in boids:
        # Skip checking the boid itself
        if other_boid is boid:
            continue

        # Calculate the distance between the boids
        distance = boid.pos.distance_to(other_boid.pos)

        # If the distance is less than the minimum, apply the avoidance
        if distance < separation:
            # Calculate the vector to the other boid
            delta += boid.pos - other_boid.pos

    # Apply the vector to the boid
    boid.vel += delta * avoid_factor


def match_velocity(
    boid: Boid,
    boids: List[Boid],
    alignment_factor: float = ALIGNMENT_FACTOR,
    visual_range: float = VISUAL_RANGE,
):
    """Match the velocity of the boid with the velocity of the flock"""
    num_boids = 0

    # Calculate the average velocity of the flock, as long as they are
    # within the visual range
    sum_velocity = pg.Vector2(0, 0)
    for other_boid in boids:
        if other_boid.pos.distance_to(boid.pos) < visual_range:
            sum_velocity += other_boid.vel
            num_boids += 1

    # There should at least 2 boids, yourself and another boid
    if num_boids >= 2:
        # Subract the boid's own velocity contribution
        sum_velocity -= boid.vel

        # Calculate the average velocity of other boids
        average_velocity = sum_velocity / (num_boids - 1)

        # Update the boid's velocity
        boid.vel += (average_velocity - boid.vel) * alignment_factor


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
                cohesion(boid, self.block_list)
                avoid_other_boids(boid, self.block_list)
                match_velocity(boid, self.block_list)
                boid.speed_limit(MAX_SPEED)
                boundary_type = BoundaryType.BOUNCE
                move_boid(
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
