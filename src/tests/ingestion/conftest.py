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
