from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, status, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncio
from datetime import datetime

# Import the placeholder processing function
from src.doc_intelligence.ingestion.processor import process_documents
# Import the metadata store dependency
from src.doc_intelligence.metadata_store.sqlite_store import get_metadata_store

def process_document(*args, **kwargs):
    """Placeholder for single document processing."""
    pass

import logging

logger = logging.getLogger(__name__)

# Placeholder for background task
async def _ingest_document_background(metadata_store: get_metadata_store, content: str, metadata: dict, chunk_size: Optional[int], chunk_overlap: Optional[int]):
    """Placeholder for the actual document ingestion and chunking logic."""
    filename = metadata.get("filename", "unknown")
    try:
        print(f"Processing document: {filename}")
        # Update metadata store with processing status
        metadata_store.add_record(
            document_name=filename,
            ingestion_timestamp=datetime.now(),
            status="processing",
            details=f"Chunking and embedding initiated for {filename}."
        )
        # In a real implementation, this would call the chunking and embedding logic
        await asyncio.sleep(1) # Simulate async work
        print(f"Finished processing document: {filename}")
        metadata_store.add_record(
            document_name=filename,
            ingestion_timestamp=datetime.now(), # This might need to be the original ingestion timestamp
            status="completed",
            details=f"Successfully processed {filename}."
        )
    except Exception as e:
        logger.error(f"Error occurred during document processing for {filename}: {e}")
        metadata_store.add_record(
            document_name=filename,
            ingestion_timestamp=datetime.now(), # This might need to be the original ingestion timestamp
            status="failed",
            details=f"Error processing {filename}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during document processing: {e}",
        )


router = APIRouter(prefix="/documents", tags=["ingestion"])


class IngestionResponse(BaseModel):
    """Response model for document ingestion."""
    message: str
    received_files: List[str] = Field(default_factory=list)
    status: str = "received"


@router.post("", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_documents(
    background_tasks: BackgroundTasks,
    metadata_store: get_metadata_store,
    files: List[UploadFile] = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
) -> IngestionResponse:
    """Accept document file uploads for ingestion and asynchronous chunking."""
    try:
        file_names = []
        for file in files:
            if file.filename:
                file_names.append(file.filename)
                metadata_store.add_record(
                    document_name=file.filename,
                    ingestion_timestamp=datetime.now(),
                    status="received",
                    details="File received by API, queued for processing."
                )

        background_tasks.add_task(process_documents, file_names, chunk_size, chunk_overlap)

        return IngestionResponse(
            message="Documents received successfully and queued for processing.",
            received_files=file_names,
            status="processing",
        )
    except Exception as e:
        # Log the error and raise an HTTPException
        logger.error(f"An error occurred during document ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during document ingestion: {e}",
        )


    # Endpoint for single document ingestion
    @router.post("/document", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
    async def ingest_document(
        background_tasks: BackgroundTasks,
        metadata_store: get_metadata_store,
        content: str = Form(...),
        filename: str = Form(...),
        chunk_size: Optional[int] = Form(None),
        chunk_overlap: Optional[int] = Form(None),
    ) -> IngestionResponse:
        """Accept a single document's content for ingestion and asynchronous chunking."""
        metadata = {"filename": filename}
        try:
            metadata_store.add_record(
                document_name=filename,
                ingestion_timestamp=datetime.now(),
                status="received",
                details="Single document content received by API, queued for processing."
            )
            background_tasks.add_task(_ingest_document_background, metadata_store, content, metadata, chunk_size, chunk_overlap)
            return IngestionResponse(
                message="Document received successfully and queued for processing.",
                received_files=[filename],
                status="processing",
            )
        except Exception as e:
            logger.error(f"An error occurred during document ingestion for {filename}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during document ingestion: {e}",
            )
from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, status, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
import asyncio

# Import the placeholder processing function
from src.doc_intelligence.ingestion.processor import process_documents

import logging

logger = logging.getLogger(__name__)

# Placeholder for background task
async def _ingest_document_background(content: str, metadata: dict, chunk_size: Optional[int], chunk_overlap: Optional[int]):
    """Placeholder for the actual document ingestion and chunking logic."""
    try:
        print(f"Processing document: {metadata.get('filename')}")
        # In a real implementation, this would call the chunking and embedding logic
        await asyncio.sleep(1) # Simulate async work
        print(f"Finished processing document: {metadata.get('filename')}")
    except Exception as e:
        logger.error(f"Error occurred during document processing: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during document processing: {e}",
        )


router = APIRouter(prefix="/documents", tags=["ingestion"])


class IngestionResponse(BaseModel):
    """Response model for document ingestion."""
    message: str
    received_files: List[str] = Field(default_factory=list)
    status: str = "received"


@router.post("", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
) -> IngestionResponse:
    """Accept document file uploads for ingestion and asynchronous chunking."""
    try:
        file_names = [file.filename for file in files if file.filename]

        background_tasks.add_task(process_documents, file_names, chunk_size, chunk_overlap)

        return IngestionResponse(
            message="Documents received successfully and queued for processing.",
            received_files=file_names,
            status="processing",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during document ingestion: {e}",
        )


    # Endpoint for single document ingestion
    @router.post("/document", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
    async def ingest_document(
        background_tasks: BackgroundTasks,
        content: str = Form(...),
        filename: str = Form(...),
        chunk_size: Optional[int] = Form(None),
        chunk_overlap: Optional[int] = Form(None),
    ) -> IngestionResponse:
        """Accept a single document's content for ingestion and asynchronous chunking."""
        metadata = {"filename": filename}
        try:
            background_tasks.add_task(_ingest_document_background, content, metadata, chunk_size, chunk_overlap)
            return IngestionResponse(
                message="Document received successfully and queued for processing.",
                received_files=[filename],
                status="processing",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during document ingestion: {e}",
            )
