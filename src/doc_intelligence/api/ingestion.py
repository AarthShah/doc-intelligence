from datetime import datetime
import logging
import multiprocessing
from typing import List, Optional
import asyncio

from fastapi import APIRouter, File, Form, UploadFile, status, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# Import the placeholder processing function
from doc_intelligence.ingestion.processor import process_documents
from doc_intelligence.api.dependencies.metadata import get_metadata_store

logger = logging.getLogger(__name__)

# Document processing handlers
def process_document(content: str, metadata: Optional[dict] = None) -> None:
    """Process a document payload and update store."""
    logger.info(f"Processing document: {(metadata or {}).get('filename', 'payload')}")

async def _ingest_document_background(metadata_store: get_metadata_store, content: str, metadata: dict, chunk_size: Optional[int], chunk_overlap: Optional[int]):
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


@router.post("/ingest", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
@router.post("/ingest", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_file(
    background_tasks: BackgroundTasks,
    metadata_store: get_metadata_store,
    file: UploadFile = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
    embedding_provider: Optional[str] = Form("fastembed"),
    embedding_model: Optional[str] = Form(None),
    embedding_api_key: Optional[str] = Form(None)
) -> IngestionResponse:
    """Accept a single document file upload for ingestion."""
    return await ingest_documents(
        background_tasks=background_tasks,
        metadata_store=metadata_store,
        files=[file],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_workers=1,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        embedding_api_key=embedding_api_key,
    )


@router.post("/ingest", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_file(
    background_tasks: BackgroundTasks,
    metadata_store: get_metadata_store,
    file: UploadFile = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
    embedding_provider: Optional[str] = Form("fastembed"),
    embedding_model: Optional[str] = Form(None),
    embedding_api_key: Optional[str] = Form(None)
) -> IngestionResponse:
    """Accept a single document file upload for ingestion."""
    return await ingest_documents(
        background_tasks=background_tasks,
        metadata_store=metadata_store,
        files=[file],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        max_workers=1,
        embedding_provider=embedding_provider,
        embedding_model=embedding_model,
        embedding_api_key=embedding_api_key,
    )


@router.post("", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_documents(
    background_tasks: BackgroundTasks,
    metadata_store: get_metadata_store,
    files: List[UploadFile] = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
    max_workers: Optional[int] = Form(None),
    embedding_provider: Optional[str] = Form("fastembed"),
    embedding_model: Optional[str] = Form(None),
    embedding_api_key: Optional[str] = Form(None)
) -> IngestionResponse:
    """Accept document file uploads for ingestion and asynchronous chunking with optional parallel processing.

    Args:
        background_tasks: BackgroundTasks object for scheduling asynchronous tasks.
        metadata_store: Dependency injection for the metadata store.
        files: List of UploadFile objects to be ingested.
        chunk_size: Optional chunk size for document processing.
        chunk_overlap: Optional chunk overlap for document processing.
        max_workers: The maximum number of worker processes to use for parallel ingestion.
                     Defaults to the number of CPU cores.
    """
    file_names = []
    try:
        for file in files:
            if file.filename:
                file_names.append(file.filename)
                metadata_store.add_record(
                    document_name=file.filename,
                    ingestion_timestamp=datetime.now(),
                    status="received",
                    details="File received by API, queued for processing."
                )

        # Determine the number of workers, defaulting to CPU count if not specified
        num_workers = max_workers if max_workers is not None and max_workers > 0 else multiprocessing.cpu_count()
        
        logger.info(f"Starting parallel ingestion for {len(file_names)} files using {num_workers} workers.")
        
        # Prepare arguments for the process_documents function including embedding provider config
        task_args = [( [fname], chunk_size, chunk_overlap, embedding_provider, embedding_model, embedding_api_key ) for fname in file_names]

        # Use multiprocessing Pool to run process_documents in parallel
        try:
            with multiprocessing.Pool(processes=num_workers) as pool:
                pool.starmap(process_documents, task_args)
            logger.info("Successfully completed parallel ingestion for all files.")
        except Exception as parallel_err:
            logger.error(f"Error encountered during parallel document processing pool execution: {parallel_err}")
            raise
        
        # Update metadata store for all processed files
        for filename in file_names:
            metadata_store.add_record(
                document_name=filename,
                ingestion_timestamp=datetime.now(),
                status="completed",
                details=f"Parallel processing initiated for {filename}."
            )

        return IngestionResponse(
            message="Documents received successfully and queued for parallel processing.",
            received_files=file_names,
            status="processing",
        )
    except Exception as e:
        logger.error(f"An error occurred during document ingestion: {e}")
        # Ensure that if an error occurs, the status reflects failure for any received files
        for filename in file_names:
            metadata_store.add_record(
                document_name=filename,
                ingestion_timestamp=datetime.now(),
                status="failed",
                details=f"Error during ingestion setup: {e}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during document ingestion: {e}",
        )


@router.post("/document", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_document(
    background_tasks: BackgroundTasks,
    metadata_store: get_metadata_store,
    content: str = Form(...),
    filename: str = Form(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
    embedding_provider: Optional[str] = Form("fastembed"),
    embedding_model: Optional[str] = Form(None),
    embedding_api_key: Optional[str] = Form(None),
) -> IngestionResponse:
    """Accept a single document's content for ingestion and asynchronous chunking."""
    metadata = {
        "filename": filename,
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
        "embedding_api_key": embedding_api_key,
    }
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
