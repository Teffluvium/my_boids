"""
Boid simulation using PyGame and Sprites
"""

import pygame as pg
import pygame_gui
from pygame_gui.elements import UIButton

from my_boids.game import Game
from my_boids.options import ScreenOptions
from my_boids.settings_ui import SettingsDialog

_CONFIG_PATH = "config.ini"
_SETTINGS_BTN_W = 120
_SETTINGS_BTN_H = 34
_SETTINGS_BTN_MARGIN = 8


def main():
    """Main program function."""
    # Initialize Pygame and set up the window
    pg.init()

    screen_opts = ScreenOptions.from_config()

    if screen_opts.fullscreen:
        screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        # Update the window size for fullscreen
        screen_size = screen.get_size()
        screen_opts.winsize = [screen_size[0], screen_size[1]]
    else:
        screen = pg.display.set_mode(screen_opts.winsize)

    pg.display.set_caption("My Boids")
    pg.mouse.set_visible(True)

    # Create UI manager (must be sized to the actual window)
    ui_manager = pygame_gui.UIManager(screen.get_size())

    # Persistent "Settings" button - top-right corner of the game window
    settings_btn = UIButton(
        relative_rect=pg.Rect(
            screen.get_width() - _SETTINGS_BTN_W - _SETTINGS_BTN_MARGIN,
            _SETTINGS_BTN_MARGIN,
            _SETTINGS_BTN_W,
            _SETTINGS_BTN_H,
        ),
        text="Settings",
        manager=ui_manager,
    )

    # Create an instance of the Game class
    game = Game(screen_opts=screen_opts)

    # Create the settings dialog (built lazily when first opened)
    settings_dialog = SettingsDialog(
        ui_manager=ui_manager,
        config_path=_CONFIG_PATH,
        game=game,
    )

    done = False
    clock = pg.time.Clock()

    # Main game loop
    while not done:
        time_delta = clock.tick(50) / 1000.0

        # Start performance monitoring for this frame
        game.performance.start_frame()

        # Collect events once so both the UI layer and game receive them
        events = pg.event.get()

        for event in events:
            # Let pygame_gui handle its own events first
            ui_manager.process_events(event)

            # Settings button opens the dialog
            if (
                event.type == pygame_gui.UI_BUTTON_PRESSED
                and event.ui_element is settings_btn
                and not settings_dialog.is_open()
            ):
                settings_dialog.open(screen.get_size())

            # Forward all events to the dialog (it ignores them when closed)
            settings_dialog.handle_event(event)

        # Only forward game events when the settings dialog is closed
        if settings_dialog.is_open():
            # Still honour QUIT / ESC so the app can always be exited
            for event in events:
                if event.type == pg.QUIT or (event.type == pg.KEYUP and event.key == pg.K_ESCAPE):
                    done = True
        else:
            done = game.process_events(events)

        # Update object positions, check for collisions
        game.run_logic()

        # Draw game frame - defer the display flip so the UI renders on top
        game.display_frame(screen, flip=False)

        # Draw pygame_gui elements on top of the game frame
        ui_manager.update(time_delta)
        ui_manager.draw_ui(screen)

        # Single flip for the final composited frame
        pg.display.flip()

    # Close window and exit
    pg.quit()


if __name__ == "__main__":
    main()
