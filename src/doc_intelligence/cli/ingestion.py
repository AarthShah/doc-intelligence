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

    # Placeholder for future ingestion logic
    print(f"Ingesting documents from: {args.input_dir}")
    print(f"Document type: {args.doc_type}")

    if not args.input_dir.is_dir():
        print(f"Error: Input directory '{args.input_dir}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
