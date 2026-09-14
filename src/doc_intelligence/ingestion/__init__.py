"""Ingestion subsystem: Document parsers and normalizers."""

from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.ingestion.markdown_parser import MarkdownParser

__all__ = ["TextParser", "MarkdownParser"]
