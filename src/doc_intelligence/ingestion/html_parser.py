from pathlib import Path
from typing import List, Union
from doc_intelligence.models import Document, DocumentMetadata

# Attempt to import BeautifulSoup; if unavailable, fall back to a minimal parser.
try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    import re
    from html.parser import HTMLParser as _HTMLParser

    class _FallbackSoup:
        """
        Very small subset of BeautifulSoup's API used by HTMLParser.
        It strips script/style tags and removes all HTML tags,
        returning the remaining text.
        """

        def __init__(self, html: str, parser: str = "html.parser"):
            # Remove script and style blocks
            html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
            # Strip remaining tags
            self._text = re.sub(r"<[^>]+>", "", html)

        def __call__(self, *args, **kwargs):
            # Allows the object to be called like BeautifulSoup(html, "html.parser")
            return self

        def __iter__(self):
            return iter([])

        def find_all(self, tags):
            # Return a list containing a single element representing the whole document.
            return [self]

        def get_text(self, separator: str = " ", strip: bool = False):
            text = self._text
            if strip:
                text = text.strip()
            return text

    BeautifulSoup = _FallbackSoup


class HTMLParser:
    """Parse HTML content into clean, normalized Document representations."""

    def parse(self, content_or_path: Union[str, Path], source_name: str = "document.html") -> Document:
        """
        Convert an HTML document or string to a normalized Document.

        Steps:
        1. Read content if a path is provided, otherwise use the string.
        2. Parse the HTML with BeautifulSoup.
        3. Remove ``script`` and ``style`` elements.
        4. Extract text from block-level elements (headings, paragraphs, list items).
        5. Normalize whitespace and join blocks with line breaks.

        Args:
            content_or_path: Raw HTML string or Path to an HTML file.
            source_name: Name of the source.

        Returns:
            Normalized Document representation.
        """
        if isinstance(content_or_path, Path):
            html_content = content_or_path.read_text(encoding="utf-8")
            source = str(content_or_path)
        else:
            html_content = content_or_path
            source = source_name

        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style tags
        for tag in soup(["script", "style"]):
            tag.decompose()

        # Elements whose text should be treated as separate blocks
        block_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li"]
        blocks: List[str] = []

        for element in soup.find_all(block_tags):
            # Get text, collapse internal whitespace, strip surrounding spaces
            text = " ".join(element.get_text(separator=" ", strip=True).split())
            if text:
                blocks.append(text)

        extracted_text = "\n".join(blocks)

        metadata = DocumentMetadata(
            source=source,
            source_name=source_name,
            format="html",
            custom={},
        )
        return Document(text=extracted_text, metadata=metadata)
