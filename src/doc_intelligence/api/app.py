"""REST API server for doc-intelligence."""

from typing import Any, Dict, List, Optional

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore

from doc_intelligence import __version__
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever

# Global retriever & evaluator instances for the service
retriever = HybridRetriever()
evaluator = RAGEvaluator()
parser = TextParser()
chunker = SemanticChunker(max_chunk_size=300)


if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="doc-intelligence API",
        description="Autonomous AI Document Intelligence & RAG Evaluation Platform",
        version=__version__,
    )

    class IngestRequest(BaseModel):
        text: str
        source_name: str = "api_payload"
        format: str = "plaintext"

    class QueryRequest(BaseModel):
        query: str
        top_k: int = 5

    class EvaluateRequest(BaseModel):
        query: str
        context: List[str]
        answer: str
        ground_truth: Optional[str] = None

    @app.get("/health")
    def health_check() -> Dict[str, Any]:
        return {
            "status": "healthy",
            "version": __version__,
            "indexed_chunks": retriever.vector_store.count,
        }

    @app.post("/ingest")
    def ingest_document(req: IngestRequest) -> Dict[str, Any]:
        doc = parser.parse(req.text, source_name=req.source_name)
        chunks = chunker.chunk(doc)
        retriever.index(chunks)
        return {
            "message": "Document ingested and indexed successfully",
            "doc_id": doc.id,
            "chunks_created": len(chunks),
            "total_index_count": retriever.vector_store.count,
        }

    @app.post("/query")
    def search_documents(req: QueryRequest) -> Dict[str, Any]:
        results = retriever.search(req.query, top_k=req.top_k)
        return {
            "query": req.query,
            "results_count": len(results),
            "results": [
                {
                    "text": r.chunk.text,
                    "score": r.score,
                    "chunk_id": r.chunk.id,
                    "method": r.retrieval_method,
                }
                for r in results
            ],
        }

    @app.post("/evaluate")
    def evaluate_rag(req: EvaluateRequest) -> Dict[str, Any]:
        report = evaluator.evaluate(
            query=req.query,
            context=req.context,
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

else:
    # Minimal fallback mock object if FastAPI is not installed
    class DummyApp:
        def __init__(self):
            self.title = "doc-intelligence API (FastAPI not installed)"
    app = DummyApp()  # type: ignore


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("doc_intelligence.api.app:app", host="0.0.0.0", port=8000, reload=True)
