from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends
from typing import List
from pydantic import BaseModel
from doc_intelligence.api.ingestion import process_document, IngestionResponse
from doc_intelligence.api.dependencies.rate_limiter import RateLimiter

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

class DocumentIngestRequest(BaseModel):
    content: str
    metadata: dict = {}

@router.post("/documents", dependencies=[Depends(RateLimiter(requests_per_unit=2, unit_seconds=10))])
async def ingest_documents(files: List[UploadFile] = File(...)):
    """
    Ingests a list of documents and initiates asynchronous chunking.
    """
    # In a real application, you would:
    # 1. Process each uploaded file (e.g., save to disk, extract text).
    # 2. Validate the content.
    # 3. Convert documents to a standardized format.
    # 4. Add chunking tasks to a background processing queue (e.g., Celery, Dramatiq).
    # 5. Return a response indicating the ingestion process has started.

    # For now, we'll just return a confirmation message.
    file_names = [file.filename for file in files]
    return {"message": "Documents received for ingestion.", "filenames": file_names}

@router.post("/ingest", response_model=IngestionResponse, dependencies=[Depends(RateLimiter(requests_per_unit=5, unit_seconds=5))])
async def ingest_document(request: DocumentIngestRequest, background_tasks: BackgroundTasks) -> IngestionResponse:
    """
    Ingests a document payload containing content and metadata,
    and initiates asynchronous chunking via background tasks.
    """
    background_tasks.add_task(process_document, request.content, request.metadata)
    return IngestionResponse(message="Document ingestion initiated.", status="processing")
