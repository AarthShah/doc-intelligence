import pytest
from unittest.mock import MagicMock, patch
from doc_intelligence.retrieval.vector_store import VectorStore, VectorStoreError

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
