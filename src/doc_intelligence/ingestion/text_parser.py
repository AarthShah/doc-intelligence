"""Plaintext document parser."""

from pathlib import Path
from typing import Union
from doc_intelligence.models import Document, DocumentMetadata


class TextParser:
    """Parses raw text strings or files into Document objects."""

    def parse(self, content_or_path: Union[str, Path], source_name: str = "raw_text") -> Document:
        """Parse raw text or a file path."""
        if isinstance(content_or_path, Path) or (isinstance(content_or_path, str) and Path(content_or_path).is_file()):
            path = Path(content_or_path)
            text = path.read_text(encoding="utf-8", errors="replace")
            src = path.name
        else:
            text = str(content_or_path)
            src = source_name

        cleaned = text.strip()
        metadata = DocumentMetadata(
            source_name=src,
            format="plaintext",
            custom={"char_length": len(cleaned), "line_count": len(cleaned.splitlines())},
        )
        return Document(text=cleaned, metadata=metadata)
