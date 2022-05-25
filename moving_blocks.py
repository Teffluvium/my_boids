"""
Sample Python/Pygame Programs
Simpson College Computer Science
http://programarcadegames.com/
http://simpson.edu/computer-science/
 
Explanation video: http://youtu.be/qbEEcQXw8aw
"""

import random

import numpy as np
import pygame as pg

# Define some colors
BLACK = pg.Color(0, 0, 0)
WHITE = pg.Color(255, 255, 255)
GREEN = pg.Color(0, 255, 0)
RED = pg.Color(255, 0, 0)

screen_width = 700
screen_height = 400

max_speed = 3

rng = np.random.default_rng()


class Boid(pg.sprite.Sprite):
    """
    This class represents the ball
    It derives from the "Sprite" class in Pygame
    """

    def __init__(
        self,
        pos: pg.Vector2 = pg.Vector2(0, 0),
        vel: pg.Vector2 = pg.Vector2(0, 0),
        color: pg.Color = pg.Color(0, 0, 0),
        size: int = 10,
        width: int = 20,
        height: int = 15,
    ):
        """Constructor. Pass in the color of the block,
        and its x and y position."""
        # Call the parent class (Sprite) constructor
        super().__init__()

        # # Create an image of the block, and fill it with a color.
        # # This could also be an image loaded from the disk.
        # self.image = pg.Surface([width, height])
        # self.image.fill(color)

        # Set the background color and set it to be transparent
        self.image = pg.Surface([width, height])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        # Draw the ellipse
        pg.draw.ellipse(self.image, color, [0, 0, width, height])

        # Fetch the rectangle object that has the dimensions of the image
        # image. Update the position of this object by setting the values
        # of rect.x and rect.y
        self.rect = self.image.get_rect()

        self.pos = pos
        self.vel = vel
        self.color = color
        self.size = size

    def reset_pos(self):
        """Reset position to the top of the screen, at a random x location.
        Called by update() or the main program loop if there is a collision.
        """
        self.rect.y = random.randrange(-300, -20)
        self.rect.x = random.randrange(0, screen_width)

    def update(self):
        """Called each frame."""

        # Move block down one pixel
        self.rect.y += 1

        # If block is too far down, reset to top of screen.
        if self.rect.y > screen_height - 10:
            self.reset_pos()


class Player(Boid):
    """The player class derives from Block, but overrides the 'update'
    functionality with new a movement function that will move the block
    with the mouse."""

    def update(self):
        # Get the current mouse position. This returns the position
        # as a list of two numbers.
        pos = pg.mouse.get_pos()

        # Fetch the x and y out of the list,
        # just like we'd fetch letters out of a string.
        # Set the player object to the mouse location
        self.rect.x = pos[0]
        self.rect.y = pos[1]


def main():
    # Initialize Pygame
    pg.init()

    # Set the height and width of the screen
    screen = pg.display.set_mode([screen_width, screen_height])

    # This is a list of 'sprites.' Each block in the program is
    # added to this list. The list is managed by a class called 'Group.'
    block_list = pg.sprite.Group()

    # This is a list of every sprite. All blocks and the player block as well.
    all_sprites_list = pg.sprite.Group()

    for i in range(50):
        # This represents a block
        boid = Boid(
            vel=pg.Vector2(rng.uniform(-max_speed, max_speed, 2).tolist()),
            color=rng.integers(30, 255, 3).tolist(),
            width=20,
            height=15,
        )

        # Set a random location for the block
        boid.rect.x = random.randrange(screen_width)
        boid.rect.y = random.randrange(screen_height)

        # Add the block to the list of objects
        block_list.add(boid)
        all_sprites_list.add(boid)

    # Create a red player block
    player = Player(color=RED, width=25, height=15)
    all_sprites_list.add(player)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pg.time.Clock()

    score = 0

    # -------- Main Program Loop -----------
    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        # Clear the screen
        screen.fill(BLACK)

        # Calls update() method on every sprite in the list
        all_sprites_list.update()

        # See if the player block has collided with anything.
        blocks_hit_list = pg.sprite.spritecollide(player, block_list, False)

        # Check the list of collisions.
        for boid in blocks_hit_list:
            score += 1
            print(score)

            # Reset block to the top of the screen to fall again.
            boid.reset_pos()

        # Draw all the spites
        all_sprites_list.draw(screen)

        # Limit to 20 frames per second
        clock.tick(20)

        # Go ahead and update the screen with what we've drawn.
        pg.display.flip()

    pg.quit()


if __name__ == "__main__":
    main()
