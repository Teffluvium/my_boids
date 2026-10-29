"""Focused tests for HUD rendering helpers."""

import pygame as pg
import pytest

from my_boids import hud
from my_boids.flock_stepper import FlockStats
from my_boids.performance import FrameMetrics, PerformanceMonitor


def test_draw_predator_attack_mode_uses_friendly_label(monkeypatch, pygame_display):
    captured_text: list[str] = []

    class FakeFont:
        def render(self, text: str, _antialias: bool, _color: pg.Color) -> pg.Surface:
            captured_text.append(text)
            return pg.Surface((1, 1))

    monkeypatch.setattr(pg.font, "SysFont", lambda *_args, **_kwargs: FakeFont())

    hud.draw_predator_attack_mode(pygame_display, "center")

    assert captured_text == ["Predator Attack Mode: Flock Center"]


def test_draw_metrics_includes_grid_mode_and_timing_lines(monkeypatch, pygame_display):
    captured_lines: list[str] = []

    class FakeFont:
        def render(self, text: str, _antialias: bool, _color: pg.Color) -> pg.Surface:
            captured_lines.append(text)
            return pg.Surface((1, 1))

    monkeypatch.setattr(pg.font, "SysFont", lambda *_args, **_kwargs: FakeFont())

    performance = PerformanceMonitor(enabled=True)
    performance.frame_times.append(1 / 50)
    performance.current_metrics = FrameMetrics(
        frame_time=1 / 50,
        update_time=0.001,
        logic_time=0.002,
        collision_time=0.003,
        render_time=0.004,
    )
    hud.draw_metrics(
        pygame_display,
        performance,
        boid_count=12,
        flock_stats=FlockStats(True, 15, 3),
    )

    assert "Boids: 12" in captured_lines
    assert "Grid: 3 cells" in captured_lines
    assert "Mode: Spatial" in captured_lines
    assert "Update: 1.00ms" in captured_lines
    assert "Logic: 2.00ms" in captured_lines
    assert "Collision: 3.00ms" in captured_lines
    assert "Render: 4.00ms" in captured_lines


def test_draw_frame_game_over_short_circuits_sprite_and_metric_draw(monkeypatch, pygame_display):
    calls: list[str] = []

    def fake_draw_game_over(_screen: pg.Surface) -> None:
        calls.append("game_over")

    def fake_draw_score(_screen: pg.Surface, _score: int) -> None:
        calls.append("score")

    def fake_draw_predator_mode(_screen: pg.Surface, _mode: str) -> None:
        calls.append("predator_mode")

    def fake_draw_predator_attack_mode(_screen: pg.Surface, _mode: str) -> None:
        calls.append("predator_attack_mode")

    def fake_draw_metrics(*_args, **_kwargs) -> None:
        calls.append("metrics")

    def fake_draw_detection_range(*_args, **_kwargs) -> None:
        calls.append("detection_range")

    def fake_group_draw(self, _surface: pg.Surface) -> None:
        calls.append("sprites")

    monkeypatch.setattr(hud, "draw_game_over", fake_draw_game_over)
    monkeypatch.setattr(hud, "draw_score", fake_draw_score)
    monkeypatch.setattr(hud, "draw_predator_mode", fake_draw_predator_mode)
    monkeypatch.setattr(hud, "draw_predator_attack_mode", fake_draw_predator_attack_mode)
    monkeypatch.setattr(hud, "draw_metrics", fake_draw_metrics)
    monkeypatch.setattr(hud, "draw_detection_range", fake_draw_detection_range)
    monkeypatch.setattr(pg.sprite.Group, "draw", fake_group_draw)

    hud.draw_frame(
        pygame_display,
        pg.sprite.Group(),
        score=0,
        predator_mode="avoid",
        predator_attack_mode="center",
        game_over=True,
        performance=PerformanceMonitor(enabled=True),
        show_metrics=True,
        boid_count=0,
        flock_stats=FlockStats(False, 0, None),
        predator_pos=pg.Vector2(),
        detection_range=100.0,
    )

    assert calls == ["game_over"]


def test_draw_frame_active_calls_expected_helpers(monkeypatch, pygame_display):
    calls: list[str] = []

    def fake_draw_game_over(_screen: pg.Surface) -> None:
        calls.append("game_over")

    def fake_draw_score(_screen: pg.Surface, _score: int) -> None:
        calls.append("score")

    def fake_draw_predator_mode(_screen: pg.Surface, _mode: str) -> None:
        calls.append("predator_mode")

    def fake_draw_predator_attack_mode(_screen: pg.Surface, _mode: str) -> None:
        calls.append("predator_attack_mode")

    def fake_draw_metrics(*_args, **_kwargs) -> None:
        calls.append("metrics")

    def fake_group_draw(self, _surface: pg.Surface) -> None:
        calls.append("sprites")

    monkeypatch.setattr(hud, "draw_game_over", fake_draw_game_over)
    monkeypatch.setattr(hud, "draw_score", fake_draw_score)
    monkeypatch.setattr(hud, "draw_predator_mode", fake_draw_predator_mode)
    monkeypatch.setattr(hud, "draw_predator_attack_mode", fake_draw_predator_attack_mode)
    monkeypatch.setattr(hud, "draw_metrics", fake_draw_metrics)
    monkeypatch.setattr(pg.sprite.Group, "draw", fake_group_draw)

    hud.draw_frame(
        pygame_display,
        pg.sprite.Group(),
        score=5,
        predator_mode="avoid",
        predator_attack_mode="nearest",
        game_over=False,
        performance=PerformanceMonitor(enabled=True),
        show_metrics=True,
        boid_count=3,
        flock_stats=FlockStats(False, 0, None),
        predator_pos=pg.Vector2(),
        detection_range=100.0,
    )

    assert "sprites" in calls
    assert "score" in calls
    assert "predator_mode" in calls
    assert "predator_attack_mode" in calls
    assert "metrics" in calls
    assert "game_over" not in calls


def test_draw_detection_range_draws_one_pixel_outline(monkeypatch, pygame_display):
    calls: list[tuple] = []
    monkeypatch.setattr(pg.draw, "circle", lambda *args, **kwargs: calls.append((args, kwargs)))

    hud.draw_detection_range(pygame_display, pg.Vector2(40, 50), 100.0)

    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args[0] is pygame_display
    assert args[2] == pg.Vector2(40, 50)
    assert args[3] == 100.0
    assert kwargs == {"width": 1}


@pytest.mark.parametrize("show_metrics", [True, False])
def test_draw_frame_draws_detection_range_only_with_metrics(
    monkeypatch, pygame_display, show_metrics
):
    circles: list[tuple[pg.Vector2, float]] = []
    monkeypatch.setattr(
        hud,
        "draw_detection_range",
        lambda _screen, center, radius: circles.append((center, radius)),
    )
    monkeypatch.setattr(hud, "draw_metrics", lambda *_args, **_kwargs: None)

    hud.draw_frame(
        pygame_display,
        pg.sprite.Group(),
        score=0,
        predator_mode="avoid",
        predator_attack_mode="nearest",
        game_over=False,
        performance=PerformanceMonitor(enabled=True),
        show_metrics=show_metrics,
        boid_count=0,
        flock_stats=FlockStats(False, 0, None),
        predator_pos=pg.Vector2(70, 80),
        detection_range=120.0,
    )

    assert circles == ([(pg.Vector2(70, 80), 120.0)] if show_metrics else [])
