import pytest
from doc_intelligence.chunking import RecursiveCharacterTextSplitter

def test_recursive_character_text_splitter_import():
    """Verify that RecursiveCharacterTextSplitter is exported correctly."""
    assert RecursiveCharacterTextSplitter is not None
    assert isinstance(RecursiveCharacterTextSplitter, type)
