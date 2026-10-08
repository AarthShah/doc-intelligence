import time
import unittest
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class IngestionBenchmark(unittest.TestCase):
    """Base benchmark suite for evaluating ingestion throughput and accuracy."""

    def setUp(self) -> None:
        super().setUp()
        self.metrics: Dict[str, Any] = {}

    def time_operation(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[Any, float]:
        """Execute a function and measure its execution time in seconds."""
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_time = time.perf_counter() - start_time
        return result, elapsed_time

    def calculate_throughput(self, item_count: int, duration_seconds: float) -> float:
        """Calculate items processed per second."""
        if duration_seconds <= 0:
            return 0.0
        return item_count / duration_seconds

    def record_metric(self, name: str, value: Any) -> None:
        """Record a benchmark metric."""
        self.metrics[name] = value
