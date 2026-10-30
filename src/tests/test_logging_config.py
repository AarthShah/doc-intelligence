import json
import logging
import sys
from doc_intelligence.logging_config import JSONFormatter, setup_logging


def test_json_formatter():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["message"] == "Test message"
    assert data["level"] == "INFO"
    assert data["logger"] == "test_logger"
    assert "timestamp" in data


def test_setup_logging(capsys):
    setup_logging(level="INFO")
    logger = logging.getLogger("doc_intelligence.test")
    logger.info("Hello structured log")

    # Verify root or handler has JSONFormatter
    root_logger = logging.getLogger()
    has_json_formatter = any(
        isinstance(handler.formatter, JSONFormatter)
        for handler in root_logger.handlers
    )
    assert has_json_formatter
