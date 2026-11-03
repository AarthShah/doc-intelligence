import pytest
from click.testing import CliRunner

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

# Assuming ingest_docs.py will be located at src/cli/ingest_docs.py
# and will expose a 'cli' or similar entry point function.
# This import will fail until src/cli/ingest_docs.py is provided.
try:
    # Import the main function directly for testing purposes
    from scripts.ingest_docs import main as ingest_docs_main
    # Mock necessary components that might be hard to set up in a test environment
    from src.doc_intelligence.storage.sqlite_vector_store import SQLiteVectorStore
    from src.doc_intelligence.metadata_store import SQLiteMetadataStore
except ImportError as e:
    pytest.fail(f"Could not import necessary modules for ingest_docs tests: {e}")


# Mock the underlying multiprocessing Pool to control execution and avoid actual parallel processes
# This allows us to simulate the behavior of multiprocessing for testing purposes.
class MockPool:
    def __init__(self, processes=None):
        self.processes = processes
        self.tasks = []

    def starmap(self, func, iterable):
        # Execute tasks sequentially in the main process for predictable testing
        results = []
        for args in iterable:
            results.append(func(*args))
        return results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture
def mock_multiprocessing_pool():
    with patch("multiprocessing.Pool", new=MockPool) as mock_pool:
        yield mock_pool

def test_ingest_docs_command_basic_execution():
    """
    Test that the ingest_docs command can be invoked without errors and
    produces expected output for a basic scenario.
    """
    runner = CliRunner()
    # In a real test, you would pass arguments and check side effects
    # e.g., result = runner.invoke(cli, ["--input-dir", "dummy_docs", "--db-path", "test.db"])
    # For now, we just check if the command can be called (assuming a help or no-args output)
    result = runner.invoke(ingest_docs_main, ["--help"])

    assert result.exit_code == 0
    # The help output might change, so checking for key phrases is more robust
    assert "Usage: ingest_docs.py" in result.output
    assert "input_dir" in result.output
    assert "--doc_types" in result.output


