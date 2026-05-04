"""Performance monitoring and metrics tracking for the boids simulation."""

import time
from collections import deque
from dataclasses import dataclass


@dataclass
class FrameMetrics:
    """Metrics for a single frame.

    Attributes:
        frame_time: Total time to process the frame in seconds.
        update_time: Time spent updating sprites in seconds.
        logic_time: Time spent applying boid rules in seconds.
        collision_time: Time spent checking collisions in seconds.
        render_time: Time spent rendering in seconds.
    """

    frame_time: float
    update_time: float = 0.0
    logic_time: float = 0.0
    collision_time: float = 0.0
    render_time: float = 0.0


class PerformanceMonitor:
    """Monitor and track performance metrics for the simulation.

    This class tracks frame times and calculates statistics like FPS,
    average frame time, and timing breakdowns for different operations.

    Attributes:
        enabled (bool): Whether performance monitoring is active.
        max_samples (int): Maximum number of frame samples to keep.
        frame_times (deque): Recent frame times in seconds.
        current_metrics (FrameMetrics | None): Metrics for the current frame.
    """

    def __init__(self, enabled: bool = True, max_samples: int = 60):
        """Initialize the performance monitor.

        Args:
            enabled (bool): Whether to enable performance tracking. Defaults to True.
            max_samples (int): Number of frame samples to keep for averaging.
                Defaults to 60 (approximately 1 second at 60 FPS).
        """
        self.enabled = enabled
        self.max_samples = max_samples
        self.frame_times: deque[float] = deque(maxlen=max_samples)
        self.current_metrics: FrameMetrics | None = None
        self._frame_start_time: float = 0.0
        self._operation_start_time: float = 0.0

    def start_frame(self) -> None:
        """Mark the start of a new frame."""
        if not self.enabled:
            return
        self._frame_start_time = time.perf_counter()
        self.current_metrics = FrameMetrics(frame_time=0.0)

    def end_frame(self) -> None:
        """Mark the end of a frame and record its duration."""
        if not self.enabled or self.current_metrics is None:
            return
        frame_time = time.perf_counter() - self._frame_start_time
        self.current_metrics.frame_time = frame_time
        self.frame_times.append(frame_time)

    def start_operation(self) -> None:
        """Mark the start of a timed operation."""
        if not self.enabled:
            return
        self._operation_start_time = time.perf_counter()

    def end_operation(self, operation: str) -> None:
        """Mark the end of a timed operation and record its duration.

        Args:
            operation (str): Name of the operation. One of: 'update', 'logic',
                'collision', 'render'.
        """
        if not self.enabled or self.current_metrics is None:
            return
        elapsed = time.perf_counter() - self._operation_start_time

        if operation == "update":
            self.current_metrics.update_time = elapsed
        elif operation == "logic":
            self.current_metrics.logic_time = elapsed
        elif operation == "collision":
            self.current_metrics.collision_time = elapsed
        elif operation == "render":
            self.current_metrics.render_time = elapsed

    def get_fps(self) -> float:
        """Calculate the current frames per second.

        Returns:
            float: Current FPS, or 0.0 if no samples available.
        """
        if not self.frame_times:
            return 0.0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

    def get_avg_frame_time(self) -> float:
        """Calculate the average frame time in milliseconds.

        Returns:
            float: Average frame time in milliseconds, or 0.0 if no samples.
        """
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000

    def get_min_frame_time(self) -> float:
        """Get the minimum frame time in milliseconds.

        Returns:
            float: Minimum frame time in milliseconds, or 0.0 if no samples.
        """
        if not self.frame_times:
            return 0.0
        return min(self.frame_times) * 1000

    def get_max_frame_time(self) -> float:
        """Get the maximum frame time in milliseconds.

        Returns:
            float: Maximum frame time in milliseconds, or 0.0 if no samples.
        """
        if not self.frame_times:
            return 0.0
        return max(self.frame_times) * 1000

    def get_performance_summary(self) -> dict[str, float]:
        """Get a summary of performance metrics.

        Returns:
            dict[str, float]: Dictionary containing FPS and timing statistics.
        """
        return {
            "fps": self.get_fps(),
            "avg_frame_time_ms": self.get_avg_frame_time(),
            "min_frame_time_ms": self.get_min_frame_time(),
            "max_frame_time_ms": self.get_max_frame_time(),
        }

    def reset(self) -> None:
        """Clear all collected metrics."""
        self.frame_times.clear()
        self.current_metrics = None
