# doc-intelligence Architecture Blueprint

## System Architecture

```mermaid
graph TD
    RawDocs[Raw Documents: PDF, MD, TXT] --> Ingestion[Ingestion Engine]
    Ingestion --> ParsedDoc[Normalized Document Object]
    
    ParsedDoc --> ChunkEngine[Semantic Chunking Engine]
    ChunkEngine --> Chunks[Atomic Semantic Chunks]
    
    Chunks --> DenseStore[In-Memory Dense Vector Store]
    Chunks --> LexicalStore[BM25 Lexical Index]
    
    Query[User / Agent Query] --> HybridRetriever[Hybrid Retriever: Reciprocal Rank Fusion]
    DenseStore --> HybridRetriever
    LexicalStore --> HybridRetriever
    
    HybridRetriever --> RetrievedContext[Ranked Context Window]
    RetrievedContext --> Generator[LLM Generator]
    Generator --> GeneratedAnswer[Generated Answer]
    
    GeneratedAnswer --> Evaluator[RAG Hallucination & Faithfulness Evaluator]
    RetrievedContext --> Evaluator
    Evaluator --> EvalMetrics[Evaluation Metrics: Faithfulness, Recall, Relevance]
```

## Module Structure
- `doc_intelligence.models`: Core data classes (`Document`, `Chunk`, `QueryResult`, `EvaluationReport`).
- `doc_intelligence.ingestion`: Parsers for structured and unstructured formats with metadata extraction.
- `doc_intelligence.chunking`: Boundary-aware semantic chunker with token budget constraints.
- `doc_intelligence.retrieval`: Hybrid retrieval combining dense vector similarity and BM25 keyword matching.
- `doc_intelligence.evaluation`: Verifiable RAG evaluation metrics without external proprietary APIs.
- `doc_intelligence.api`: Async FastAPI application with OpenAPI documentation.
