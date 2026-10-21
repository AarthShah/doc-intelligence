from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Optional
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
        pass
