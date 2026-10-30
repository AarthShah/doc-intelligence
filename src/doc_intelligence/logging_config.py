import json
import logging
import sys
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Formatter that outputs JSON strings."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger to use JSON formatting."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicate logs
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.addHandler(handler)
