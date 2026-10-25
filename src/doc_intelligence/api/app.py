"""REST API server for doc-intelligence."""

from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Request
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore

from doc_intelligence import __version__
from doc_intelligence.api.dependencies.rate_limiter import RateLimiter
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever
from doc_intelligence.retrieval.context_compressor import ContextCompressor
from doc_intelligence.ingestion.epub_extractor import EpubExtractor
from doc_intelligence.sanitizer import DocumentSanitizer
from doc_intelligence.api.routers.ingestion import router as ingestion_router
from doc_intelligence.api.routers.evaluation import router as evaluation_router
from sentence_transformers import SentenceTransformer

# Global retriever & evaluator instances for the service
retriever = HybridRetriever()
evaluator = RAGEvaluator()
parser = TextParser()
chunker = SemanticChunker(max_chunk_size=300)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
context_compressor = ContextCompressor(embedding_model=embedding_model)

# Instantiate rate limiter for API request throttling
rate_limiter = RateLimiter(requests_per_unit=100, unit_seconds=60)


def enforce_rate_limit(request: Request, limiter: RateLimiter = Depends(lambda: rate_limiter)) -> RateLimiter:
    """
    FastAPI dependency that checks the request against the global RateLimiter.
    Raises HTTP 429 if the client has exceeded the allowed request quota.
    """
    client_ip = request.client.host if request.client else "unknown"
    check_fn = getattr(limiter, "is_allowed", getattr(limiter, "allow", None))
    if check_fn and not check_fn(client_ip):
        raise HTTPException(status_code=429, detail="Too Many Requests")
    return limiter


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="doc-intelligence API",
        description="Autonomous AI Document Intelligence & RAG Evaluation Platform",
        version=__version__,
        dependencies=[Depends(enforce_rate_limit)],
    )

    app.include_router(ingestion_router, prefix="/api/v1/ingestion")
    app.include_router(evaluation_router, prefix="/api/v1/evaluation")

    class IngestRequest(BaseModel):
        text: str
        source_name: str = "api_payload"
        format: str = "plaintext"

    class QueryRequest(BaseModel):
        query: str
        top_k: int = 5
        compress_context: bool = False

    class EvaluateRequest(BaseModel):
        query: str
        contexts: List[str]
        answer: str
        ground_truth: Optional[str] = None

    @app.get("/health")
    def health_check(request: Request) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "version": __version__,
            "indexed_chunks": retriever.vector_store.count,
        }

    @app.post("/ingest/text")
    def ingest_document(
        request: Request,
        req: IngestRequest,
        redact_pii: bool = False,
    ) -> Dict[str, Any]:
        sanitizer = DocumentSanitizer() if redact_pii else None
        doc = parser.parse(req.text, source_name=req.source_name, sanitizer=sanitizer)
        chunks = chunker.chunk(doc)
        retriever.index(chunks)
        return {
            "message": "Document ingested and indexed successfully",
            "doc_id": doc.id,
            "chunks_created": len(chunks),
            "total_index_count": retriever.vector_store.count,
        }

    @app.post("/query")
    def search_documents(
        request: Request,
        req: QueryRequest,
    ) -> Dict[str, Any]:
        results = retriever.search(req.query, top_k=req.top_k)
        formatted_results = []
        for r in results:
            text = r.chunk.text
            if req.compress_context:
                text = context_compressor.compress(text)
            formatted_results.append({
                "text": text,
                "score": r.score,
                "chunk_id": r.chunk.id,
                "method": r.retrieval_method,
            })
        return {
            "query": req.query,
            "results_count": len(results),
            "results": formatted_results,
        }

    @app.post("/api/v1/evaluate")
    def evaluate_rag(
        request: Request,
        req: EvaluateRequest,
    ) -> Dict[str, Any]:
        report = evaluator.evaluate(
            query=req.query,
            context=req.contexts,
            answer=req.answer,
            ground_truth=req.ground_truth or "",
        )
        return {
            "faithfulness": report.faithfulness_score,
            "answer_relevance": report.answer_relevance_score,
            "context_recall": report.context_recall_score,
            "hallucination_score": report.hallucination_score,
            "details": report.details,
        }

    @app.post("/ingest/epub")
    async def ingest_epub(
        request: Request,
        file: UploadFile = File(...),
    ) -> Dict[str, Any]:
        """Ingest an EPUB file, extract its sections, and return them as JSON."""
        import tempfile, os
        from pathlib import Path

        # Save uploaded file to a temporary location
        suffix = Path(file.filename).suffix if file.filename else ".epub"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            extractor = EpubExtractor(tmp_path)
            sections = extractor.extract()
        finally:
            # Clean up the temporary file
            os.remove(tmp_path)

        return {"sections": sections}

else:
    # Minimal fallback mock object if FastAPI is not installed
    class DummyApp:
        def __init__(self):
            self.title = "doc-intelligence API (FastAPI not installed)"
    app = DummyApp()  # type: ignore


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("doc_intelligence.api.app:app", host="0.0.0.0", port=8000, reload=True)
