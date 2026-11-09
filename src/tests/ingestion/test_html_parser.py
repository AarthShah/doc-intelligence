from src.doc_intelligence.ingestion.html_parser import HTMLParser


def test_html_parser_basic():
    """Tests parsing of a simple HTML snippet."""
    html_content = """
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
    """
    expected_structure = [
        {"type": "heading", "level": 1, "text": "Main Title"},
        {"type": "paragraph", "text": "This is the first paragraph."},
        {"type": "heading", "level": 2, "text": "Section Header"},
        {"type": "paragraph", "text": "This is the second paragraph with bold text."},
        {"type": "list", "items": ["Item 1", "Item 2"]},
        {"type": "paragraph", "text": "Paragraph inside a div."}
    ]

    parser = HTMLParser()
    parsed_structure = parser.parse(html_content)

    assert parsed_structure == expected_structure
