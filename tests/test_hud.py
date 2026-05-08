"""Focused tests for HUD rendering helpers."""

import pygame as pg

from my_boids import hud
from my_boids.performance import FrameMetrics, PerformanceMonitor
from my_boids.spatial_grid import SpatialGrid


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
    spatial_grid = SpatialGrid(cell_size=25.0)

    hud.draw_metrics(
        pygame_display,
        performance,
        boid_count=12,
        use_spatial_grid=True,
        spatial_grid=spatial_grid,
    )

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
        score=0,
        predator_mode="avoid",
        predator_attack_mode="center",
        game_over=True,
        performance=PerformanceMonitor(enabled=True),
        show_metrics=True,
        boid_count=0,
        use_spatial_grid=False,
        spatial_grid=None,
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
        use_spatial_grid=False,
        spatial_grid=None,
    )

    assert "sprites" in calls
    assert "score" in calls
    assert "predator_mode" in calls
    assert "predator_attack_mode" in calls
    assert "metrics" in calls
    assert "game_over" not in calls
