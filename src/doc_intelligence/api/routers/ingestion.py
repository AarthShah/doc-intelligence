from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from doc_intelligence.api.ingestion import process_document, IngestionResponse
from doc_intelligence.api.dependencies.rate_limiter import RateLimiter

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

from doc_intelligence.api.models import DocumentIngestRequest

@router.post("/documents", dependencies=[Depends(RateLimiter(requests_per_unit=2, unit_seconds=10))])
async def ingest_documents(files: List[UploadFile] = File(...), max_workers: int = 1):
    """
    Ingests a list of documents and initiates asynchronous chunking.

    Args:
        files: A list of uploaded files.
        max_workers: The maximum number of worker processes to use for parallel ingestion. Defaults to 1.
    """
    if not isinstance(max_workers, int) or max_workers <= 0:
        raise HTTPException(status_code=400, detail="max_workers must be a positive integer.")

    # In a real application, you would:
    # 1. Process each uploaded file (e.g., save to disk, extract text).
    # 2. Validate the content.
    # 3. Convert documents to a standardized format.
    # 4. Add chunking tasks to a background processing queue (e.g., Celery, Dramatiq).
    # 5. Return a response indicating the ingestion process has started.

    # For now, we'll just return a confirmation message.
    # The actual parallel processing logic would be implemented in process_document
    # or a similar function that handles batch processing.
    file_names = [file.filename for file in files]
    return {"message": f"Documents received for ingestion with max_workers={max_workers}.", "filenames": file_names}

@router.post("/ingest", response_model=IngestionResponse, dependencies=[Depends(RateLimiter(requests_per_unit=5, unit_seconds=5))])
async def ingest_document(request: DocumentIngestRequest, background_tasks: BackgroundTasks) -> IngestionResponse:
    """
    Ingests a document payload containing content and metadata,
    and initiates asynchronous chunking via background tasks.
    """
    try:
        background_tasks.add_task(process_document, request.content, request.metadata)
        return IngestionResponse(message="Document ingestion initiated.", status="processing")
    except Exception as e:
        from doc_intelligence.exceptions import ParsingError, VectorStoreError, DocumentIntelligenceError
        if isinstance(e, ParsingError):
            raise HTTPException(status_code=400, detail=str(e))
        elif isinstance(e, VectorStoreError):
            raise HTTPException(status_code=500, detail=str(e))
        elif isinstance(e, DocumentIntelligenceError):
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))
