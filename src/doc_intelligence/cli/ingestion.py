import argparse
import sys
from pathlib import Path


def main():
    """
    Main entry point for the document ingestion CLI.

    Parses command-line arguments and initiates the document ingestion process.
    """
    parser = argparse.ArgumentParser(
        description="Ingest documents from a specified directory into the document intelligence platform."
    )

    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Path to the directory containing documents to ingest.",
    )
    parser.add_argument(
        "--doc-type",
        type=str,
        default="pdf",  # A reasonable default for common document types
        help="Type of documents to ingest (e.g., 'pdf', 'docx', 'txt').",
    )

    args = parser.parse_args()

    if not args.input_dir.is_dir():
        print(f"Error: Input directory '{args.input_dir}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Ingesting documents from: {args.input_dir}")
    print(f"Document type: {args.doc_type}")

    doc_type = args.doc_type.lower()
    extension_map = {
        "pdf": (".pdf", process_pdf),
        "html": (".html", ".htm", process_html),
        "markdown": (".md", ".markdown", process_markdown),
        "txt": (".txt", process_txt),
    }

    # Normalize mapping lookup
    matched_files = []
    for path in args.input_dir.iterdir():
        if path.is_file():
            ext = path.suffix.lower()
            if doc_type == "pdf" and ext == ".pdf":
                matched_files.append((path, process_pdf))
            elif doc_type == "html" and ext in (".html", ".htm"):
                matched_files.append((path, process_html))
            elif doc_type in ("markdown", "md") and ext in (".md", ".markdown"):
                matched_files.append((path, process_markdown))
            elif doc_type == "txt" and ext == ".txt":
                matched_files.append((path, process_txt))

    for file_path, processor in matched_files:
        processor(file_path)


def process_pdf(file_path: Path):
    """Process a PDF document."""
    print(f"Processing PDF file: {file_path}")


def process_html(file_path: Path):
    """Process an HTML document."""
    print(f"Processing HTML file: {file_path}")


def process_markdown(file_path: Path):
    """Process a Markdown document."""
    print(f"Processing Markdown file: {file_path}")


def process_txt(file_path: Path):
    """Process a text document."""
    print(f"Processing text file: {file_path}")


if __name__ == "__main__":
    main()
