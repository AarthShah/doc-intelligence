import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from collections import Counter

from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTChar, LTTextLineHorizontal, LTTextBoxHorizontal
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

from src.doc_intelligence.models import Document, DocumentMetadata


@dataclass
class TextBlock:
    """Represents a block of text extracted from a PDF page."""
    text: str
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    page_num: int
    font_size: Optional[float] = None


class MultiColumnPDFExtractor:
    """
    Parses PDF content, reconstructs reading order in multi-column layouts,
    and strips recurring/margin-based headers and footers.
    """

    def __init__(
        self,
        header_margin_ratio: float = 0.1,  # Ratio of page height for header region
        footer_margin_ratio: float = 0.1,  # Ratio of page height for footer region
        column_tolerance: float = 0.03,  # Max horizontal gap (as % of page width) for blocks in same column
        line_spacing_tolerance: float = 0.5,  # Max vertical gap (as % of avg line height) for lines in same paragraph
        min_header_footer_text_len: int = 20, # Minimum text length to consider for header/footer pattern detection
        min_pages_for_hf_detection: int = 2, # Minimum pages a pattern must appear on to be considered a header/footer
    ):
        self.header_margin_ratio = header_margin_ratio
        self.footer_margin_ratio = footer_margin_ratio
        self.column_tolerance = column_tolerance
        self.line_spacing_tolerance = line_spacing_tolerance
        self.min_header_footer_text_len = min_header_footer_text_len
        self.min_pages_for_hf_detection = min_pages_for_hf_detection


    def _extract_blocks_from_pdfminer(self, file_object: Union[Path, io.BytesIO]) -> Tuple[List[TextBlock], Dict[int, Tuple[float, float]]]:
        """
        Extracts text blocks and their bounding boxes from a PDF using pdfminer.six.
        Returns a list of TextBlock objects and a dictionary of page dimensions.
        """
        blocks: List[TextBlock] = []
        page_dimensions: Dict[int, Tuple[float, float]] = {}

        if isinstance(file_object, Path):
            fp = open(file_object, "rb")
        else:
            fp = file_object

        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        try:
            for i, page in enumerate(PDFPage.get_pages(fp)):
                page_num = i + 1
                interpreter.process_page(page)
                layout = device.get_result()

                page_dimensions[page_num] = (layout.width, layout.height)

                for element in layout:
                    if isinstance(element, LTTextBoxHorizontal):
                        text_content = element.get_text().strip()
                        if not text_content:
                            continue

                        x0, y0, x1, y1 = element.bbox

                        # Estimate font size: take the average size of characters in the block
                        font_sizes = []
                        for text_line in element:
                            if isinstance(text_line, LTTextLineHorizontal):
                                for char in text_line:
                                    if isinstance(char, LTChar):
                                        font_sizes.append(char.size)
                        
                        font_size: Optional[float] = None
                        if font_sizes:
                            font_size = sum(font_sizes) / len(font_sizes)

                        blocks.append(
                            TextBlock(
                                text=text_content,
                                bbox=(x0, y0, x1, y1),
                                page_num=page_num,
                                font_size=font_size,
                            )
                        )
        finally:
            if isinstance(file_object, Path):
                fp.close()
            device.close() # Ensure device is closed

        return blocks, page_dimensions

    def _group_blocks_into_columns_and_reorder(self, page_blocks: List[TextBlock], page_width: float) -> List[TextBlock]:
        """
        Groups text blocks into columns and reorders them by reading order
        (left-to-right columns, then top-to-bottom within each column).
        """
        if not page_blocks:
            return []

        # Sort blocks by their horizontal position (x0) to facilitate column detection
        # then by vertical position (y0) to maintain reading order within groups
        page_blocks.sort(key=lambda block: (block.bbox[0], -block.bbox[1]))

        # Cluster x0 coordinates to identify column boundaries
        x0_coords = sorted(list(set([block.bbox[0] for block in page_blocks])))
        
        column_boundaries: List[Tuple[float, float]] = [] # stores (min_x, max_x) for each column
        if x0_coords:
            current_col_min_x = x0_coords[0]
            for i in range(1, len(x0_coords)):
                # If the gap between successive x-starts is significant, it's a new column
                if x0_coords[i] - x0_coords[i-1] > page_width * self.column_tolerance:
                    column_boundaries.append((current_col_min_x, x0_coords[i-1]))
                    current_col_min_x = x0_coords[i]
            column_boundaries.append((current_col_min_x, x0_coords[-1]))

        # Fallback if no distinct columns found or all blocks are very close, treat as single column
        if not column_boundaries and page_blocks:
             column_boundaries = [(min(b.bbox[0] for b in page_blocks), max(b.bbox[2] for b in page_blocks))]
        elif not column_boundaries: # No blocks on page
            return []


        # Assign blocks to columns
        column_groups: Dict[int, List[TextBlock]] = {}
        for block in page_blocks:
            assigned_to_column = False
            # Find the column whose x-range most significantly contains the block's x-range
            block_center_x = (block.bbox[0] + block.bbox[2]) / 2
            
            best_col_idx = -1
            min_dist_to_col_center = float('inf')

            for idx, (col_min_x, col_max_x) in enumerate(column_boundaries):
                col_center_x = (col_min_x + col_max_x) / 2
                dist = abs(block_center_x - col_center_x)
                
                # Check for direct overlap as well
                if (max(col_min_x, block.bbox[0]) < min(col_max_x, block.bbox[2])) or (dist < min_dist_to_col_center):
                    if dist < min_dist_to_col_center:
                        min_dist_to_col_center = dist
                        best_col_idx = idx
            
            if best_col_idx != -1:
                if best_col_idx not in column_groups:
                    column_groups[best_col_idx] = []
                column_groups[best_col_idx].append(block)
                assigned_to_column = True
            
            # If still not assigned, perhaps it's an outlier. Assign to closest one.
            if not assigned_to_column and column_boundaries:
                 best_col_idx = 0
                 min_dist_to_col_center = float('inf')
                 for idx, (col_min_x, col_max_x) in enumerate(column_boundaries):
                     col_center_x = (col_min_x + col_max_x) / 2
                     dist = abs(block_center_x - col_center_x)
                     if dist < min_dist_to_col_center:
                         min_dist_to_col_center = dist
                         best_col_idx = idx
                 if best_col_idx not in column_groups:
                    column_groups[best_col_idx] = []
                 column_groups[best_col_idx].append(block)


        # Reconstruct reading order: process columns from left to right, then blocks within columns from top to bottom
        ordered_blocks_in_page: List[TextBlock] = []
        
        # Sort column_groups by the x-coordinate of their representative boundary (min_x)
        sorted_column_indices = sorted(column_groups.keys(), key=lambda idx: column_boundaries[idx][0])
        
        for col_idx in sorted_column_indices:
            # Sort blocks within each column by y-coordinate (top to bottom)
            sorted_column_blocks = sorted(column_groups[col_idx], key=lambda block: -block.bbox[1])
            ordered_blocks_in_page.extend(sorted_column_blocks)

        return ordered_blocks_in_page

    def _filter_headers_and_footers(
        self, all_blocks: List[TextBlock], page_dimensions: Dict[int, Tuple[float, float]]
    ) -> List[TextBlock]:
        """
        Identifies and filters out recurring text blocks in header and footer regions
        based on configurable margin ratios and frequency across pages.
        """
        if not all_blocks:
            return []

        # Group blocks by page number for individual page analysis
        blocks_by_page: Dict[int, List[TextBlock]] = {}
        for block in all_blocks:
            if block.page_num not in blocks_by_page:
                blocks_by_page[block.page_num] = []
            blocks_by_page[block.page_num].append(block)

        # Collect potential header/footer candidates based on their position on each page
        potential_headers: List[TextBlock] = []
        potential_footers: List[TextBlock] = []

        for page_num, blocks_on_page in blocks_by_page.items():
            page_width, page_height = page_dimensions.get(page_num, (0, 0))
            if page_height == 0:  # Cannot apply margin logic if page dimensions are unknown
                continue

            for block in blocks_on_page:
                y0, y1 = block.bbox[1], block.bbox[3]

                # Check if block is in header region
                if y1 > page_height * (1 - self.header_margin_ratio):
                    if len(block.text) > self.min_header_footer_text_len:
                        potential_headers.append(block)
                # Check if block is in footer region
                elif y0 < page_height * self.footer_margin_ratio:
                    if len(block.text) > self.min_header_footer_text_len:
                        potential_footers.append(block)
        
        # Determine actual recurring headers/footers based on frequency across distinct pages
        header_page_counts: Dict[str, Set[int]] = {}
        for block in potential_headers:
            norm = re.sub(r'\d+', '#', block.text.strip())
            header_page_counts.setdefault(norm, set()).add(block.page_num)

        footer_page_counts: Dict[str, Set[int]] = {}
        for block in potential_footers:
            norm = re.sub(r'\d+', '#', block.text.strip())
            footer_page_counts.setdefault(norm, set()).add(block.page_num)

        # A block's text is considered a recurring header/footer if it appears on
        # a minimum number of distinct pages within its respective margin region.
        is_actual_header = {
            norm for norm, pages in header_page_counts.items()
            if len(pages) >= self.min_pages_for_hf_detection
        }
        is_actual_footer = {
            norm for norm, pages in footer_page_counts.items()
            if len(pages) >= self.min_pages_for_hf_detection
        }

        # Filter out identified headers and footers from the original list of all blocks
        final_blocks: List[TextBlock] = []
        for block in all_blocks:
            page_width, page_height = page_dimensions.get(block.page_num, (0, 0))
            
            # If page dimensions are missing or zero, we cannot reliably filter by margin, so keep the block.
            if page_height == 0:
                final_blocks.append(block)
                continue

            y0, y1 = block.bbox[1], block.bbox[3]
            in_header_region = y1 > page_height * (1 - self.header_margin_ratio)
            in_footer_region = y0 < page_height * self.footer_margin_ratio
            
            norm = re.sub(r'\d+', '#', block.text.strip())
            is_filtered = False
            if in_header_region and norm in is_actual_header:
                is_filtered = True
            elif in_footer_region and norm in is_actual_footer:
                is_filtered = True
            
            # Also filter out very short, non-content text blocks that are not clear headers/footers
            # e.g., single characters, punctuation that might be noise.
            # This is a general cleanup, not directly related to H/F, but good for content quality.
            # It should not remove page numbers explicitly, as they are part of common H/F detection.
            if not is_filtered and (len(block.text.strip()) < 3 and not re.search(r'\d+', block.text)):
                 is_filtered = True

            if not is_filtered:
                final_blocks.append(block)

        return final_blocks

    def _merge_blocks_into_paragraphs(self, blocks: List[TextBlock]) -> List[str]:
        """
        Merges text blocks that are vertically and horizontally close within a page
        into coherent paragraph strings, respecting line spacing.
        """
        if not blocks:
            return []

        merged_paragraphs = []
        current_paragraph_blocks: List[TextBlock] = []

        # The blocks are already ordered by column and then top-to-bottom within columns.
        # This function processes them in this reading order.

        for block in blocks:
            if not current_paragraph_blocks:
                current_paragraph_blocks.append(block)
                continue

            last_block = current_paragraph_blocks[-1]
            
            # Calculate vertical gap between the bottom of the last block and the top of the current block
            vertical_gap = last_block.bbox[1] - block.bbox[3]
            
            # Estimate average line height. If font_size is available, use it. Otherwise, estimate from block height.
            avg_line_height = last_block.font_size if last_block.font_size else (last_block.bbox[3] - last_block.bbox[1]) * 1.2
            if avg_line_height <= 0: # Prevent division by zero or negative
                avg_line_height = 10 # Default to a reasonable line height

            # Horizontal alignment check: check if the x0 coordinates are close
            # This helps ensure we don't merge across distinct columns inadvertently.
            x0_proximity = abs(last_block.bbox[0] - block.bbox[0])
            # Consider merging if vertical gap is small and horizontal alignment is good
            if (0 <= vertical_gap < avg_line_height * self.line_spacing_tolerance) and \
               (x0_proximity < (last_block.bbox[2] - last_block.bbox[0]) * self.line_spacing_tolerance):
                current_paragraph_blocks.append(block)
            else:
                merged_paragraphs.append(" ".join([b.text for b in current_paragraph_blocks]))
                current_paragraph_blocks = [block]

        if current_paragraph_blocks:
            merged_paragraphs.append(" ".join([b.text for b in current_paragraph_blocks]))

        # Further cleanup: remove any empty or very short paragraphs that might remain
        return [p for p in merged_paragraphs if len(p.strip()) > 5]


    def parse(
        self,
        content_or_path: Union[str, Path, io.BytesIO],
        source_name: str = "document.pdf",
        extracted_blocks: Optional[List[TextBlock]] = None, # For testing or pre-processing scenarios
        pre_extracted_page_dimensions: Optional[Dict[int, Tuple[float, float]]] = None, # For testing
    ) -> Document:
        """
        Extracts content from a PDF, handling multi-column layouts and filtering
        headers/footers. Returns a Document object.
        """
        
        file_object: Optional[Union[Path, io.BytesIO]] = None
        if isinstance(content_or_path, str):
            file_object = Path(content_or_path)
            if not file_object.is_file():
                raise FileNotFoundError(f"File not found at {content_or_path}")
        elif isinstance(content_or_path, Path):
            file_object = content_or_path
        elif isinstance(content_or_path, io.BytesIO):
            file_object = content_or_path
        elif extracted_blocks is None: # Only if neither file nor blocks are provided
            raise TypeError("content_or_path must be a file path (str or Path), a BytesIO object, or extracted_blocks must be provided.")

        raw_blocks: List[TextBlock]
        page_dimensions: Dict[int, Tuple[float, float]]

        if extracted_blocks is None:
            if file_object is None: # Should not happen due to previous check
                 raise ValueError("No file object or extracted blocks provided.")
            raw_blocks, page_dimensions = self._extract_blocks_from_pdfminer(file_object)
        else:
            raw_blocks = extracted_blocks
            page_dimensions = pre_extracted_page_dimensions if pre_extracted_page_dimensions is not None else {}
            # If page_dimensions are not explicitly provided with pre-extracted blocks,
            # try to infer them from block bounding boxes. This is a best-effort.
            if not page_dimensions:
                for block in raw_blocks:
                    if block.page_num not in page_dimensions:
                        # Initial guess: page dimensions are at least as large as the first block's dimensions
                        page_dimensions[block.page_num] = (block.bbox[2] - block.bbox[0], block.bbox[3] - block.bbox[1])
                    else: # Expand dimensions if block indicates larger bounds
                        current_width, current_height = page_dimensions[block.page_num]
                        new_width = max(current_width, block.bbox[2]) # max x-coordinate (assuming 0,0 is bottom-left)
                        new_height = max(current_height, block.bbox[3]) # max y-coordinate
                        page_dimensions[block.page_num] = (new_width, new_height)
                # Ensure some minimal dimensions if inference fails for some pages (e.g., empty page or tiny block)
                for pn in sorted(list(set(b.page_num for b in raw_blocks))):
                    if pn not in page_dimensions:
                        page_dimensions[pn] = (100, 100) # Default small page size if no blocks
                    else: # Ensure derived dimensions are sensible (e.g., not zero)
                        w, h = page_dimensions[pn]
                        page_dimensions[pn] = (max(w, 100), max(h, 100))


        # Filter out headers and footers
        content_blocks = self._filter_headers_and_footers(raw_blocks, page_dimensions)

        # Group blocks by page number and then process columns and merge paragraphs for each page
        blocks_by_page: Dict[int, List[TextBlock]] = {}
        for block in content_blocks:
            if block.page_num not in blocks_by_page:
                blocks_by_page[block.page_num] = []
            blocks_by_page[block.page_num].append(block)

        ordered_content_parts: List[str] = []
        for page_num in sorted(blocks_by_page.keys()):
            page_blocks = blocks_by_page[page_num]
            
            # Get page dimensions for column detection, default if not found
            page_width, _ = page_dimensions.get(page_num, (0, 0)) 
            if page_width <= 0 and page_blocks: # If page_width is still 0/invalid, derive from blocks
                min_x = min(b.bbox[0] for b in page_blocks)
                max_x = max(b.bbox[2] for b in page_blocks)
                page_width = max_x - min_x
                if page_width <= 0: page_width = 100 # Default if no blocks or zero width
            elif page_width <= 0: 
                page_width = 100 # Default if no blocks on page or no dimensions

            # Order blocks on the current page by columns and reading order
            ordered_page_blocks = self._group_blocks_into_columns_and_reorder(page_blocks, page_width)
            
            # Merge ordered blocks into paragraphs for the current page
            merged_text_blocks = self._merge_blocks_into_paragraphs(ordered_page_blocks)
            ordered_content_parts.extend(merged_text_blocks)

        full_content = "\n\n".join(ordered_content_parts).strip()

        metadata = DocumentMetadata(
            source_name=source_name,
            format="pdf",
            page_count=len(blocks_by_page) or 1,
        )
        return Document(text=full_content, metadata=metadata)
