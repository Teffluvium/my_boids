"""
Show the proper way to organize a game using the a game class.
 
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
 
Explanation video: http://youtu.be/O4Y5KrNgP_c
"""

import configparser
from enum import Enum, auto
from typing import Tuple

import numpy as np
import pygame as pg

# --- Global constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

rng = np.random.default_rng()

# Boid Constants
SIZE = 10
MAX_SPEED = 3
COHESION_FACTOR = 0.001
SEPARATION = 20
AVOID_FACTOR = 0.01
ALIGNMENT_FACTOR = 0.01
VISUAL_RANGE = 100


# --- Classes ---


class Boid(pg.sprite.Sprite):
    def __init__(
        self,
        pos: pg.Vector2 = pg.Vector2(0, 0),
        vel: pg.Vector2 = pg.Vector2(0, 0),
        color: pg.Color = pg.Color(255, 255, 255),
        size: int = 10,
        width: int = 10,
        height: int = 10,
    ):
        """Constructor"""
        # Call the Sprite initializer
        super().__init__()

        """Validate parameters"""
        # Ensure that position and velocity are Vector2 objects
        self.pos = pos if isinstance(pos, pg.Vector2) else pg.Vetor2(pos)
        self.vel = vel if isinstance(vel, pg.Vector2) else pg.Vetor2(vel)

        # Ensure color is a tuple and has 3 or 4 elements
        self.color = color if isinstance(color, pg.Color) else pg.Color(color)

        # Check size is a positive
        if size >= 1:
            self.size = size
        else:
            raise ValueError("Size cannot be negative")

        # Create a surface for the boid
        self.image = pg.Surface([width, height])

        # Fill the surface with the the background color and set it to be transparent
        self.image.fill(pg.Color("black"))
        self.image.set_colorkey(pg.Color("black"))

        # Draw the boid onto the surface
        pg.draw.ellipse(self.image, color, [0, 0, width, height])

        # Get a rectangle object that represents the size of the image
        self.rect = self.image.get_rect()

        self.rect.center = self.pos

    def reset_pos(self, window_size: tuple = (SCREEN_WIDTH, SCREEN_HEIGHT)):
        """Called when the boid 'falls off' the screen."""
        # TODO: move this function out of Boid class
        boundary_type = BoundaryType.WRAP
        move_boid(self, boundary_type, window_size=window_size)

    def update(self):
        """Called each frame. Updates the position of the boid."""
        # # Move the boid based on its velocity
        self.pos += self.vel

        # Update boid position relative to the screen boundaries
        self.reset_pos()

        # Update the rectangle position
        self.rect.center = self.pos

    def avoid_other_boids(
        self,
        boids: list,
        separation: float = SEPARATION,
        avoid_factor: float = AVOID_FACTOR,
    ):
        """Avoid other boids that are too close"""
        delta = pg.Vector2(0, 0)
        for other_boid in boids:
            # Skip checking the boid itself
            if other_boid is self:
                continue

            # Calculate the distance between the boids
            distance = self.pos.distance_to(other_boid.pos)

            # If the distance is less than the minimum, apply the avoidance
            if distance < separation:
                # Calculate the vector to the other boid
                delta += self.pos - other_boid.pos

        # Apply the vector to the boid
        self.vel += delta * avoid_factor

    def match_velocity(
        self,
        boids: list,
        alignment_factor: float = ALIGNMENT_FACTOR,
        visual_range: float = VISUAL_RANGE,
    ):
        """Match the velocity of the boid with the velocity of the flock"""
        num_boids = 0

        # Calculate the average velocity of the flock, as long as they are
        # within the visual range
        sum_velocity = pg.Vector2(0, 0)
        for boid in boids:
            if boid.pos.distance_to(self.pos) < visual_range:
                sum_velocity += boid.vel
                num_boids += 1

        # There should at least 2 boids, yourself and another boid
        if num_boids >= 2:
            # Subract the boid's own velocity contribution
            sum_velocity -= self.vel

            # Calculate the average velocity of other boids
            average_velocity = sum_velocity / (num_boids - 1)

            # Update the boid's velocity
            self.vel += (average_velocity - self.vel) * alignment_factor

    def speed_limit(self, max_speed: float = MAX_SPEED):
        """Limit the speed of the boid"""
        speed = self.vel.magnitude()
        # Apply a speed limit
        if speed > max_speed:
            self.vel.scale_to_length(max_speed)


