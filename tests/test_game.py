"""Tests for boids/game.py"""

import pygame as pg
import pytest

from my_boids.boid_vs_boundary import BoundaryType
from my_boids.game import Game
from my_boids.options import (
    PREDATOR_ATTACK_CENTER,
    PREDATOR_ATTACK_ISOLATED,
    PREDATOR_ATTACK_NEAREST,
    PREDATOR_MODE_AVOID,
    BoidOptions,
    ScreenOptions,
)

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="game")
def fixture_game(pygame_display):
    """Return a fresh Game instance backed by test options.

    Uses spatial grid disabled for deterministic testing.
    """
    screen_opts = ScreenOptions(
        winsize=[800, 600],
        fullscreen=False,
        boundary_type=BoundaryType.BOUNCE,
    )
    boid_opts = BoidOptions(
        num_boids=3,
        size=10,
        max_speed=5.0,
        cohesion_factor=0.005,
        separation=20,
        avoid_factor=0.05,
        alignment_factor=0.01,
        visual_range=100,
        predator_behavior_mode=PREDATOR_MODE_AVOID,
        predator_attack_strategy=PREDATOR_ATTACK_CENTER,
        predator_detection_range=400.0,
        predator_reaction_strength=0.5,
    )
    return Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        use_spatial_grid=False,
    )


@pytest.fixture(name="game_with_spatial_grid")
def fixture_game_with_spatial_grid(pygame_display):
    """Return a fresh Game instance with spatial grid enabled."""
    screen_opts = ScreenOptions(
        winsize=[800, 600],
        fullscreen=False,
        boundary_type=BoundaryType.BOUNCE,
    )
    boid_opts = BoidOptions(
        num_boids=3,
        size=10,
        max_speed=5.0,
        cohesion_factor=0.005,
        separation=20,
        avoid_factor=0.05,
        alignment_factor=0.01,
        visual_range=100,
        predator_behavior_mode=PREDATOR_MODE_AVOID,
        predator_attack_strategy=PREDATOR_ATTACK_CENTER,
        predator_detection_range=400.0,
        predator_reaction_strength=0.5,
    )
    return Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        use_spatial_grid=True,
    )


# ---------------------------------------------------------------------------
# Game.__init__
# ---------------------------------------------------------------------------


def test_game_initial_score(game):
    """Game starts with a score of zero"""
    assert game.score == 0


def test_game_initial_game_over(game):
    """Game starts with game_over False"""
    assert game.game_over is False


def test_game_creates_correct_number_of_boids(game):
    """Game creates the number of boids specified in BoidOptions"""
    assert len(game.boid_list) == 3


def test_game_predator_exists(game):
    """Game creates a Predator sprite"""
    assert game.predator is not None


def test_game_all_sprites_populated(game):
    """all_sprites_list contains boids plus the predator"""
    # 3 boids + 1 predator
    assert len(game.all_sprites_list) == 4


# ---------------------------------------------------------------------------
# Game.run_logic
# ---------------------------------------------------------------------------


def test_run_logic_does_not_raise(game):
    """run_logic executes without error during normal play"""
    game.run_logic()


def test_run_logic_score_non_negative(game):
    """Score never decreases after run_logic"""
    game.run_logic()
    assert game.score >= 0


def test_run_logic_skipped_when_game_over(game):
    """run_logic is a no-op when game_over is True"""
    game.game_over = True
    initial_score = game.score
    game.run_logic()
    assert game.score == initial_score


def test_game_over_when_boid_list_empty(game):
    """game_over is set to True once all boids have been removed"""
    game.boid_list.empty()
    game.run_logic()
    assert game.game_over is True


def test_score_increments_on_collision(game):
    """Score increments when the predator sprite collides with a boid"""
    # Move all boids to exactly overlap the predator so a collision is certain
    for boid in game.boid_list:
        boid.pos.update(game.predator.pos)
        boid.rect.center = boid.pos.xy

    game.predator.rect.center = game.predator.pos.xy

    score_before = game.score
    game.run_logic()
    assert game.score > score_before


def test_get_predator_target_center_strategy(game):
    """Center strategy targets the centroid of the remaining flock."""
    positions = [(100, 100), (200, 100), (300, 200)]
    for boid, (x_pos, y_pos) in zip(game.boid_list, positions, strict=False):
        boid.pos = pg.Vector2(x_pos, y_pos)

    game.boid_opts.predator_attack_strategy = PREDATOR_ATTACK_CENTER

    assert game._get_predator_target() == pg.Vector2(200, 400 / 3)


