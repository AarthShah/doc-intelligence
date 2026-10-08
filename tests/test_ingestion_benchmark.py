import time
import unittest
from pathlib import Path
import tempfile
from typing import Any, Callable, Dict, List, Optional
import io
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.ingestion.pdf_extractor import MultiColumnPDFExtractor
from doc_intelligence.ingestion.html_parser import HTMLParser


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

    def test_pdf_extractor_ingestion_benchmark(self) -> None:
        """Benchmark MultiColumnPDFExtractor ingestion throughput."""
        extractor = MultiColumnPDFExtractor()
        # Minimal valid PDF content to satisfy PDFMiner
        pdf_content = (
            b"%PDF-1.0\n"
            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] >>\nendobj\n"
            b"trailer\n<< /Root 1 0 R >>\n%%EOF"
        )
        pdf_stream = io.BytesIO(pdf_content)
        
        # Time the parse operation
        doc, duration = self.time_operation(extractor.parse, pdf_stream, source_name="benchmark_doc.pdf")

        # Calculate throughput
        throughput = self.calculate_throughput(1, duration)

        self.record_metric("pdf_extractor_duration_seconds", duration)
        self.record_metric("pdf_extractor_throughput_docs_per_sec", throughput)

        self.assertIsNotNone(doc)
        self.assertGreater(duration, 0.0)

    def test_html_parser_ingestion_benchmark(self) -> None:
        """Benchmark HTMLParser ingestion throughput with multiple HTML documents."""
        parser = HTMLParser()
        doc_count = 50
        html_contents = [
            f"<html><head><title>Doc {i}</title></head><body><script>var x = 1;</script><style>body {{ color: red; }}</style><h1>Heading {i}</h1><p>This is paragraph content for HTML benchmark document number {i}.</p></body></html>"
            for i in range(doc_count)
        ]

        start_time = time.perf_counter()
        parsed_docs = [parser.parse(html) for html in html_contents]
        duration = time.perf_counter() - start_time

        throughput = self.calculate_throughput(doc_count, duration)

        self.record_metric("html_parser_duration_seconds", duration)
        self.record_metric("html_parser_throughput_docs_per_sec", throughput)
        self.record_metric("html_parser_doc_count", doc_count)

        self.assertEqual(len(parsed_docs), doc_count)
        for doc in parsed_docs:
            self.assertIsNotNone(doc)
            self.assertIn("paragraph content", doc.content)
        self.assertGreater(duration, 0.0)
