import sqlite3
from typing import List, Dict, Any

from fastapi import Depends, FastAPI, HTTPException

# In a real application, this database path would be configurable
DATABASE_PATH = "metadata.db"

class SQLiteMetadataStore:
    """
    A SQLite-based metadata store for tracking document ingestion history.
    """

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Initializes the SQLite database and creates the necessary table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ingestion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL,
                    error_message TEXT
                )
            """)
            conn.commit()

    def add_ingestion_record(self, document_id: str, status: str, error_message: str = None):
        """Adds a record of a document ingestion attempt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ingestion_history (document_id, status, error_message)
                VALUES (?, ?, ?)
            """, (document_id, status, error_message))
            conn.commit()

    def update_ingestion_status(self, document_id: str, status: str, error_message: str = None):
        """Updates the status of an existing ingestion record."""
        with sqlite3.connect(self.db_path) as db:
            cursor = db.cursor()
            cursor.execute("""
                UPDATE ingestion_history
                SET status = ?, error_message = ?
                WHERE document_id = ?
            """, (status, error_message, document_id))
            db.commit()

    def get_ingestion_history(self, document_id: str = None) -> List[Dict[str, Any]]:
        """Retrieves ingestion history, optionally filtered by document_id."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
            cursor = conn.cursor()
            if document_id:
                cursor.execute("SELECT * FROM ingestion_history WHERE document_id = ?", (document_id,))
            else:
                cursor.execute("SELECT * FROM ingestion_history")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

def get_metadata_store() -> SQLiteMetadataStore:
    """
    FastAPI dependency to provide an instance of SQLiteMetadataStore.
    """
    store = SQLiteMetadataStore()
    # In a more complex app, you might want to manage the lifecycle
    # of the store instance more explicitly (e.g., opening/closing connections)
    # For this example, we rely on SQLite's connection handling.
    return store

# Example of how this might be used in a FastAPI app:
# app = FastAPI()
#
# @app.post("/ingest")
# async def ingest_document(file: UploadFile = File(...), metadata_store: SQLiteMetadataStore = Depends(get_metadata_store)):
#     document_id = str(uuid.uuid4()) # Generate a unique ID for the document
#     metadata_store.add_ingestion_record(document_id=document_id, status="processing")
#     try:
#         # ... document processing logic ...
#         content = await file.read()
#         # Simulate processing
#         await asyncio.sleep(1)
#         metadata_store.update_ingestion_status(document_id=document_id, status="completed")
#         return {"message": "Document processed successfully", "document_id": document_id}
#     except Exception as e:
#         metadata_store.update_ingestion_status(document_id=document_id, status="failed", error_message=str(e))
#         raise HTTPException(status_code=500, detail=f"Document processing failed: {e}")
