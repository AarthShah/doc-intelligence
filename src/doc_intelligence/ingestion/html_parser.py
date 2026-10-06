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

        def find_all(self, tags):
            # Return a list containing a single element representing the whole document.
            return [self]

        def get_text(self, separator: str = " ", strip: bool = False):
            text = self._text
            if strip:
                text = text.strip()
            return text

    BeautifulSoup = _FallbackSoup
from typing import List


class HTMLParser:
    """Parse HTML content into clean, normalized plain text."""

    def parse(self, html: str) -> str:
        """
        Convert an HTML document to plain text.

        Steps:
        1. Parse the HTML with BeautifulSoup.
        2. Remove ``script`` and ``style`` elements.
        3. Extract text from block‑level elements (headings, paragraphs, list items).
        4. Normalize whitespace and join blocks with line breaks.

        Args:
            html: Raw HTML string.

        Returns:
            Normalized plain‑text representation of the HTML.
        """
        soup = BeautifulSoup(html, "html.parser")

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

        # Join blocks with a newline to preserve a readable structure
        return "\n".join(blocks)
