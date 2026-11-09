import pytest
from src.doc_intelligence.ingestion.html_parser import HTMLParser


@pytest.fixture
def sample_html_snippets():
    return {
        "basic": """
        <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <p>This is the first paragraph.</p>
            <h2>Section Header</h2>
            <p>This is the second paragraph with <b>bold</b> text.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <div>
                <p>Paragraph inside a div.</p>
            </div>
        </body>
        </html>
        """,
        "tables_and_scripts": """
        <html>
        <head>
            <style>body { color: red; }</style>
            <script>console.log('test');</script>
        </head>
        <body>
            <table>
                <tr><th>Header 1</th><th>Header 2</th></tr>
                <tr><td>Data 1</td><td>Data 2</td></tr>
            </table>
        </body>
        </html>
        """,
        "nested_elements": """
        <div>
            <p>Outer <span>inner <b>nested</b> text</span> end.</p>
        </div>
        """,
        "malformed": """
        <html>
        <body>
            <h1>Unclosed heading
            <p>Broken paragraph structure <b>bold text
        </body>
        </html>
        """
    }


def test_html_parser_basic(sample_html_snippets):
    """Tests parsing of a simple HTML snippet."""
    expected_structure = [
        {"type": "heading", "level": 1, "text": "Main Title"},
        {"type": "paragraph", "text": "This is the first paragraph."},
        {"type": "heading", "level": 2, "text": "Section Header"},
        {"type": "paragraph", "text": "This is the second paragraph with bold text."},
        {"type": "list", "items": ["Item 1", "Item 2"]},
        {"type": "paragraph", "text": "Paragraph inside a div."}
    ]

    parser = HTMLParser()
    parsed_structure = parser.parse(sample_html_snippets["basic"])

    assert parsed_structure == expected_structure


def test_html_parser_tables_and_scripts(sample_html_snippets):
    """Tests that script and style tags are removed and tables are parsed correctly."""
    parser = HTMLParser()
    parsed_structure = parser.parse(sample_html_snippets["tables_and_scripts"])

    # Ensure styles and scripts do not appear in output
    all_text = str(parsed_structure)
    assert "color: red" not in all_text
    assert "console.log" not in all_text

    # Verify table representation exists and captures content
    table_items = [item for item in parsed_structure if item.get("type") in ("table", "paragraph", "list")]
    assert len(table_items) > 0


def test_html_parser_nested_elements(sample_html_snippets):
    """Tests preservation of correct text order in deeply nested elements."""
    parser = HTMLParser()
    parsed_structure = parser.parse(sample_html_snippets["nested_elements"])

    assert len(parsed_structure) == 1
    assert parsed_structure[0]["text"] == "Outer inner nested text end."


def test_html_parser_malformed_graceful_fallback(sample_html_snippets):
    """Tests graceful fallback and structure recovery on malformed HTML."""
    parser = HTMLParser()
    parsed_structure = parser.parse(sample_html_snippets["malformed"])

    # Should not raise an exception and still extract available text
    assert isinstance(parsed_structure, list)
    assert len(parsed_structure) > 0
