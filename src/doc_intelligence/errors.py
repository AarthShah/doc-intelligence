class DocIntelligenceError(Exception):
    """Base exception for all errors in the doc-intelligence library."""

    def __init__(self, message: str):
        super().__init__(message)
