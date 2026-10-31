class DocIntelligenceError(Exception):
    """Base exception for all errors in the doc-intelligence library."""

    def __init__(self, message: str):
        super().__init__(message)


class ParsingError(DocIntelligenceError):
    """Exception raised for errors during document parsing."""

    def __init__(self, message: str):
        super().__init__(message)


class UnsupportedDocumentTypeError(ParsingError):
    """Exception raised when a document type is not supported for parsing."""

    def __init__(self, message: str):
        super().__init__(message)


class RetrievalError(DocIntelligenceError):
    """Exception raised for general errors during retrieval."""

    def __init__(self, message: str):
        super().__init__(message)


class VectorStoreError(RetrievalError):
    """Exception raised for errors specific to the vector store operations."""

    def __init__(self, message: str):
        super().__init__(message)
