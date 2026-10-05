import io
import unittest
from pathlib import Path
from typing import Dict, List, Tuple
from unittest.mock import MagicMock, patch

from pdfminer.layout import LTChar, LTTextLineHorizontal, LTTextBoxHorizontal

from src.doc_intelligence.models import Document, DocumentMetadata
from src.doc_intelligence.ingestion.pdf_extractor import MultiColumnPDFExtractor, TextBlock


class TestMultiColumnPDFExtractor(unittest.TestCase):
    """Test suite for MultiColumnPDFExtractor functionalities."""

    def setUp(self):
        self.extractor = MultiColumnPDFExtractor(
            header_margin_ratio=0.1,
            footer_margin_ratio=0.1,
            column_tolerance=0.05,
            line_spacing_tolerance=0.5,
            min_header_footer_text_len=10,
            min_pages_for_hf_detection=2,
        )
        self.mock_page_dimensions = {
            1: (600, 800),  # width, height for page 1
            2: (600, 800),  # width, height for page 2
            3: (600, 800),  # width, height for page 3
        }

    def create_mock_blocks(self, blocks_data: List[Dict]) -> List[TextBlock]:
        """Helper to create TextBlock instances from simplified data."""
        return [
            TextBlock(
                text=data["text"],
                bbox=tuple(data["bbox"]),
                page_num=data["page_num"],
                font_size=data.get("font_size"),
            )
            for data in blocks_data
        ]

    def test_single_column_ordering(self):
        blocks_data = [
            {"text": "Block C", "bbox": (50, 200, 250, 220), "page_num": 1},
            {"text": "Block A", "bbox": (50, 400, 250, 420), "page_num": 1},
            {"text": "Block B", "bbox": (50, 300, 250, 320), "page_num": 1},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        ordered_blocks = self.extractor._group_blocks_into_columns_and_reorder(
            mock_blocks, self.mock_page_dimensions[1][0]
        )
        self.assertEqual(len(ordered_blocks), 3)
        self.assertEqual(ordered_blocks[0].text, "Block A")
        self.assertEqual(ordered_blocks[1].text, "Block B")
        self.assertEqual(ordered_blocks[2].text, "Block C")

    def test_two_column_ordering(self):
        blocks_data = [
            {"text": "Left Col A", "bbox": (50, 400, 250, 420), "page_num": 1},
            {"text": "Right Col A", "bbox": (300, 400, 500, 420), "page_num": 1},
            {"text": "Left Col B", "bbox": (50, 300, 250, 320), "page_num": 1},
            {"text": "Right Col B", "bbox": (300, 300, 500, 320), "page_num": 1},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        ordered_blocks = self.extractor._group_blocks_into_columns_and_reorder(
            mock_blocks, self.mock_page_dimensions[1][0]
        )
        self.assertEqual(len(ordered_blocks), 4)
        # Expected order: Left A, Left B, Right A, Right B
        self.assertEqual(ordered_blocks[0].text, "Left Col A")
        self.assertEqual(ordered_blocks[1].text, "Left Col B")
        self.assertEqual(ordered_blocks[2].text, "Right Col A")
        self.assertEqual(ordered_blocks[3].text, "Right Col B")

    def test_three_column_ordering(self):
        blocks_data = [
            {"text": "C1-A", "bbox": (50, 400, 150, 420), "page_num": 1},
            {"text": "C2-A", "bbox": (200, 400, 300, 420), "page_num": 1},
            {"text": "C3-A", "bbox": (350, 400, 450, 420), "page_num": 1},
            {"text": "C1-B", "bbox": (50, 300, 150, 320), "page_num": 1},
            {"text": "C2-B", "bbox": (200, 300, 300, 320), "page_num": 1},
            {"text": "C3-B", "bbox": (350, 300, 450, 320), "page_num": 1},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        ordered_blocks = self.extractor._group_blocks_into_columns_and_reorder(
            mock_blocks, self.mock_page_dimensions[1][0]
        )
        self.assertEqual(len(ordered_blocks), 6)
        # Expected order: C1-A, C1-B, C2-A, C2-B, C3-A, C3-B
        self.assertEqual(ordered_blocks[0].text, "C1-A")
        self.assertEqual(ordered_blocks[1].text, "C1-B")
        self.assertEqual(ordered_blocks[2].text, "C2-A")
        self.assertEqual(ordered_blocks[3].text, "C2-B")
        self.assertEqual(ordered_blocks[4].text, "C3-A")
        self.assertEqual(ordered_blocks[5].text, "C3-B")

    def test_header_stripping(self):
        header_text = "My Document Header - Page"
        blocks_data = [
            # Page 1
            {"text": header_text + " 1", "bbox": (50, 750, 550, 770), "page_num": 1}, # In header margin
            {"text": "Main content page 1", "bbox": (50, 400, 550, 420), "page_num": 1},
            # Page 2
            {"text": header_text + " 2", "bbox": (50, 750, 550, 770), "page_num": 2}, # In header margin
            {"text": "Another content page 2", "bbox": (50, 400, 550, 420), "page_num": 2},
            # Page 3 - different header, should be kept
            {"text": "Unique Header Longer Than Min Length", "bbox": (50, 750, 550, 770), "page_num": 3},
            {"text": "Content for Page 3", "bbox": (50, 400, 550, 420), "page_num": 3},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        filtered_blocks = self.extractor._filter_headers_and_footers(mock_blocks, self.mock_page_dimensions)
        
        self.assertEqual(len(filtered_blocks), 4) # Should remove 2 headers with recurring text
        self.assertNotIn(header_text + " 1", [b.text for b in filtered_blocks])
        self.assertNotIn(header_text + " 2", [b.text for b in filtered_blocks])
        self.assertIn("Main content page 1", [b.text for b in filtered_blocks])
        self.assertIn("Unique Header Longer Than Min Length", [b.text for b in filtered_blocks]) # Should be kept as not recurring

    def test_footer_stripping(self):
        footer_text = "Confidential - Page"
        blocks_data = [
            # Page 1
            {"text": "Main content page 1", "bbox": (50, 400, 550, 420), "page_num": 1},
            {"text": footer_text + " 1", "bbox": (50, 20, 550, 40), "page_num": 1}, # In footer margin
            # Page 2
            {"text": "Another content page 2", "bbox": (50, 400, 550, 420), "page_num": 2},
            {"text": footer_text + " 2", "bbox": (50, 20, 550, 40), "page_num": 2}, # In footer margin
            # Page 3 - different footer, should be kept
            {"text": "Content for Page 3", "bbox": (50, 400, 550, 420), "page_num": 3},
            {"text": "Single Page Footer Longer Than Min Length", "bbox": (50, 20, 550, 40), "page_num": 3},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        filtered_blocks = self.extractor._filter_headers_and_footers(mock_blocks, self.mock_page_dimensions)
        
        self.assertEqual(len(filtered_blocks), 4) # Should remove 2 footers with recurring text
        self.assertNotIn(footer_text + " 1", [b.text for b in filtered_blocks])
        self.assertNotIn(footer_text + " 2", [b.text for b in filtered_blocks])
        self.assertIn("Main content page 1", [b.text for b in filtered_blocks])
        self.assertIn("Single Page Footer Longer Than Min Length", [b.text for b in filtered_blocks]) # Should be kept

    def test_merge_blocks_into_paragraphs(self):
        blocks_data = [
            {"text": "Line 1 of paragraph 1.", "bbox": (50, 400, 250, 415), "page_num": 1, "font_size": 12},
            {"text": "Line 2 of paragraph 1.", "bbox": (50, 380, 250, 395), "page_num": 1, "font_size": 12}, # Small vertical gap
            {"text": "Paragraph 2, line 1.", "bbox": (50, 300, 250, 315), "page_num": 1, "font_size": 12}, # Large vertical gap
            {"text": "Line 2 of paragraph 2.", "bbox": (52, 280, 252, 295), "page_num": 1, "font_size": 12}, # Small vertical gap, slight x0 diff
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        paragraphs = self.extractor._merge_blocks_into_paragraphs(mock_blocks)
        
        self.assertEqual(len(paragraphs), 2)
        self.assertEqual(paragraphs[0], "Line 1 of paragraph 1. Line 2 of paragraph 1.")
        self.assertEqual(paragraphs[1], "Paragraph 2, line 1. Line 2 of paragraph 2.")

    def test_parse_with_pre_extracted_blocks(self):
        # Simulate a 2-column document with headers and footers
        header_text = "Document Title for All Pages"
        footer_text = "Page X of Y" # Example page number pattern
        blocks_data = [
            # Page 1
            {"text": header_text, "bbox": (50, 750, 550, 770), "page_num": 1, "font_size": 10},
            {"text": "Left Column 1A. This is a sentence.", "bbox": (50, 400, 250, 420), "page_num": 1, "font_size": 12},
            {"text": "Next sentence in Left Column 1A.", "bbox": (50, 380, 250, 395), "page_num": 1, "font_size": 12},
            {"text": "Right Column 1A content.", "bbox": (300, 400, 500, 420), "page_num": 1, "font_size": 12},
            {"text": "More text on Right Column 1A.", "bbox": (300, 380, 500, 395), "page_num": 1, "font_size": 12},
            {"text": footer_text.replace("X", "1"), "bbox": (250, 20, 350, 40), "page_num": 1, "font_size": 8},
            # Page 2
            {"text": header_text, "bbox": (50, 750, 550, 770), "page_num": 2, "font_size": 10},
            {"text": "Left Column 2A. Another sentence.", "bbox": (50, 400, 250, 420), "page_num": 2, "font_size": 12},
            {"text": "Next sentence in Left Column 2A.", "bbox": (50, 380, 250, 395), "page_num": 2, "font_size": 12},
            {"text": "Right Column 2A content.", "bbox": (300, 400, 500, 420), "page_num": 2, "font_size": 12},
            {"text": "More text on Right Column 2A.", "bbox": (300, 380, 500, 395), "page_num": 2, "font_size": 12},
            {"text": footer_text.replace("X", "2"), "bbox": (250, 20, 350, 40), "page_num": 2, "font_size": 8},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        doc = self.extractor.parse(
            content_or_path=None, # Indicate that blocks are pre-extracted
            source_name="test_doc.pdf",
            extracted_blocks=mock_blocks,
            pre_extracted_page_dimensions=self.mock_page_dimensions,
        )

        expected_content = (
            "Left Column 1A. This is a sentence. Next sentence in Left Column 1A.\n\n"
            "Right Column 1A content. More text on Right Column 1A.\n\n"
            "Left Column 2A. Another sentence. Next sentence in Left Column 2A.\n\n"
            "Right Column 2A content. More text on Right Column 2A."
        )
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.content.strip(), expected_content.strip())
        self.assertEqual(doc.metadata.source, "test_doc.pdf")

    @patch("src.doc_intelligence.ingestion.pdf_extractor.PDFPage.get_pages")
    @patch("src.doc_intelligence.ingestion.pdf_extractor.PDFPageAggregator")
    @patch("builtins.open", new_callable=MagicMock)
    def test_parse_from_file_path(self, mock_open, MockPDFPageAggregator, mock_get_pages):
        # Mock PDFMiner.six components
        mock_layout_element = MagicMock(spec=LTTextBoxHorizontal)
        mock_layout_element.get_text.return_value = "Sample Content from file path. This is a second sentence."
        mock_layout_element.bbox = (100, 100, 500, 150) # Make it look like two lines close together
        mock_char = MagicMock(spec=LTChar, size=12)
        mock_text_line = MagicMock(spec=LTTextLineHorizontal)
        mock_text_line.__iter__.return_value = [mock_char] # Simulate characters for font size
        mock_layout_element.__iter__.return_value = [mock_text_line] # Simulate text lines for font size

        mock_layout = MagicMock()
        mock_layout.width = 600
        mock_layout.height = 800
        mock_layout.__iter__.return_value = [mock_layout_element]

        mock_page = MagicMock()
        mock_page.mediabox = (0, 0, 600, 800)
        mock_get_pages.return_value = [mock_page] # Single page

        mock_device = MockPDFPageAggregator.return_value
        mock_device.get_result.return_value = mock_layout

        # Create a dummy file
        dummy_pdf_path = Path("dummy.pdf")
        dummy_pdf_path.touch()

        try:
            doc = self.extractor.parse(dummy_pdf_path, source_name="dummy.pdf")
            self.assertIsInstance(doc, Document)
            # Content should be merged into one paragraph if line spacing is small
            self.assertEqual(doc.content, "Sample Content from file path. This is a second sentence.")
            self.assertEqual(doc.metadata.source, "dummy.pdf")
        finally:
            dummy_pdf_path.unlink()

    @patch("src.doc_intelligence.ingestion.pdf_extractor.PDFPage.get_pages")
    @patch("src.doc_intelligence.ingestion.pdf_extractor.PDFPageAggregator")
    def test_parse_from_bytesio(self, MockPDFPageAggregator, mock_get_pages):
        # Mock PDFMiner.six components
        mock_layout_element = MagicMock(spec=LTTextBoxHorizontal)
        mock_layout_element.get_text.return_value = "BytesIO Content. Another line of text."
        mock_layout_element.bbox = (100, 100, 500, 150) # Simulate a block covering two lines
        mock_char = MagicMock(spec=LTChar, size=10)
        mock_text_line = MagicMock(spec=LTTextLineHorizontal)
        mock_text_line.__iter__.return_value = [mock_char]
        mock_layout_element.__iter__.return_value = [mock_text_line]

        mock_layout = MagicMock()
        mock_layout.width = 600
        mock_layout.height = 800
        mock_layout.__iter__.return_value = [mock_layout_element]

        mock_page = MagicMock()
        mock_page.mediabox = (0, 0, 600, 800)
        mock_get_pages.return_value = [mock_page]

        mock_device = MockPDFPageAggregator.return_value
        mock_device.get_result.return_value = mock_layout

        dummy_bytes = io.BytesIO(b"dummy pdf content")
        doc = self.extractor.parse(dummy_bytes, source_name="dummy_bytes.pdf")

        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.content, "BytesIO Content. Another line of text.")
        self.assertEqual(doc.metadata.source, "dummy_bytes.pdf")

    def test_filter_short_noise_blocks(self):
        blocks_data = [
            {"text": "A", "bbox": (50, 400, 60, 410), "page_num": 1},  # Too short
            {"text": "123", "bbox": (70, 400, 100, 410), "page_num": 1}, # Short, but contains number (keep)
            {"text": "Normal text block content", "bbox": (50, 300, 250, 320), "page_num": 1},
        ]
        mock_blocks = self.create_mock_blocks(blocks_data)
        
        filtered_blocks = self.extractor._filter_headers_and_footers(mock_blocks, self.mock_page_dimensions)
        
        self.assertEqual(len(filtered_blocks), 2)
        self.assertNotIn("A", [b.text for b in filtered_blocks])
        self.assertIn("123", [b.text for b in filtered_blocks])
        self.assertIn("Normal text block content", [b.text for b in filtered_blocks])
