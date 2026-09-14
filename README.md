# doc-intelligence

> **Industrial-Grade Autonomous Document Intelligence & RAG Evaluation Platform** — Multimodal parsing, semantic chunking, hybrid vector retrieval, and automated hallucination scoring.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen.svg)](https://github.com/AarthShah/doc-intelligence)

---

## 1. Overview

`doc-intelligence` is an enterprise-grade document intelligence platform designed to ingest complex multi-format documents (PDFs, Markdown, raw text), partition them into semantically cohesive chunks, perform hybrid vector search (Dense Cosine + Lexical BM25 with Reciprocal Rank Fusion), and provide verifiable RAG evaluation metrics to measure faithfulness and detect hallucinations.

---

## 2. Problem

Building production Retrieval-Augmented Generation (RAG) systems presents steep engineering challenges:
- **Arbitrary Chunking Splitting**: Fixed-character splitting cuts sentences and tables in half, destroying context.
- **Single-Mode Retrieval Failure**: Pure vector search misses exact keyword matches (IDs, part numbers, dates), while pure keyword search misses semantic synonyms.
- **Untracked Hallucinations**: Most teams deploy LLMs without quantitative measurement of whether answers are faithful to the retrieved context or hallucinated.

---

## 3. Motivation

`doc-intelligence` solves these bottlenecks with a deterministic, modular pipeline that unifies ingestion, chunking, hybrid retrieval, and automated statistical evaluation without forcing dependencies on proprietary closed-source APIs.

---

## 4. Features

- **📄 Multimodal Document Ingestion**: Structured extractors for Plaintext, Markdown headers/tables, and PDF documents.
- **✂️ Semantic & Sliding-Window Chunkers**: Sentence-aware boundary chunking with configurable overlap and token budgeting.
- **🔍 Hybrid Retrieval Engine**: Combines dense semantic vector embeddings with BM25 lexical search using Reciprocal Rank Fusion (RRF).
- **📊 Verifiable RAG Evaluation**: Quantitative scoring for Faithfulness, Answer Relevance, Context Recall, and Hallucination Risk.
- **⚡ High-Performance REST API**: Async FastAPI endpoints for ingestion, query, and evaluation.
- **🛡️ 100% Offline Capable**: Zero mandatory external cloud dependencies; run locally with complete privacy.

---

## 5. Architecture

```text
Raw Documents (PDF, MD, TXT)
            │
            ▼
┌───────────────────────────────┐
│     Ingestion Subsystem       │
│  (Metadata, Sections, Clean)  │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│   Semantic Chunking Engine    │
│ (Boundary Aware + Overlap)    │
└───────────────┬───────────────┘
                │
                ├─────────────────────────────┐
                ▼                             ▼
┌───────────────────────────────┐  ┌─────────────────────────┐
│   Dense Vector Store (Cos)    │  │  BM25 Lexical Ranker    │
└───────────────┬───────────────┘  └──────────┬──────────────┘
                │                             │
                └──────────────┬──────────────┘
                               ▼
            ┌────────────────────────────────────┐
            │ Hybrid Retriever (Rank Fusion RRF) │
            └──────────────────┬─────────────────┘
                               │
                               ▼
            ┌────────────────────────────────────┐
            │   RAG Evaluation & Hallucination   │
            │  (Faithfulness, Recall, Precision) │
            └────────────────────────────────────┘
```

---

## 6. Installation

```bash
git clone https://github.com/AarthShah/doc-intelligence.git
cd doc-intelligence

# Install package
python -m pip install -e .
```

---

## 7. Quick Start

```python
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator

# 1. Parse document
parser = TextParser()
doc = parser.parse("Deep learning models require clean training data. RAG systems reduce hallucinations by grounding generation in retrieved documents.")

# 2. Chunk semantically
chunker = SemanticChunker(max_chunk_size=100)
chunks = chunker.chunk(doc)

# 3. Index in hybrid retriever
retriever = HybridRetriever()
retriever.index(chunks)

# 4. Search
results = retriever.search("How do RAG systems reduce hallucinations?", top_k=2)
for r in results:
    print(f"[{r.score:.3f}] {r.chunk.text}")

# 5. Evaluate answer faithfulness
evaluator = RAGEvaluator()
report = evaluator.evaluate(
    query="How do RAG systems reduce hallucinations?",
    context=[r.chunk.text for r in results],
    answer="RAG systems reduce hallucinations by grounding generation in retrieved context."
)
print("Faithfulness:", report.faithfulness_score)
print("Hallucination Risk:", report.hallucination_score)
```

---

## 8. API Reference

Start the REST API server:
```bash
python -m doc_intelligence.api.app
```
Endpoints:
- `GET /health`: Health status and index statistics.
- `POST /ingest`: Ingest raw text or markdown with automatic chunking.
- `POST /query`: Search indexed documents with hybrid retrieval.
- `POST /evaluate`: Compute faithfulness, relevance, and hallucination scores.

---

## 9. Testing

Run the automated test suite:
```bash
python -m unittest discover -s tests -v
```

---

## 10. Roadmap

- [x] **Milestone 1**: Multi-Format Ingestion, Semantic Chunking, Vector Retrieval & RAG Evaluator
- [ ] **Milestone 2**: FastAPI Async Serving & Streaming Inference
- [ ] **Milestone 3**: Multimodal OCR & Tabular PDF Extraction
- [ ] **Milestone 4**: Distributed Vector Store Connectors (Milvus, Qdrant, Chroma)
- [ ] **Milestone 5**: Automated Benchmark Suite & 1.0 Production Release

---

## 11. Contributing

Pull requests are welcome! Please ensure that all changes include comprehensive unit tests and follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## 12. License

Licensed under the MIT License. See [LICENSE](LICENSE) for details.
