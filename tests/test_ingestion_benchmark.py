import time
import unittest
from pathlib import Path
import tempfile
from typing import Any, Callable, Dict, List, Optional
from doc_intelligence.ingestion.text_parser import TextParser


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

    def test_text_parser_ingestion_benchmark(self) -> None:
        """Benchmark TextParser ingestion throughput with a large text file."""
        parser = TextParser()
        # Generate a sufficiently large text file for meaningful benchmarking
        line_count = 5000
        content = "\n".join([f"This is line number {i} containing some sample text for benchmarking ingestion performance." for i in range(line_count)])

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "large_benchmark_document.txt"
            file_path.write_text(content, encoding="utf-8")

            # Time the parse operation
            doc, duration = self.time_operation(parser.parse, file_path, source_name="benchmark_doc")

            # Calculate throughput (documents per second, or lines/items)
            throughput = self.calculate_throughput(1, duration)

            self.record_metric("text_parser_duration_seconds", duration)
            self.record_metric("text_parser_throughput_docs_per_sec", throughput)
            self.record_metric("text_parser_line_count", line_count)

            self.assertIsNotNone(doc)
            self.assertEqual(doc.metadata.source_name, "large_benchmark_document.txt")
            self.assertGreater(duration, 0.0)