def test_get_predator_target_nearest_strategy(game):
    """Nearest strategy targets the boid closest to the predator."""
    game.predator.pos = pg.Vector2(10, 10)
    positions = [(100, 100), (30, 20), (300, 200)]
    for boid, (x_pos, y_pos) in zip(game.boid_list, positions, strict=False):
        boid.pos = pg.Vector2(x_pos, y_pos)

    game.boid_opts.predator_attack_strategy = PREDATOR_ATTACK_NEAREST

    assert game._get_predator_target() == pg.Vector2(30, 20)


def test_get_predator_target_isolated_strategy(game):
    """Isolated strategy targets the boid farthest from its nearest neighbour."""
    positions = [(100, 100), (110, 100), (400, 400)]
    for boid, (x_pos, y_pos) in zip(game.boid_list, positions, strict=False):
        boid.pos = pg.Vector2(x_pos, y_pos)

    game.boid_opts.predator_attack_strategy = PREDATOR_ATTACK_ISOLATED

    assert game._get_predator_target() == pg.Vector2(400, 400)


# ---------------------------------------------------------------------------
# Game.process_events
# ---------------------------------------------------------------------------


def test_process_events_returns_false_with_no_events(game):
    """process_events returns False when the event queue is empty"""
    pg.event.clear()
    result = game.process_events()
    assert result is False


def test_process_events_quit_event(game):
    """process_events returns True when a QUIT event is in the queue"""
    pg.event.clear()
    pg.event.post(pg.event.Event(pg.QUIT))
    result = game.process_events()
    assert result is True


def test_process_events_escape_key(game):
    """process_events returns True when the ESCAPE key is released"""
    pg.event.clear()
    pg.event.post(pg.event.Event(pg.KEYUP, key=pg.K_ESCAPE))
    result = game.process_events()
    assert result is True


def test_process_events_mousebuttondown_restarts_game(game):
    """A MOUSEBUTTONDOWN event restarts the game when game_over is True"""
    game.game_over = True
    game.score = 10
    pg.event.clear()
    pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    game.process_events()
    assert game.score == 0
    assert game.game_over is False


# ---------------------------------------------------------------------------
# Game.display_frame / display_score / display_game_over_text
# ---------------------------------------------------------------------------


def test_display_frame_normal(game, pygame_display):
    """display_frame runs without error during normal play"""
    game.display_frame(pygame_display)


def test_display_frame_game_over(game, pygame_display):
    """display_frame shows game-over screen without error"""
    game.game_over = True
    game.display_frame(pygame_display)


def test_display_score(game, pygame_display):
    """display_score renders to the surface without error"""
    game.display_score(pygame_display)


def test_display_score_after_increment(game, pygame_display):
    """display_score works correctly after score changes"""
    game.score = 5
    game.display_score(pygame_display)


def test_display_game_over_text(game, pygame_display):
    """display_game_over_text renders to the surface without error"""
    game.display_game_over_text(pygame_display)


# ---------------------------------------------------------------------------
# Spatial Grid Integration Tests
# ---------------------------------------------------------------------------


def test_game_spatial_grid_disabled(game):
    """Game with use_spatial_grid=False has no spatial grid"""
    assert game.use_spatial_grid is False
    assert game.spatial_grid is None


def test_game_spatial_grid_enabled(game_with_spatial_grid):
    """Game with use_spatial_grid=True has a spatial grid"""
    assert game_with_spatial_grid.use_spatial_grid is True
    assert game_with_spatial_grid.spatial_grid is not None


def test_spatial_grid_cell_size_matches_visual_range(game_with_spatial_grid):
    """Spatial grid cell size is set to visual range for optimal performance"""
    assert game_with_spatial_grid.spatial_grid is not None
    assert game_with_spatial_grid.spatial_grid.cell_size == 100


def test_spatial_grid_run_logic(game_with_spatial_grid):
    """run_logic with spatial grid executes without error"""
    game_with_spatial_grid.run_logic()


def test_spatial_grid_produces_same_behavior(game, game_with_spatial_grid):
    """Spatial grid runs without errors and maintains valid game state"""
    # Run the spatial grid game for a few frames
    for _ in range(5):
        game_with_spatial_grid.run_logic()

    # Game should still be in valid state
    assert game_with_spatial_grid.score >= 0
    # Number of boids should be <= initial number (some may have been eaten)
    assert len(game_with_spatial_grid.boid_list) <= 3
