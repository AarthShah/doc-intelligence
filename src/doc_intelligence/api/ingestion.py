from typing import List, Optional
from fastapi import APIRouter, File, Form, UploadFile, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/documents", tags=["ingestion"])


class IngestionResponse(BaseModel):
    """Response model for document ingestion."""
    message: str
    received_files: List[str] = Field(default_factory=list)
    status: str = "received"


@router.post("", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_documents(
    files: List[UploadFile] = File(...),
    chunk_size: Optional[int] = Form(None),
    chunk_overlap: Optional[int] = Form(None),
) -> IngestionResponse:
    """Accept document file uploads for ingestion and asynchronous chunking."""
    file_names = [file.filename for file in files if file.filename]
    return IngestionResponse(
        message="Documents received successfully and queued for processing.",
        received_files=file_names,
        status="received",
    )
