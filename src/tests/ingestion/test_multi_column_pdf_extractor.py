import io
import pytest
from doc_intelligence.ingestion.pdf_extractor import MultiColumnPDFExtractor

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


@pytest.mark.skipif(not HAS_REPORTLAB, reason="reportlab is required to generate test PDFs")
def test_multi_column_pdf_extraction(tmp_path):
    pdf_path = tmp_path / "test_multicolumn.pdf"
    
    # Generate a simple two-column layout PDF
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Left column
    c.drawString(54, height - 100, "Left column text content")
    
    # Right column
    c.drawString(width / 2 + 20, height - 100, "Right column text content")
    
    c.save()
    
    extractor = MultiColumnPDFExtractor()
    document = extractor.extract(str(pdf_path))
    
    assert document is not None
    content = document.content
    assert "Left column text content" in content
    assert "Right column text content" in content


@pytest.mark.skipif(not HAS_REPORTLAB, reason="reportlab is required to generate test PDFs")
def test_multi_column_multi_page_pdf_extraction(sample_multi_page_pdf):
    extractor = MultiColumnPDFExtractor()
    document = extractor.extract(sample_multi_page_pdf)

    assert document is not None
    content = document.content
    assert "Page 1 left content" in content
    assert "Page 2 right content continuation" in content