class BoundaryType(Enum):
    """Enum for boid behavior when they hit the boundary"""

    BOUNCE = auto()
    WRAP = auto()


def move_boid(
    boid: Boid,
    boundary_type: BoundaryType,
    window_size: Tuple[int, int],
    margin: int = 30,
    turn_factor: float = 1,
) -> None:
    """Move a boid and keep it within the windows according to the boundary type.

    Args:
        boid (Boid): Its a Boid
        boundary_type (BoundaryType): What to do when the boid hits the edge
        window_size (Tuple[int, int]): Window size in pixels
    """

    # Select the boundary type and adjust the boid's position and/or velocity
    if boundary_type == BoundaryType.WRAP:
        wrap_around_screen(
            boid,
            window_size,
        )
    elif boundary_type == BoundaryType.BOUNCE:
        keep_within_bounds(
            boid,
            window_size,
            margin=margin,
            turn_factor=turn_factor,
        )


def wrap_around_screen(boid: Boid, window_size: Tuple[int, int]) -> None:
    """Wrap boid around to opposite side of the window.

    Note: This function compares the postion of the boid to the window size
        and adjusts the position, leaving the velocity unchanged.

    Args:
        boid (Boid): Its a Boid
        window_size (Tuple[int, int]): Window size in pixels
    """
    boid.pos.update(
        boid.pos[0] % window_size[0],
        boid.pos[1] % window_size[1],
    )


def keep_within_bounds(
    boid: Boid,
    window_size: Tuple[int, int],
    margin: int = 30,
    turn_factor: float = 1,
) -> None:
    """Adjust the boid's velocity to keep it within the window.

    Note: This function compares the postion of the boid to the window size
        and adjusts the velocity, leaving the position unchanged.

    Args:
        boid (Boid): Its a Boid
        window_size (Tuple[int, int]): Window size in pixels
        margin (int, optional): Buffer of pixels from the edges of the
            window. Defaults to 30.
        turn_factor (float, optional): Adjust the velocity by this factor.
            Defaults to 1.
    """

    def adjust_vel(pos, vel, window_size) -> float:
        """Adjust velocity component to keep boid within bounds"""
        if pos < margin:
            vel += turn_factor
        elif pos > window_size - margin:
            vel -= turn_factor

        return vel

    # Calculate the new velocity
    vel = [0.0, 0.0]
    vel[0] = adjust_vel(boid.pos[0], boid.vel[0], window_size[0])
    vel[1] = adjust_vel(boid.pos[1], boid.vel[1], window_size[1])

    # Update the boid's velocity
    boid.vel.update(vel)


class Player(pg.sprite.Sprite):
    """This class represents the player."""

    def __init__(self):
        super().__init__()
        self.image = pg.Surface([20, 20])
        self.image.fill(RED)
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
                pass

            # See if the player boid has collided with anything.
            blocks_hit_list = pg.sprite.spritecollide(
                self.player, self.block_list, True
            )

            # Check the list of collisions.
            for boid in blocks_hit_list:
                self.score += 1
                print(self.score)
                print(f"{boid.rect.x=}, {boid.rect.y=}")
                print(f"{boid.rect.centerx=}, {boid.rect.centery=}")
                print(f"{boid.rect.center=}")
                # You can do something with "boid" here.

            if len(self.block_list) == 0:
                self.game_over = True

    def display_frame(self, screen):
        """Display everything to the screen for the game."""
        screen.fill(WHITE)

        if self.game_over:
            # font = pg.font.Font("Serif", 25)
            font = pg.font.SysFont("serif", 25)
            text = font.render("Game Over, click to restart", True, BLACK)
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
