import logging
import sqlite3
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MetadataStore(ABC):
    """
    Abstract base class for metadata storage.

    This class defines the interface for storing and retrieving document ingestion metadata.
    """

    @abstractmethod
    def add_record(self, record: Dict[str, Any]) -> None:
        """Adds a new ingestion record to the store."""
        pass

    @abstractmethod
    def get_records(self, document_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves ingestion records from the store.

        Args:
            document_id: If provided, filters records by this document ID.

        Returns:
            A list of ingestion records.
        """
        pass

class SQLiteMetadataStore(MetadataStore):
    """
    Concrete implementation of MetadataStore using SQLite.

    Handles the creation of the metadata table and provides methods for adding
    and retrieving ingestion records.
    """

    def __init__(self, db_path: str = "metadata.db"):
        """
        Initializes the SQLiteMetadataStore.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        """Creates the metadata table if it does not exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ingestion_metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        document_id TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT,
                        details TEXT
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error during initialization: {e}")
            raise

    def add_record(self, record: Dict[str, Any]) -> None:
        """
        Adds a new ingestion record to the SQLite database.

        Args:
            record: A dictionary containing the ingestion metadata. Expected keys:
                    'document_id', 'status', 'details'.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO ingestion_metadata (document_id, status, details)
                    VALUES (:document_id, :status, :details)
                """, record)
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database error adding record for document {record.get('document_id', 'N/A')}: {e}")
            raise

    def get_records(self, document_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieves ingestion records from the SQLite database.

        Args:
            document_id: If provided, filters records by this document ID.

        Returns:
            A list of dictionaries, where each dictionary represents an ingestion record.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
                cursor = conn.cursor()
                query = "SELECT id, document_id, timestamp, status, details FROM ingestion_metadata"
                params = {}
                if document_id:
                    query += " WHERE document_id = :document_id"
                    params["document_id"] = document_id

                cursor.execute(query, params)
                records = [dict(row) for row in cursor.fetchall()]
                return records
        except sqlite3.Error as e:
            logging.error(f"Database error retrieving records for document {document_id if document_id else 'all'}: {e}")
            raise
