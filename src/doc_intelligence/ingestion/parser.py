from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Optional
from doc_intelligence.exceptions import ParsingError, UnsupportedDocumentTypeError
from doc_intelligence.models import Document
from doc_intelligence.sanitizer import DocumentSanitizer


class BaseParser(ABC):
    """Abstract base class for document parsers."""

    @abstractmethod
    def parse(
        self,
        content_or_path: Union[str, Path],
        source_name: str = "document",
        sanitizer: Optional[DocumentSanitizer] = None,
    ) -> Document:
        """Parse content or file path into a Document object."""
        try:
            # Placeholder for actual parsing logic which might raise errors
            # For demonstration, we'll simulate a potential error
            if isinstance(content_or_path, Path) and content_or_path.suffix.lower() not in [".txt", ".md"]:
                raise UnsupportedDocumentTypeError(f"Unsupported document type: {content_or_path.suffix}")

            # Simulate a general parsing error
            if "error" in str(content_or_path).lower():
                raise ValueError("Simulated parsing error")

            # Actual parsing logic would go here.
            # For now, we create a dummy document.
            document_content = str(content_or_path)
            if sanitizer:
                document_content = sanitizer.sanitize(document_content)
            return Document(content=document_content, metadata={"source": source_name})

        except UnsupportedDocumentTypeError:
            raise
        except ValueError as e:
            raise ParsingError(f"Failed to parse document: {e}") from e
        except Exception as e:
            raise ParsingError(f"An unexpected error occurred during parsing: {e}") from e
