import pytest
from unittest.mock import MagicMock, patch
from doc_intelligence.retrieval.vector_store import VectorStore, VectorStoreError
import os

def test_vector_store_initialization():
    store = VectorStore(dimension=128)
    assert store.dimension == 128

@patch("doc_intelligence.retrieval.vector_store.sqlite3")
def test_vector_store_add_error_handling(mock_sqlite):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("DB failure")
    mock_conn.cursor.return_value = mock_cursor
    mock_sqlite.connect.return_value = mock_conn

    store = VectorStore(dimension=128, db_path=":memory:")
    with pytest.raises(VectorStoreError):
        store.add(vectors=[[0.1] * 128], metadata=[{"id": 1}])

@patch("doc_intelligence.retrieval.vector_store.sqlite3")
def test_vector_store_search_error_handling(mock_sqlite):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Search query failed")
    mock_conn.cursor.return_value = mock_cursor
    mock_sqlite.connect.return_value = mock_conn

    store = VectorStore(dimension=128, db_path=":memory:")
    with pytest.raises(VectorStoreError):
        store.search(query_vector=[0.1] * 128, top_k=5)

def test_vector_store_persistence():
    file_path = "test_vector_store.db"
    dimension = 128
    vectors = [[float(i) * 0.1] * dimension for i in range(5)]
    metadata = [{"id": i} for i in range(5)]

    # Test saving and loading
    store1 = VectorStore(dimension=dimension, db_path=file_path)
    store1.add(vectors=vectors, metadata=metadata)
    store1.close()

    store2 = VectorStore(dimension=dimension, db_path=file_path)
    loaded_vectors, loaded_metadata = store2.get_all_data() # Assuming such a method exists or will be added
    assert len(loaded_vectors) == len(vectors)
    assert len(loaded_metadata) == len(metadata)
    for i in range(len(vectors)):
        assert loaded_vectors[i] == vectors[i]
        assert loaded_metadata[i] == metadata[i]
    store2.close()

    # Test delete operation persistence
    store3 = VectorStore(dimension=dimension, db_path=file_path)
    store3.delete(ids=[0, 2]) # Assuming delete by id is implemented
    remaining_vectors, remaining_metadata = store3.get_all_data()
    assert len(remaining_vectors) == 3
    assert len(remaining_metadata) == 3
    assert remaining_metadata[0]["id"] == 1
    assert remaining_metadata[1]["id"] == 3
    assert remaining_metadata[2]["id"] == 4
    store3.close()

    # Clean up the test file
    if os.path.exists(file_path):
        os.remove(file_path)

def test_vector_store_empty_persistence():
    file_path = "empty_test_vector_store.db"
    dimension = 128

    # Test initialization with an empty store
    store1 = VectorStore(dimension=dimension, db_path=file_path)
    vectors, metadata = store1.get_all_data()
    assert len(vectors) == 0
    assert len(metadata) == 0
    store1.close()

    # Test loading an empty store
    store2 = VectorStore(dimension=dimension, db_path=file_path)
    vectors, metadata = store2.get_all_data()
    assert len(vectors) == 0
    assert len(metadata) == 0
    store2.close()

    # Clean up the test file
    if os.path.exists(file_path):
        os.remove(file_path)

def test_vector_store_index_caching():
    file_path = "cache_test_vector_store.db"
    dimension = 128
    vectors = [[float(i) * 0.1] * dimension for i in range(5)]
    metadata = [{"id": i} for i in range(5)]

    # Test initial load and cache population
    store1 = VectorStore(dimension=dimension, db_path=file_path)
    store1.add(vectors=vectors, metadata=metadata)
    store1.close()

    # When VectorStore is initialized, it should load from DB and populate cache
    store2 = VectorStore(dimension=dimension, db_path=file_path)
    # Accessing data through get_all_data should utilize the cache
    loaded_vectors, loaded_metadata = store2.get_all_data()
    assert len(loaded_vectors) == len(vectors)
    assert len(loaded_metadata) == len(metadata)
    assert loaded_vectors == vectors
    assert loaded_metadata == metadata
    store2.close()

    # Test add operation updates cache
    store3 = VectorStore(dimension=dimension, db_path=file_path)
    new_vector = [[0.5] * dimension]
    new_metadata = [{"id": 5}]
    store3.add(vectors=new_vector, metadata=new_metadata)
    # Accessing data should now include the new entry
    loaded_vectors_after_add, loaded_metadata_after_add = store3.get_all_data()
    assert len(loaded_vectors_after_add) == len(vectors) + 1
    assert len(loaded_metadata_after_add) == len(metadata) + 1
    assert loaded_vectors_after_add[-1] == new_vector[0]
    assert loaded_metadata_after_add[-1] == new_metadata[0]
    store3.close()

    # Test delete operation updates cache
    store4 = VectorStore(dimension=dimension, db_path=file_path)
    store4.delete(ids=[0, 2, 5]) # Delete some existing and the newly added
    remaining_vectors, remaining_metadata = store4.get_all_data()
    assert len(remaining_vectors) == 3
    assert len(remaining_metadata) == 3
    # Check that the correct items remain
    expected_ids = {1, 3, 4}
    actual_ids = {m["id"] for m in remaining_metadata}
    assert actual_ids == expected_ids
    store4.close()

    # Clean up the test file
    if os.path.exists(file_path):
        os.remove(file_path)

# Note: Concurrency testing might require a more sophisticated setup
# involving threading or multiprocessing, which could be a separate test suite.
