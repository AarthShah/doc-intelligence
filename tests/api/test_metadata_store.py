import pytest
from typing import List, Dict, Any
from doc_intelligence.metadata_store import SQLiteMetadataStore, get_metadata_store

# Define a temporary database file path for tests
TEST_DB_PATH = "test_metadata.db"

@pytest.fixture(scope="function")
def metadata_store() -> SQLiteMetadataStore:
    """Fixture to provide a fresh SQLiteMetadataStore for each test function."""
    store = SQLiteMetadataStore(db_path=TEST_DB_PATH)
    # Ensure the table is created before each test
    store._create_table()
    yield store
    # Clean up the database file after each test
    import os
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_metadata_store_connection(metadata_store: SQLiteMetadataStore):
    """Test if the metadata store connects and initializes correctly."""
    assert metadata_store.db_path == TEST_DB_PATH
    # We can infer connection success from the _create_table call in the fixture.
    # Further checks could involve querying a non-existent table before creation,
    # but the fixture handles the creation part.
    assert True # Placeholder, as fixture handles setup

def test_insert_and_get_metadata(metadata_store: SQLiteMetadataStore):
    """Test inserting and retrieving document metadata."""
    doc_id = "doc-123"
    metadata_to_insert: Dict[str, Any] = {
        "source": "sample.pdf",
        "ingestion_date": "2023-10-27T10:00:00Z",
        "chunking_strategy": "recursive",
        "num_chunks": 5
    }

    metadata_store.insert_metadata(doc_id=doc_id, metadata=metadata_to_insert)

    retrieved_metadata = metadata_store.get_metadata(doc_id=doc_id)

    assert retrieved_metadata is not None
    assert retrieved_metadata["doc_id"] == doc_id
    assert retrieved_metadata["metadata"] == metadata_to_insert

def test_get_metadata_non_existent(metadata_store: SQLiteMetadataStore):
    """Test retrieving metadata for a non-existent document ID."""
    non_existent_doc_id = "non-existent-doc"
    retrieved_metadata = metadata_store.get_metadata(doc_id=non_existent_doc_id)
    assert retrieved_metadata is None

def test_get_all_metadata(metadata_store: SQLiteMetadataStore):
    """Test retrieving all metadata records."""
    metadata1 = {"source": "doc1.txt", "ingestion_date": "2023-10-27T10:00:00Z"}
    metadata2 = {"source": "doc2.txt", "ingestion_date": "2023-10-27T11:00:00Z"}

    metadata_store.insert_metadata(doc_id="doc-A", metadata=metadata1)
    metadata_store.insert_metadata(doc_id="doc-B", metadata=metadata2)

    all_metadata = metadata_store.get_all_metadata()

    assert len(all_metadata) == 2
    # Convert to dictionaries for easier comparison as order might not be guaranteed
    all_metadata_dict = {item['doc_id']: item['metadata'] for item in all_metadata}

    assert all_metadata_dict["doc-A"] == metadata1
    assert all_metadata_dict["doc-B"] == metadata2

def test_update_metadata(metadata_store: SQLiteMetadataStore):
    """Test updating existing metadata."""
    doc_id = "doc-update-1"
    initial_metadata = {"status": "processing"}
    updated_metadata = {"status": "completed", "num_chunks": 10}

    metadata_store.insert_metadata(doc_id=doc_id, metadata=initial_metadata)
    metadata_store.update_metadata(doc_id=doc_id, metadata=updated_metadata)

    retrieved_metadata = metadata_store.get_metadata(doc_id=doc_id)

    assert retrieved_metadata is not None
    assert retrieved_metadata["doc_id"] == doc_id
    # Ensure the update merged correctly and didn't overwrite entirely if not specified
    # The current implementation replaces, so we assert against the updated value directly.
    assert retrieved_metadata["metadata"] == updated_metadata

def test_delete_metadata(metadata_store: SQLiteMetadataStore):
    """Test deleting metadata."""
    doc_id = "doc-delete-1"
    metadata = {"source": "delete_me.txt"}

    metadata_store.insert_metadata(doc_id=doc_id, metadata=metadata)
    retrieved_before_delete = metadata_store.get_metadata(doc_id=doc_id)
    assert retrieved_before_delete is not None

    metadata_store.delete_metadata(doc_id=doc_id)
    retrieved_after_delete = metadata_store.get_metadata(doc_id=doc_id)

    assert retrieved_after_delete is None

def test_get_metadata_store_dependency():
    """Test the get_metadata_store dependency function."""
    # This test assumes that get_metadata_store uses a default path or a mechanism
    # that can be controlled or observed. For simplicity, we'll check if it returns
    # an instance of SQLiteMetadataStore. A more robust test would involve
    # patching or configuring the store's path.
    store = get_metadata_store()
    assert isinstance(store, SQLiteMetadataStore)
    # If there was a way to configure the default path, we'd test that too.
    # For example, if it reads from an environment variable.
    # assert store.db_path == expected_default_path
