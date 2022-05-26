"""
Show the proper way to organize a game using the a game class.
 
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
 
Explanation video: http://youtu.be/O4Y5KrNgP_c
"""

import configparser

import numpy as np
import pygame as pg

from boids.movement import BoundaryType, move_boid

# --- Global constants ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500

rng = np.random.default_rng()


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
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw the boid onto the surface
        pg.draw.ellipse(self.image, color, [0, 0, width, height])

        # Get a rectangle object that represents the size of the image
        self.rect = self.image.get_rect()

        self.rect.center = self.pos

    def reset_pos(self):
        """Called when the boid 'falls off' the screen."""
        boundary_type = BoundaryType.BOUNCE

        move_boid(self, boundary_type, [SCREEN_WIDTH, SCREEN_HEIGHT])

    def update(self):
        """Called each frame. Updates the position of the boid."""
        # # Move the boid based on its velocity
        self.pos += self.vel

        # Update boid position relative to the screen boundaries
        self.reset_pos()

        # Update the rectangle position
        self.rect.center = self.pos


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
