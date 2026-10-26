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
