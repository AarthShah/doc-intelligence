import argparse
import logging
import sys
from pathlib import Path

from src.doc_intelligence.cli.ingestion import main as ingestion_main
import argparse
import logging
import sys
from pathlib import Path

from src.doc_intelligence.cli.ingestion import main as ingestion_main
from src.doc_intelligence.chunking.recursive_character_text_splitter import (
    RecursiveCharacterTextSplitter,
)
from src.doc_intelligence.embedding.fastembed_provider import FastembedProvider
from src.doc_intelligence.storage.sqlite_vector_store import SQLiteVectorStore
from src.doc_intelligence.ingestion.processor import Processor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

EMBEDDING_MODELS = {
    "fastembed/sentencetfidf-msmarco-use-ft-all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "fastembed/all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Ingest documents into the vector store.")
    parser.add_argument(
        "input_dir",
        type=str,
        help="Directory containing documents to ingest.",
    )
    parser.add_argument(
        "--doc_types",
        nargs="+",
        default=["txt", "md", "pdf"],
        help="Document types (extensions) to process.",
    )
    parser.add_argument(
        "--embedding_model",
        type=str,
        default="fastembed/all-MiniLM-L6-v2",
        choices=EMBEDDING_MODELS.keys(),
        help="Embedding model to use for generating document embeddings.",
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=1000,
        help="Maximum size of each text chunk.",
    )
    parser.add_argument(
        "--chunk_overlap",
        type=int,
        default=200,
        help="Overlap between consecutive text chunks.",
    )
    parser.add_argument(
        "--vector_store_path",
        type=str,
        default="doc_intelligence.db",
        help="Path to the SQLite vector store database.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)

    embedding_model_name = EMBEDDING_MODELS.get(args.embedding_model)
    if not embedding_model_name:
        logger.error(f"Invalid embedding model specified: {args.embedding_model}")
        sys.exit(1)

    logger.info(f"Starting document ingestion from: {input_dir}")
    logger.info(f"Document types to process: {args.doc_types}")
    logger.info(f"Embedding model: {args.embedding_model}")
    logger.info(f"Chunk size: {args.chunk_size}, Chunk overlap: {args.chunk_overlap}")
    logger.info(f"Vector store path: {args.vector_store_path}")

    try:
        # Initialize components
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap
        )
        embedding_provider = FastembedProvider(model_name=embedding_model_name)
        vector_store = SQLiteVectorStore(db_path=args.vector_store_path)
        processor = Processor(
            text_splitter=text_splitter,
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        )

        # Call the core ingestion logic
        # The processor.process_documents method is designed to handle the file discovery,
        # type determination, parsing, and then calls to the text_splitter, embedding_provider,
        # and vector_store.
        #
        # We pass the list of document types to be processed.
        # The processor will recursively find files in input_dir matching these types.
        processor.process_documents(input_dir=input_dir, doc_types=args.doc_types)

        logger.info("Document ingestion completed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
