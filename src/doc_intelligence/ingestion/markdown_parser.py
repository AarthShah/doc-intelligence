"""Markdown document parser extracting headers, sections, and tables."""

import re
from pathlib import Path
from typing import List, Union
from doc_intelligence.models import Document, DocumentMetadata


class MarkdownParser:
    """Parses Markdown content and extracts structural hierarchy."""

    HEADER_REGEX = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def parse(self, content_or_path: Union[str, Path], source_name: str = "document.md") -> Document:
        """Parse Markdown file or raw string into a structured Document."""
        if isinstance(content_or_path, Path) or (isinstance(content_or_path, str) and Path(content_or_path).is_file()):
            path = Path(content_or_path)
            text = path.read_text(encoding="utf-8", errors="replace")
            src = path.name
        else:
            text = str(content_or_path)
            src = source_name

        headers: List[str] = [m.group(2).strip() for m in self.HEADER_REGEX.finditer(text)]

        metadata = DocumentMetadata(
            source_name=src,
            format="markdown",
            custom={
                "headings": headers,
                "heading_count": len(headers),
                "char_length": len(text),
            },
        )
        return Document(text=text.strip(), metadata=metadata)
