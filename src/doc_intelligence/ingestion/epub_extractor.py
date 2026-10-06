import zipfile
from typing import List, Dict

# The `ebooklib` package provides EPUB parsing utilities. It is an optional
# dependency for the ePub ingestion feature. Import it lazily so that the rest
# of the library (e.g., PDF extraction) can be used without requiring the
# package to be installed.
try:
    from ebooklib import epub  # type: ignore
except Exception:  # pragma: no cover
    epub = None

from .html_parser import HTMLParser


class EpubExtractor:
    """Extracts structured text from an EPUB file."""

    def __init__(self, file_path: str):
        """
        Initialize the extractor.

        Parameters
        ----------
        file_path: str
            Path to the EPUB file to be processed.
        """
        if epub is None:
            raise ImportError(
                "The 'ebooklib' package is required for EpubExtractor but is not installed. "
                "Install it with `pip install ebooklib`."
            )
        self.file_path = file_path
        self._parser = HTMLParser()
        self._parser = HTMLParser()

    def extract(self) -> List[Dict[str, str]]:
        """Parse the EPUB and return a list of dictionaries with keys
        ``title``, ``chapter`` and ``text``.
        """
        # Ensure the file is a valid zip archive (EPUBs are zip files)
        if not zipfile.is_zipfile(self.file_path):
            raise ValueError(f"The file {self.file_path} is not a valid EPUB archive.")

        book = epub.read_epub(self.file_path)

        # Retrieve the book title from metadata if available
        title_meta = book.get_metadata("DC", "title")
        book_title = title_meta[0][0] if title_meta else ""

        chapters: List[Dict[str, str]] = []
        for item in book.get_items():
            # Process only document (XHTML) items
            if item.get_type() == epub.ITEM_DOCUMENT:
                raw_html = item.get_content()
                if isinstance(raw_html, bytes):
                    raw_html = raw_html.decode("utf-8", errors="ignore")
                text = self._parser.parse(raw_html)
                chapter_name = item.get_name()
                chapters.append(
                    {
                        "title": book_title,
                        "chapter": chapter_name,
                        "text": text,
                    }
                )
        return chapters