def test_ingest_docs_parallel_processing(mock_multiprocessing_pool):
    """
    Test that the ingest_docs script correctly processes multiple documents in parallel.
    """
    # Create a temporary directory for input documents
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir)
        doc1_path = input_dir / "doc1.txt"
        doc2_path = input_dir / "doc2.txt"
        doc3_path = input_dir / "subdir/doc3.txt"

        # Create dummy documents
        doc1_path.write_text("This is the content of document 1.")
        doc2_path.write_text("This is the content of document 2.")
        doc3_path.parent.mkdir()
        doc3_path.write_text("This is the content of document 3 in a subdirectory.")

        # Mock the actual processing logic to simulate successful ingestion
        # We need to mock the `process_document` function within `scripts.ingest_docs`
        # and ensure it returns a result that `main` can interpret.
        # The `process_document` function is called by `pool.starmap`.
        
        # Mock the metadata store to check if records are added
        mock_metadata_store = MagicMock(spec=SQLiteMetadataStore)
        mock_metadata_store.add_record = MagicMock()

        # Mock the vector store and its persist method
        mock_vector_store = MagicMock(spec=SQLiteVectorStore)
        mock_vector_store.persist = MagicMock()

        # Define the arguments that would be passed to `ingest_docs_main`
        # We'll pass a list of dummy files instead of relying on filesystem scanning for simplicity
        # This requires modifying the `main` function to accept a file list or mocking its internal file discovery.
        # For this test, we'll assume `main` correctly finds the files.

        # Mock the `multiprocessing.Pool` and its `starmap` method to simulate parallel execution
        # and verify that `process_document` is called with the correct arguments.
        
        # We need to mock the internal `process_document` function.
        # The `ingest_docs_main` function calls `pool.starmap(process_document, files_to_process_info)`.
        # We will patch `process_document` within the `scripts.ingest_docs` module.
        
        # The `process_document` function is defined within `scripts/ingest_docs.py`.
        # Its signature is: `process_document(args_tuple)` which is then unpacked.
        # The `main` function prepares `files_to_process_info` which contains tuples of arguments.
        # The `starmap` call unpacks these tuples when calling `process_document`.
        # So, the arguments passed to `process_document` by `starmap` are:
        # (input_dir, doc_type, parser_class, embedding_provider_config, vector_store_config, metadata_store_config, ingestion_process_id, text_splitter_config, file_path)
        
        # Mocking `scripts.ingest_docs.process_document`
        mock_process_document_return_value = {
            "status": "success",
            "file": str(input_dir) # Mock return value structure
        }
        
        # Mocking the function `process_document` that `pool.starmap` calls.
        # We need to ensure this mock returns a value that `main` expects.
        # `main` expects a list of dictionaries, each with a "status" key.
        # The actual return value of `process_document` is processed by `main`.
        
        # We will mock the internal `process_document` directly.
        # `pool.starmap` calls the function provided as the first argument.
        # If we pass `MockPool`, `starmap` will call our `MockPool.starmap`.
        # Our `MockPool.starmap` will call the `func` argument (which is `process_document`) sequentially.
        
        # We need to mock `scripts.ingest_docs.process_document` to return consistent results.
        
        # When `starmap` is called with `func=process_document`, our `MockPool.starmap`
        # will call `process_document(*args)` for each item in `iterable`.
        
        # We need to mock `process_document` before calling `ingest_docs_main`.
        
        # Let's ensure the mocks are set up correctly for `scripts.ingest_docs`.
        
        # Define a mock `process_document` that returns a successful status for each file.
        # It will be called by our `MockPool.starmap`.
        
        def mock_process_document(*args, **kwargs):
            # Simulate successful processing
            # `args` will contain the unpacked tuple from `files_to_process_info`
            # We expect the last argument to be `file_path`
            file_path = args[-1]
            print(f"Mock processing file: {file_path}") # for debugging if needed
            return {"status": "success", "file": str(file_path)}

        # Patch the `process_document` function *within* the `scripts.ingest_docs` module.
        with patch("scripts.ingest_docs.process_document", side_effect=mock_process_document) as mock_proc_doc:
            # Patch the SQLiteVectorStore and SQLiteMetadataStore to prevent actual DB operations
            with patch("src.doc_intelligence.storage.sqlite_vector_store.SQLiteVectorStore", return_value=mock_vector_store) as mock_vec_store_cls, \
                 patch("src.doc_intelligence.metadata_store.SQLiteMetadataStore", return_value=mock_metadata_store) as mock_meta_store_cls:

                # Call the main function with specific arguments
                runner = CliRunner()
                result = runner.invoke(ingest_docs_main, [
                    str(input_dir),
                    "--doc_types", "txt",
                    "--max-workers", "4",  # Ensure we are testing parallel execution
                    "--vector_store_path", "dummy_db.db" # Provide a dummy path
                ])

                assert result.exit_code == 0, f"Ingestion failed with output: {result.output}"

                # Assert that process_document was called for each file found
                # The number of files is 3 (doc1, doc2, doc3)
                # `starmap` will unpack the arguments, so we check the number of calls to the mocked `process_document`.
                # The iterable passed to starmap contains tuples of arguments for each file.
                # Since we have 3 files, `starmap` will call `process_document` 3 times.
                
                # The mocked `process_document` function is called once for each file.
                # The `files_to_process_info` list has 3 elements.
                # `mock_multiprocessing_pool` executes this sequentially, so `mock_proc_doc` should be called 3 times.
                
                # If `num_workers` > 1, the `main` function will use `multiprocessing.Pool`.
                # Our `MockPool` simulates this sequential execution for testing.
                
                # `mock_proc_doc.call_count` should be equal to the number of files found.
                assert mock_proc_doc.call_count == 3, f"Expected process_document to be called 3 times, but it was called {mock_proc_doc.call_count} times."

                # Verify that metadata store was used to record status
                # Expecting calls for 'started', 'completed' (or 'completed_with_errors'), and potentially others.
                assert mock_metadata_store.add_record.call_count >= 2 # At least start and end record

                # Verify that the vector store's persist method was called
                mock_vector_store.persist.assert_called_once()
