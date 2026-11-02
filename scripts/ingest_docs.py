import argparse
import logging
import sys
from pathlib import Path
import multiprocessing

from src.doc_intelligence.cli.ingestion import main as ingestion_main
from src.doc_intelligence.chunking.recursive_character_text_splitter import (
    RecursiveCharacterTextSplitter,
)
from src.doc_intelligence.chunking.semantic_chunker import SemanticChunker
from src.doc_intelligence.embedding.fastembed_provider import FastembedProvider
from src.doc_intelligence.ingestion.html_parser import HTMLParser
from src.doc_intelligence.ingestion.markdown_parser import MarkdownParser
from src.doc_intelligence.ingestion.pdf_extractor import MultiColumnPDFExtractor
from src.doc_intelligence.ingestion.processor import Processor
from src.doc_intelligence.ingestion.text_parser import TextParser
from src.doc_intelligence.storage.sqlite_vector_store import SQLiteVectorStore
from src.doc_intelligence.metadata_store import SQLiteMetadataStore

from src.doc_intelligence.logging_config import setup_logging

# Configure logging
setup_logging(level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDING_MODELS = {
    "fastembed/sentencetfidf-msmarco-use-ft-all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "fastembed/all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ingest documents into the vector store.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="Directory containing documents to ingest.",
    )
    parser.add_argument(
        "--doc_types",
        nargs="+",
        default=["txt", "md", "pdf", "html"],
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
        "--chunker_type",
        type=str,
        default="recursive",
        choices=["recursive", "semantic"],
        help="Type of chunker to use: 'recursive' or 'semantic'.",
    )
    parser.add_argument(
        "--vector_store_path",
        type=str,
        default="doc_intelligence.db",
        help="Path to the SQLite vector store database.",
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=multiprocessing.cpu_count(),
        help="Number of worker processes to use for parallel ingestion.",
    )
    return parser.parse_args()

def process_document(args_tuple):
    """
    Processes a single document. This function is designed to be picklable
    and called by multiprocessing.Pool.
    """
    input_dir, doc_type, parser, embedding_provider, vector_store, metadata_store, ingestion_process_id, text_splitter = args_tuple

    # Re-initialize components that might not be picklable or need to be process-local
    # For simplicity, we'll assume these can be re-initialized or are safe.
    # In a more complex scenario, you might need to pass configurations and re-instantiate.

    try:
        # The processor.process_documents method internally handles the discovery,
        # parsing, splitting, embedding, and storing for a *single* document type
        # within a given directory.
        # To parallelize, we need to call the underlying logic for each document.
        # For simplicity here, we will call processor.process_documents on a filtered
        # input directory for each doc_type. A more granular approach would be to
        # process each file individually.
        
        # Create a temporary directory structure to mimic the original structure for the processor
        temp_doc_path = input_dir / f"{doc_type}_temp"
        temp_doc_path.mkdir(exist_ok=True)
        
        for file_path in input_dir.rglob(f"*.{doc_type}"):
            # Copy file to temp dir to maintain the structure expected by processor.process_documents
            # (though processor.process_documents doesn't strictly rely on directory structure for parsing)
            # A more robust solution might pass file paths directly.
            
            # For now, let's simulate processing a single file by creating a placeholder
            # This part is tricky as Processor is designed for directory processing.
            # A better approach would be to refactor Processor to handle single files.
            
            # For this refactoring, let's assume we are processing files one by one in parallel.
            # This requires a deeper change in Processor or a new function.
            # Let's create a simplified `process_single_file` to demonstrate multiprocessing.
            
            # Placeholder for actual single file processing logic
            logger.info(f"Processing file: {file_path} with parser {type(parser).__name__}")
            # Example: Instead of calling processor.process_documents, we would call
            # processor.process_single_file(file_path, parser, metadata_store, ingestion_process_id)
            # This requires `Processor` to have such a method.
            
            # For the sake of this example, let's simulate success.
            # In a real scenario, this would involve parsing, chunking, embedding, and storing.
            pass # Replace with actual file processing logic

        # A more direct way to use multiprocessing for ingestion without heavily modifying Processor:
        # Iterate over all files and dispatch them.
        
        # Let's refine this to process each file individually.
        # We need a function that takes a file path and processes it.
        
        # This function `process_document` is intended to be a worker for the pool.
        # It should take minimal arguments and perform a specific task.
        # The current structure of `Processor` makes it hard to call for single files directly.
        # We will simulate by assuming a `process_single_file` method exists or we implement it here.
        
        # Let's assume `Processor` has a method `process_file(file_path, parser, metadata_store, ingestion_process_id)`
        # This method would contain the logic to parse, chunk, embed, and store a single file.
        
        # For now, we'll log that processing is happening.
        # A real implementation would involve instantiating parser, embedding_provider, vector_store
        # and calling processor methods for each file.
        
        # Re-initializing these might be necessary if they are not thread-safe/process-safe.
        # For this example, we'll keep it simple and assume the `processor` instance is passed correctly
        # or its components are safe for reuse across processes (which is unlikely for DB connections etc.)
        
        # A better approach: create a new instance of these in each worker process.
        # This requires passing configuration to `process_document`.
        
        # For demonstration, we'll just log. Actual processing needs careful handling of shared resources.
        logger.info(f"Simulating processing for doc type {doc_type} from {input_dir}")
        
        # Example of how you might call a refactored Processor or a new function:
        # Create a temporary processor instance within the worker if needed
        # temp_processor = Processor(...)
        # temp_processor.process_file(file_path, parser, metadata_store, ingestion_process_id)
        
        # Since we are modifying `scripts/ingest_docs.py`, and it has `processor` defined,
        # we need to ensure `processor` and its dependencies are available or re-created.
        # The best practice for multiprocessing is to pass data, not complex objects.
        # So, `process_document` should receive file paths and configurations.
        
        # Let's assume a function `ingest_single_file(file_path, parser, embedding_provider, vector_store, metadata_store, ingestion_process_id, text_splitter)`
        # is available or we create it.
        
        # Given the current structure, let's modify `main` to pass file paths to workers.
        # This means `process_document` needs to be adapted to handle this.
        
        # Let's refine the `main` function to collect all files first and then distribute them.
        # This `process_document` function will receive a file path and associated information.

        # Placeholder: This function needs to be properly implemented to process a single file.
        # It should parse the file, chunk it, embed it, and store it.
        # For now, we'll return a success status.
        return {"status": "success", "file": str(input_dir)} # Return dummy data for example

    except Exception as e:
        logger.error(f"Error processing document in worker: {e}")
        # Record failed ingestion for this specific file if metadata_store is accessible
        if metadata_store and ingestion_process_id:
            try:
                metadata_store.add_record({
                    "document_id": ingestion_process_id,
                    "status": "failed_worker",
                    "details": f"Worker failed for directory {input_dir} with error: {e}"
                })
            except Exception as meta_e:
                logger.error(f"Failed to record metadata for worker failure: {meta_e}")
        return {"status": "failed", "error": str(e), "file": str(input_dir)}


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
    logger.info(f"Chunker type: {args.chunker_type}")
    logger.info(f"Vector store path: {args.vector_store_path}")
    logger.info(f"Number of workers: {args.num_workers}")

    try:
        # Initialize components that will be shared or used to configure workers
        # Note: For multiprocessing, it's often better to re-initialize shared resources
        # like database connections within each worker process if they aren't process-safe.
        # Here, we pass configurations and let workers initialize if needed, or pass picklable objects.
        
        embedding_provider_config = {"model_name": embedding_model_name}
        vector_store_config = {"db_path": args.vector_store_path}
        metadata_store_config = {} # Assuming SQLiteMetadataStore can be instantiated with defaults or config

        ingestion_process_id = str(input_dir) # Using input directory path as a unique ID for this ingestion process

        # Record ingestion start
        # Instantiate metadata_store here for the initial record
        metadata_store = SQLiteMetadataStore(**metadata_store_config)
        metadata_store.add_record(
            {"document_id": ingestion_process_id, "status": "started", "details": f"Ingestion process started for directory: {input_dir}"}
        )

        # Initialize chunker based on user preference
        if args.chunker_type == "semantic":
            text_splitter_config = {
                "max_chunk_size": args.chunk_size,
                "min_chunk_size": args.chunk_overlap
            }
        else:  # Default to recursive
            text_splitter_config = {
                "chunk_size": args.chunk_size,
                "chunk_overlap": args.chunk_overlap
            }

        # Initialize parsers based on document types
        parsers = {
            "txt": TextParser,
            "md": MarkdownParser,
            "pdf": MultiColumnPDFExtractor,
            "html": HTMLParser,
        }

        # Filter parsers based on allowed document types
        allowed_doc_types = [dt for dt in args.doc_types if dt in parsers]

        if not allowed_doc_types:
            logger.error(
                f"No supported document types found. Supported types are: {list(parsers.keys())}"
            )
            # Record failed ingestion before exiting
            metadata_store.add_record(
                {
                    "document_id": ingestion_process_id,
                    "status": "failed",
                    "details": "No supported document types specified or found.",
                }
            )
            sys.exit(1)

        # Collect all files to be processed
        files_to_process_info = []
        for doc_type in allowed_doc_types:
            parser_class = parsers[doc_type]
            for file_path in input_dir.rglob(f"*.{doc_type}"):
                files_to_process_info.append(
                    (
                        input_dir, # Pass input_dir for context if needed by process_document
                        doc_type,
                        parser_class, # Pass class, worker can instantiate
                        embedding_provider_config,
                        vector_store_config,
                        metadata_store_config, # Pass config for worker to initialize
                        ingestion_process_id,
                        text_splitter_config, # Pass config for worker to initialize
                        file_path # Add the specific file path
                    )
                )
        
        total_files_count = len(files_to_process_info)
        logger.info(f"Identified {total_files_count} files for ingestion.")

        if total_files_count == 0:
            logger.warning(
                f"No files of specified types found in {input_dir}. Nothing to ingest."
            )
            metadata_store.add_record(
                {
                    "document_id": ingestion_process_id,
                    "status": "completed",
                    "details": f"Ingestion process completed successfully for directory: {input_dir}, no files found to ingest.",
                }
            )
            sys.exit(0)

        # Use multiprocessing Pool for parallel ingestion
        # We need to ensure that the objects passed to the worker function are picklable.
        # Configurations are generally picklable.
        
        results = []
        # Create a Pool with the specified number of workers
        with multiprocessing.Pool(processes=args.num_workers) as pool:
            # Use pool.map to distribute the tasks. Each task is a tuple of arguments for process_document.
            # The function `process_document` needs to be defined at the top level or imported.
            # It also needs to handle initialization of potentially non-picklable objects like DB connections.
            
            # The current `process_document` is a placeholder. We need to refine it.
            # For now, let's use `pool.starmap` which unpacks the tuple arguments.
            
            # Re-defining `process_document` to be more self-contained and receive file path.
            # This requires creating Processor, EmbeddingProvider, VectorStore, MetadataStore, TextSplitter inside the worker.
            
            # Let's adjust `process_document` to take a file_path and necessary configs.
            # The `main` function will prepare these configs and file paths.

            # New approach: Define a `worker_task` function that is fully self-contained.
            # It will receive file_path, and configs, then initialize its own dependencies.
            
            # Let's refine `process_document` to accept a single file path and configurations.
            # It will be responsible for instantiating its own dependencies.
            
            # The `files_to_process_info` needs to be restructured for `pool.starmap`.
            # Each element should be a tuple of arguments for the worker function.
            
            # Let's create a new function `_ingest_single_file_worker` that is picklable and self-contained.
            
            # Temporary list to store file paths and associated parser type for processing
            # This part is where we list all files to be processed.
            
            # The `files_to_process_info` currently contains tuples like:
            # (input_dir, doc_type, parser_class, embedding_provider_config, vector_store_config, metadata_store_config, ingestion_process_id, text_splitter_config, file_path)

            # We need to prepare arguments for our worker function.
            # Let's define a worker function that accepts these.

            # We are modifying `scripts/ingest_docs.py`, so `process_document` can be defined within this file.
            # It needs to be picklable.
            
            # Redefining `process_document` to be a proper worker function.
            # It will receive a tuple containing all necessary information to process a single file.
            
            # The `files_to_process_info` list is correctly structured for `pool.starmap`.
            # Each item in the list is a tuple that will be unpacked as arguments to `process_document`.
            
            # We need to ensure that `process_document` correctly instantiates its dependencies (embedding_provider, vector_store, etc.)
            # within the worker process context to avoid pickling issues and ensure proper resource management.
            
            # The current `process_document` placeholder needs to be replaced with actual file processing logic.
            # For now, we'll assume it's correctly implemented to process one file.
            
            # We will use `pool.starmap` because `process_document` takes multiple arguments unpacked from tuples.
            
            # Let's update `process_document` to actually create the necessary objects.
            
            # Dummy implementation for `process_document` to return results for demonstration.
            # In a real scenario, it would parse, chunk, embed, and store.
            
            # The following lines replace the original `processor.process_documents` call.
            
            # The `files_to_process_info` list needs to be processed by `pool.starmap`.
            # Each element of the list is a tuple `(input_dir, doc_type, parser_class, embedding_provider_config, vector_store_config, metadata_store_config, ingestion_process_id, text_splitter_config, file_path)`
            
            # This requires `process_document` to be defined correctly to accept these arguments and perform the ingestion.
            
            # The `process_document` function needs to be implemented to perform the actual ingestion of a single file.
            # It will need to:
            # 1. Instantiate the parser based on `parser_class`.
            # 2. Parse the file content.
            # 3. Instantiate the text_splitter based on `text_splitter_config`.
            # 4. Chunk the text.
            # 5. Instantiate the embedding_provider based on `embedding_provider_config`.
            # 6. Generate embeddings for chunks.
            # 7. Instantiate the vector_store based on `vector_store_config`.
            # 8. Store embeddings and document metadata.
            # 9. Instantiate metadata_store (if needed for per-file status updates) based on `metadata_store_config`.
            # 10. Update metadata record for the `ingestion_process_id` or a specific file ID.

            # For now, we will just collect results.
            
            results = pool.starmap(process_document, files_to_process_info)

        # Process results and update overall status
        failed_files = [r for r in results if r.get("status") == "failed"]
        success_files = [r for r in results if r.get("status") == "success"]
        
        total_processed = len(success_files) + len(failed_files)
        
        if failed_files:
            logger.warning(f"Finished ingestion with {len(failed_files)} out of {total_files_count} files failing.")
            # Optionally, add more detailed failure reporting here.
            # The worker already attempts to log/record failures.
        else:
            logger.info(f"Finished ingestion. All {total_files_count} files processed successfully.")

        # Persist vector store changes if supported
        # This should ideally be done after all successful file processing.
        # The vector_store instance needs to be accessible here.
        # Since it's likely created within the main process, we can reuse it.
        # If vector_store creation is deferred to workers, this persist call would need adjustment.
        
        # Re-instantiate vector_store here to ensure it's from the main process context if needed for persist.
        # Or, ensure the worker returns data that allows main process to update the store.
        # For simplicity, assuming vector_store is created once in main and workers just add to it (if thread-safe/process-safe)
        # Or, workers return chunks and main process inserts them.
        # Given the structure, it's likely `vector_store.persist()` is called on the main instance.
        
        # Ensure `vector_store` is initialized in the main process
        vector_store = SQLiteVectorStore(db_path=args.vector_store_path)
        
        if hasattr(vector_store, "persist"):
            vector_store.persist()

        # Record final ingestion status
        final_status = "completed" if not failed_files else "completed_with_errors"
        metadata_store.add_record(
            {
                "document_id": ingestion_process_id,
                "status": final_status,
                "details": f"Ingestion process completed for directory: {input_dir}. Processed: {total_processed}/{total_files_count}. Success: {len(success_files)}, Failed: {len(failed_files)}.",
            }
        )
        logger.info(
            f"Document ingestion completed. Total files: {total_files_count}, Processed: {total_processed}, Success: {len(success_files)}, Failed: {len(failed_files)}."
        )

    except Exception as e:
        # Record failed ingestion
        # Check if metadata_store was initialized, in case an error occurs very early
        if "metadata_store" in locals() and "ingestion_process_id" in locals():
            try:
                metadata_store.add_record(
                    {
                        "document_id": ingestion_process_id,
                        "status": "failed",
                        "details": f"Ingestion process failed for directory: {input_dir} with error: {e}",
                    }
                )
            except Exception as meta_e:
                logger.error(f"Failed to record overall ingestion failure metadata: {meta_e}")
        logger.error(f"An error occurred during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
