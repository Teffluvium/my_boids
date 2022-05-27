"""
Boid simulation using PyGame and Sprites
"""
import pygame as pg

from boids.game import Game
from boids.options import ScreenOptions


def main():
    """Main program function."""
    # Initialize Pygame and set up the window
    pg.init()

    screen_opts = ScreenOptions()

    if screen_opts.fullscreen:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        # Update the window size for fullscreen
        screen_opts.winsize = screen.get_size()
    else:
        screen = pg.display.set_mode(screen_opts.winsize)

    pg.display.set_caption("My Boids")
    pg.mouse.set_visible(False)

    # Create our objects and set the data
    done = False
    clock = pg.time.Clock()

    # Create an instance of the Game class
    game = Game(screen_opts=screen_opts)

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
