"""Tests for my_boids.game."""

import pygame as pg
import pytest

from my_boids.game import Game
from my_boids.options import (
    BOID_AVOID_MODE_AVOID,
    PREDATOR_ATTACK_MODE_CENTER,
    PREDATOR_ATTACK_MODE_ISOLATED,
    PREDATOR_ATTACK_MODE_MOUSE,
    PREDATOR_ATTACK_MODE_NEAREST,
    BoidOptions,
    BoundaryType,
    PredatorOptions,
    ScreenOptions,
)


@pytest.fixture(name="game")
def fixture_game(pygame_display):
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
        boid_avoid_mode=BOID_AVOID_MODE_AVOID,
    )
    predator_opts = PredatorOptions(
        predator_attack_mode=PREDATOR_ATTACK_MODE_CENTER,
        predator_detection_range=400.0,
        predator_reaction_strength=0.5,
    )
    return Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        predator_opts=predator_opts,
        use_spatial_grid=False,
    )


@pytest.fixture(name="game_with_spatial_grid")
def fixture_game_with_spatial_grid(pygame_display):
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
        boid_avoid_mode=BOID_AVOID_MODE_AVOID,
    )
    predator_opts = PredatorOptions(
        predator_attack_mode=PREDATOR_ATTACK_MODE_CENTER,
        predator_detection_range=400.0,
        predator_reaction_strength=0.5,
    )
    return Game(
        screen_opts=screen_opts,
        boid_opts=boid_opts,
        predator_opts=predator_opts,
        use_spatial_grid=True,
    )


def test_game_initial_score(game):
    assert game.score == 0


def test_game_initial_game_over(game):
    assert game.game_over is False


def test_game_creates_correct_number_of_boids(game):
    assert len(game.boid_list) == 3


def test_game_predator_exists(game):
    assert game.predator is not None


def test_game_all_sprites_populated(game):
    assert len(game.all_sprites_list) == 4


def test_run_logic_does_not_raise(game):
    game.run_logic()


def test_run_logic_score_non_negative(game):
    game.run_logic()
    assert game.score >= 0


def test_run_logic_skipped_when_game_over(game):
    game.game_over = True
    initial_score = game.score
    game.run_logic()
    assert game.score == initial_score


def test_game_over_when_boid_list_empty(game):
    game.boid_list.empty()
    game.run_logic()
    assert game.game_over is True


def test_score_increments_on_collision(game):
    for boid in game.boid_list:
        boid.pos.update(game.predator.pos)
        boid.rect.center = boid.pos.xy

    game.predator.rect.center = game.predator.pos.xy
    score_before = game.score
    game.run_logic()
    assert game.score > score_before


def test_get_predator_target_center_strategy(game):
    positions = [(100, 100), (200, 100), (300, 200)]
    for boid, (x_pos, y_pos) in zip(game.boid_list, positions, strict=False):
        boid.pos = pg.Vector2(x_pos, y_pos)

    game.predator_opts.predator_attack_mode = PREDATOR_ATTACK_MODE_CENTER
    assert game._get_predator_target() == pg.Vector2(200, 400 / 3)


def test_get_predator_target_nearest_strategy(game):
    game.predator.pos = pg.Vector2(10, 10)
    positions = [(100, 100), (30, 20), (300, 200)]
    for boid, (x_pos, y_pos) in zip(game.boid_list, positions, strict=False):
        boid.pos = pg.Vector2(x_pos, y_pos)

    game.predator_opts.predator_attack_mode = PREDATOR_ATTACK_MODE_NEAREST
    assert game._get_predator_target() == pg.Vector2(30, 20)


def test_get_predator_target_isolated_strategy(game):
    positions = [(100, 100), (110, 100), (400, 400)]
    for boid, (x_pos, y_pos) in zip(game.boid_list, positions, strict=False):
        boid.pos = pg.Vector2(x_pos, y_pos)

    game.predator_opts.predator_attack_mode = PREDATOR_ATTACK_MODE_ISOLATED
    assert game._get_predator_target() == pg.Vector2(400, 400)


def test_get_predator_target_mouse_strategy(game, monkeypatch):
    game.predator_opts.predator_attack_mode = PREDATOR_ATTACK_MODE_MOUSE
    monkeypatch.setattr(pg.mouse, "get_pos", lambda: (123, 456))
    assert game._get_predator_target() == pg.Vector2(123, 456)


