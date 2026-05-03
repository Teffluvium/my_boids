"""Tests for boids/game.py"""
import pygame as pg
import pytest
from boids.boid_vs_boundary import BoundaryType
from boids.game import Game


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


class _MockScreenOptions:
    """Minimal ScreenOptions substitute for testing."""

    def __init__(self):
        self.winsize = [800, 600]
        self.fullscreen = False
        self.boundary_type = BoundaryType.BOUNCE


class _MockBoidOptions:
    """Minimal BoidOptions substitute for testing."""

    def __init__(self):
        self.num_boids = 3
        self.size = 10
        self.max_speed = 5.0
        self.cohesion_factor = 0.005
        self.separation = 20
        self.avoid_factor = 0.05
        self.alignment_factor = 0.01
        self.visual_range = 100


@pytest.fixture(name="game")
def fixture_game(pygame_display):
    """Return a fresh Game instance backed by mock options."""
    return Game(
        screen_opts=_MockScreenOptions(),
        boid_opts=_MockBoidOptions(),
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
