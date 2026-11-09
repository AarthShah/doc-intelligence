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
