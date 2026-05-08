"""HUD rendering helpers for the boids simulation."""

import pygame as pg

from my_boids.options import PredatorAttackMode, PredatorBehaviorMode
from my_boids.performance import PerformanceMonitor
from my_boids.spatial_grid import SpatialGrid


def draw_score(screen: pg.Surface, score: int) -> None:
    """Draw the current score."""
    winsize = screen.get_size()
    font = pg.font.SysFont("serif", 25)
    text = font.render(f"Score: {score}", True, pg.Color("white"))
    text_rect = text.get_rect()
    text_rect.topright = (winsize[0] - 10, 10)
    screen.blit(text, text_rect)


def draw_predator_mode(screen: pg.Surface, mode: PredatorBehaviorMode) -> None:
    """Draw the current predator behavior mode."""
    font = pg.font.SysFont("serif", 25)
    text = font.render(f"Predator Mode: {mode.upper()}", True, pg.Color("white"))
    text_rect = text.get_rect()
    text_rect.topleft = (10, 10)
    screen.blit(text, text_rect)


def draw_predator_attack_mode(screen: pg.Surface, attack_mode: PredatorAttackMode) -> None:
    """Draw the current predator attack mode."""
    font = pg.font.SysFont("serif", 25)
    strategy_labels = {
        "mouse": "Mouse Cursor",
        "center": "Flock Center",
        "nearest": "Nearest Bird",
        "isolated": "Most Isolated Bird",
    }
    strategy_text = strategy_labels.get(attack_mode, attack_mode.replace("_", " ").title())
    text = font.render(f"Predator Attack Mode: {strategy_text}", True, pg.Color("white"))
    text_rect = text.get_rect()
    text_rect.topleft = (10, 38)
    screen.blit(text, text_rect)


def draw_game_over(screen: pg.Surface) -> None:
    """Draw the game over message."""
    winsize = screen.get_size()
    font = pg.font.SysFont("serif", 25)
    text = font.render("Game Over, click to restart", True, pg.Color("white"))
    text_rect = text.get_rect()
    text_rect.center = (winsize[0] // 2, winsize[1] // 2)
    screen.blit(text, text_rect)


def draw_metrics(
    screen: pg.Surface,
    performance: PerformanceMonitor,
    boid_count: int,
    use_spatial_grid: bool,
    spatial_grid: SpatialGrid | None,
) -> None:
    """Draw performance metrics."""
    font = pg.font.SysFont("monospace", 14)
    y_offset = 10

    fps = performance.get_fps()
    avg_frame_time = performance.get_avg_frame_time()
    metrics = [
        f"FPS: {fps:.1f}",
        f"Frame: {avg_frame_time:.2f}ms",
        f"Boids: {boid_count}",
    ]

    if use_spatial_grid and spatial_grid is not None:
        metrics.append(f"Grid: {spatial_grid.get_cell_count()} cells")
        metrics.append("Mode: Spatial")
    else:
        metrics.append("Mode: Brute Force")

    if performance.current_metrics:
        metrics_state = performance.current_metrics
        metrics.append(f"Update: {metrics_state.update_time * 1000:.2f}ms")
        metrics.append(f"Logic: {metrics_state.logic_time * 1000:.2f}ms")
        metrics.append(f"Collision: {metrics_state.collision_time * 1000:.2f}ms")
        metrics.append(f"Render: {metrics_state.render_time * 1000:.2f}ms")

    for line in metrics:
        text = font.render(line, True, pg.Color("green"))
        screen.blit(text, (10, y_offset))
        y_offset += 18


def draw_frame(
    screen: pg.Surface,
    all_sprites: pg.sprite.Group,
    score: int,
    predator_mode: PredatorBehaviorMode,
    predator_attack_mode: PredatorAttackMode,
    game_over: bool,
    performance: PerformanceMonitor,
    show_metrics: bool,
    boid_count: int,
    use_spatial_grid: bool,
    spatial_grid: SpatialGrid | None,
) -> None:
    """Draw the complete simulation frame."""
    screen.fill(pg.Color("black"))

    if game_over:
        draw_game_over(screen)
        return

    all_sprites.draw(screen)
    draw_score(screen, score)
    draw_predator_mode(screen, predator_mode)
    draw_predator_attack_mode(screen, predator_attack_mode)
    if show_metrics:
        draw_metrics(screen, performance, boid_count, use_spatial_grid, spatial_grid)
