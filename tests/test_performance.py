"""Tests for performance.py"""

import time

from my_boids.performance import FrameMetrics, PerformanceMonitor


def test_frame_metrics_creation():
    """Test creating a FrameMetrics object."""
    metrics = FrameMetrics(frame_time=0.016)
    assert metrics.frame_time == 0.016
    assert metrics.update_time == 0.0
    assert metrics.logic_time == 0.0


def test_performance_monitor_initialization():
    """Test PerformanceMonitor initializes correctly."""
    monitor = PerformanceMonitor()
    assert monitor.enabled is True
    assert monitor.max_samples == 60
    assert len(monitor.frame_times) == 0


def test_performance_monitor_disabled():
    """Test PerformanceMonitor can be disabled."""
    monitor = PerformanceMonitor(enabled=False)
    monitor.start_frame()
    monitor.end_frame()
    assert len(monitor.frame_times) == 0


def test_performance_monitor_frame_tracking():
    """Test tracking frame times."""
    monitor = PerformanceMonitor()

    monitor.start_frame()
    time.sleep(0.01)  # Simulate some work
    monitor.end_frame()

    assert len(monitor.frame_times) == 1
    assert monitor.frame_times[0] >= 0.01


def test_performance_monitor_multiple_frames():
    """Test tracking multiple frames."""
    monitor = PerformanceMonitor(max_samples=5)

    for _ in range(10):
        monitor.start_frame()
        monitor.end_frame()

    # Should only keep the last 5 samples
    assert len(monitor.frame_times) == 5


def test_performance_monitor_operation_timing():
    """Test timing individual operations."""
    monitor = PerformanceMonitor()

    monitor.start_frame()

    monitor.start_operation()
    time.sleep(0.005)
    monitor.end_operation("update")

    monitor.start_operation()
    time.sleep(0.005)
    monitor.end_operation("logic")

    monitor.end_frame()

    assert monitor.current_metrics is not None
    assert monitor.current_metrics.update_time >= 0.005
    assert monitor.current_metrics.logic_time >= 0.005


def test_get_fps_no_samples():
    """Test FPS calculation with no samples."""
    monitor = PerformanceMonitor()
    assert monitor.get_fps() == 0.0


def test_get_fps_with_samples():
    """Test FPS calculation with samples."""
    monitor = PerformanceMonitor()

    # Simulate 60 FPS (16.67ms per frame)
    for _ in range(10):
        monitor.start_frame()
        time.sleep(0.01)  # ~100 FPS
        monitor.end_frame()

    fps = monitor.get_fps()
    # Should be around 100 FPS (may vary slightly due to timing precision)
    assert 70 <= fps <= 130


def test_get_avg_frame_time():
    """Test average frame time calculation."""
    monitor = PerformanceMonitor()

    for _ in range(5):
        monitor.start_frame()
        time.sleep(0.01)
        monitor.end_frame()

    avg_time = monitor.get_avg_frame_time()
    # Should be around 10ms
    assert 9 <= avg_time <= 15


def test_get_min_max_frame_time():
    """Test min and max frame time calculation."""
    monitor = PerformanceMonitor()

    # First frame - short
    monitor.start_frame()
    time.sleep(0.005)
    monitor.end_frame()

    # Second frame - longer
    monitor.start_frame()
    time.sleep(0.015)
    monitor.end_frame()

    min_time = monitor.get_min_frame_time()
    max_time = monitor.get_max_frame_time()

    assert min_time < max_time
    assert 4 <= min_time <= 10
    assert 14 <= max_time <= 20


def test_get_performance_summary():
    """Test getting a performance summary."""
    monitor = PerformanceMonitor()

    for _ in range(5):
        monitor.start_frame()
        time.sleep(0.01)
        monitor.end_frame()

    summary = monitor.get_performance_summary()

    assert "fps" in summary
    assert "avg_frame_time_ms" in summary
    assert "min_frame_time_ms" in summary
    assert "max_frame_time_ms" in summary

    assert summary["fps"] > 0
    assert summary["avg_frame_time_ms"] > 0


def test_reset():
    """Test resetting the performance monitor."""
    monitor = PerformanceMonitor()

    for _ in range(5):
        monitor.start_frame()
        monitor.end_frame()

    assert len(monitor.frame_times) == 5

    monitor.reset()

    assert len(monitor.frame_times) == 0
    assert monitor.current_metrics is None


def test_operation_types():
    """Test all supported operation types."""
    monitor = PerformanceMonitor()

    monitor.start_frame()

    operations = ["update", "logic", "collision", "render"]
    for op in operations:
        monitor.start_operation()
        time.sleep(0.001)
        monitor.end_operation(op)

    monitor.end_frame()

    assert monitor.current_metrics is not None
    assert monitor.current_metrics.update_time > 0
    assert monitor.current_metrics.logic_time > 0
    assert monitor.current_metrics.collision_time > 0
    assert monitor.current_metrics.render_time > 0