def test_process_events_returns_false_with_no_events(game):
    pg.event.clear()
    result = game.process_events()
    assert result is False


def test_process_events_quit_event(game):
    pg.event.clear()
    pg.event.post(pg.event.Event(pg.QUIT))
    result = game.process_events()
    assert result is True


def test_process_events_escape_key(game):
    pg.event.clear()
    pg.event.post(pg.event.Event(pg.KEYUP, key=pg.K_ESCAPE))
    result = game.process_events()
    assert result is True


def test_process_events_mousebuttondown_restarts_game(game):
    game.game_over = True
    game.score = 10
    pg.event.clear()
    pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    game.process_events()
    assert game.score == 0
    assert game.game_over is False


def test_display_frame_normal(game, pygame_display):
    game.display_frame(pygame_display)


def test_display_frame_game_over(game, pygame_display):
    game.game_over = True
    game.display_frame(pygame_display)


def test_display_score(game, pygame_display):
    game.display_score(pygame_display)


def test_display_score_after_increment(game, pygame_display):
    game.score = 5
    game.display_score(pygame_display)


def test_display_predator_attack_mode(game, pygame_display):
    game.display_predator_attack_mode(pygame_display)


def test_display_predator_attack_mode_uses_friendly_label(game, pygame_display, monkeypatch):
    captured_text: list[str] = []

    class FakeFont:
        def render(self, text, antialias, color):
            captured_text.append(text)
            return pg.Surface((1, 1))

    game.predator_opts.predator_attack_mode = PREDATOR_ATTACK_MODE_CENTER
    monkeypatch.setattr(pg.font, "SysFont", lambda *args, **kwargs: FakeFont())

    game.display_predator_attack_mode(pygame_display)
    assert captured_text == ["Predator Attack Mode: Flock Center"]


def test_display_game_over_text(game, pygame_display):
    game.display_game_over_text(pygame_display)


def test_game_spatial_grid_disabled(game):
    assert game.flock_stepper.stats().spatial_grid_enabled is False
    assert game.flock_stepper.stats().occupied_cells is None


def test_game_spatial_grid_enabled(game_with_spatial_grid):
    assert game_with_spatial_grid.flock_stepper.stats().spatial_grid_enabled is True
    game_with_spatial_grid.run_logic()
    assert game_with_spatial_grid.flock_stepper.stats().boids_processed == 3


def test_neighbor_backends_agree_when_separation_exceeds_visual_range(game, game_with_spatial_grid):
    for simulation in (game, game_with_spatial_grid):
        simulation.update_boid_options(
            simulation.boid_opts.model_copy(update={"separation": 50.0, "visual_range": 20})
        )
        simulation.predator_opts.predator_detection_range = 100.0
        simulation.predator.pos.update(750, 50)
        for boid, position in zip(
            simulation.boid_list, [(300, 300), (330, 300), (600, 500)], strict=True
        ):
            boid.pos.update(position)
            boid.vel.update(0, 0)
        simulation.run_logic()

    for full_scan, indexed in zip(game.boid_list, game_with_spatial_grid.boid_list, strict=True):
        assert tuple(indexed.pos) == pytest.approx(tuple(full_scan.pos), abs=1e-9, rel=1e-9)
        assert tuple(indexed.vel) == pytest.approx(tuple(full_scan.vel), abs=1e-9, rel=1e-9)


def test_neighbor_backends_observe_positions_wrapped_earlier_in_the_pass(
    game, game_with_spatial_grid
):
    for simulation in (game, game_with_spatial_grid):
        simulation.screen_opts.boundary_type = BoundaryType.WRAP
        simulation.update_boid_options(
            simulation.boid_opts.model_copy(update={"separation": 20.0, "visual_range": 20})
        )
        simulation.predator_opts.predator_detection_range = 100.0
        simulation.predator.pos.update(750, 50)
        for boid, position in zip(
            simulation.boid_list, [(805, 300), (10, 300), (600, 500)], strict=True
        ):
            boid.pos.update(position)
            boid.vel.update(0, 0)
        simulation.run_logic()

    for full_scan, indexed in zip(game.boid_list, game_with_spatial_grid.boid_list, strict=True):
        assert tuple(indexed.pos) == pytest.approx(tuple(full_scan.pos), abs=1e-9, rel=1e-9)
        assert tuple(indexed.vel) == pytest.approx(tuple(full_scan.vel), abs=1e-9, rel=1e-9)
