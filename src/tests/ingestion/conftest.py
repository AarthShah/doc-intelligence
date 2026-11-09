import os
import tempfile
import pytest
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


@pytest.fixture
def sample_two_column_pdf():
    """Create a temporary two-column PDF for testing multi-column extraction."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    try:
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # Left column
        c.drawString(54, height - 100, "Left column text line 1.")
        c.drawString(54, height - 115, "Left column text line 2.")

        # Right column
        c.drawString(width / 2 + 20, height - 100, "Right column text line 1.")
        c.drawString(width / 2 + 20, height - 115, "Right column text line 2.")

        c.showPage()
        c.save()

        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)


@pytest.fixture
def sample_html_snippets():
    """Provides a dictionary of diverse HTML strings for testing HTMLParser."""
    return {
        "simple_paragraph": "<p>This is a simple paragraph.</p>",
        "table_with_merged_cells": """
        <table>
            <thead>
                <tr>
                    <th colspan="2">Merged Header</th>
                    <th>Column 3</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Row 1, Col 1</td>
                    <td>Row 1, Col 2</td>
                    <td>Row 1, Col 3</td>
                </tr>
                <tr>
                    <td rowspan="2">Merged Row</td>
                    <td>Row 2, Col 2</td>
                    <td>Row 2, Col 3</td>
                </tr>
                <tr>
                    <td>Row 3, Col 2</td>
                    <td>Row 3, Col 3</td>
                </tr>
            </tbody>
        </table>
        """,
        "nested_divs": """
        <div>
            <h1>Main Title</h1>
            <div>
                <p>Paragraph inside first div.</p>
                <span>Span inside first div.</span>
                <div>
                    <p>Paragraph inside nested div.</p>
                </div>
            </div>
            <p>Another paragraph.</p>
        </div>
        """,
        "malformed_tags": """
        <p>This is <strong_broken>malformed</p> HTML with <img src="test.jpg" alt="test" /> missing closing tag.
        <div>Unclosed div.
        """,
        "script_block": """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
            <script type="text/javascript">
                function greet() {
                    alert("Hello, World!");
                }
            </script>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>This is a paragraph.</p>
        </body>
        </html>
        """,
        "html_with_comments": """
        <!-- This is a comment -->
        <p>Some visible text.</p>
        <!-- Another comment -->
        <div>
            <!-- Inner comment -->
            <span>More text.</span>
        </div>
        """,
        "html_with_attributes": """
        <p class="intro" id="first-p">This paragraph has attributes.</p>
        <a href="https://example.com" target="_blank">Link</a>
        """,
        "empty_html": "",
        "whitespace_only": "   \n\t ",
    }


@pytest.fixture
def sample_multi_page_pdf():
    """Create a temporary multi-page PDF with empty columns and spanning text for testing."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    try:
        c = canvas.Canvas(path, pagesize=letter)
        width, height = letter

        # Page 1: Left column has content, right column is empty
        c.drawString(54, height - 100, "Page 1 left content")
        c.showPage()

        # Page 2: Left column is empty, right column has content continuing across pages
        c.drawString(width / 2 + 20, height - 100, "Page 2 right content continuation")
        c.showPage()

        c.save()

        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)
