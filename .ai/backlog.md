# doc-intelligence Backlog & Priority Matrix

- **P0**: Security & Memory Leakage Guardrails
- **P1**: Core Ingestion and Retrieval Reliability
- **P2**: High-Value Pipeline Features (Chunking, RAG Evaluator, REST API)
- **P3**: External Vector Store Connectors (Chroma, Qdrant)
- **P4**: Unit & Integration Test Coverage
- **P5**: Benchmark Suite & Reproducibility Harness

| ID | Priority | Title | Component | Status |
|---|---|---|---|---|
| DOC-001 | P2 | Implement multi-format document parsers | ingestion | DONE |
| DOC-002 | P2 | Implement semantic and sliding window chunkers | chunking | DONE |
| DOC-003 | P2 | Implement cosine vector store & BM25 hybrid retriever | retrieval | DONE |
| DOC-004 | P2 | Implement RAG faithfulness & hallucination evaluation | evaluation | DONE |
| DOC-005 | P2 | Implement FastAPI server endpoints | api | DONE |
| DOC-006 | P4 | Unit test suite for full pipeline | tests | DONE |
| DOC-007 | P3 | Qdrant and Milvus external connectors | retrieval | PLANNED |
| DOC-008 | P2 | OCR pipeline for scanned PDF tables | ingestion | PLANNED |
