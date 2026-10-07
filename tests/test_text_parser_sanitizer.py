from unittest.mock import Mock

from src.doc_intelligence.ingestion.text_parser import TextParser


def test_text_parser_uses_sanitizer():
    raw_text = "Contact me at alice@example.com."
    mock_sanitizer = Mock()
    mock_sanitizer.sanitize.return_value = "sanitized content"

    parser = TextParser()
    doc = parser.parse(raw_text, sanitizer=mock_sanitizer)

    assert doc.text == "sanitized content"
    mock_sanitizer.sanitize.assert_called_once_with(raw_text.strip())
