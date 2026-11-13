# Load Testing Findings and Optimization Strategy

## Overview
This document summarizes the findings from load testing performed using Locust against the FastAPI endpoints (`/ingest` and `/search`), identifies performance bottlenecks, and outlines the next steps for optimization.

## Locust Test Summary
- **Scenarios Tested**:
  1. `ingest_document`: Multipart file uploads simulating document ingestion traffic.
  2. `search_documents`: Search queries testing retrieval latency and throughput.
  3. `test_rate_limit_burst` & `test_rate_limit_high_frequency`: High-frequency requests targeting the rate limiter.

## Identified Performance Bottlenecks
1. **Embedding Generation / Vector Search Latency**: 
   - Embedding models (`SentenceTransformers` / `FastEmbed`) and vector store queries introduce noticeable latency under high concurrency, leading to increased response times on `/search`.
2. **Synchronous Ingestion Overhead**: 
   - Processing document parsing, chunking, and metadata storage synchronously during `/ingest` blocks request threads, lowering ingestion throughput and causing queue buildup.
3. **Metadata Store Contention**: 
   - SQLite metadata store locking under high concurrent write operations from ingestion tasks leads to occasional delays and transaction retries.
4. **Rate Limiter Overhead**: 
   - In-memory rate limiting tracking scales well for single instances, but adds overhead per request during burst traffic conditions.

## Proposed Next Steps for Optimization
1. **Asynchronous Processing**:
   - Offload document parsing, chunking, and embedding generation to background workers (e.g., Celery or FastAPI background tasks with queues) for the `/ingest` endpoint.
2. **Vector Store and Embedding Caching**:
   - Implement caching for frequent queries and explore optimized vector index configurations to reduce similarity search latency.
3. **Database Connection Pooling and Concurrency Tuning**:
   - Optimize SQLite PRAGMA settings (e.g., `journal_mode=WAL`) or evaluate migrating high-concurrency deployments to PostgreSQL for improved write concurrency.
4. **Rate Limiter Refinement**:
   - Transition rate limiter state tracking to a distributed store (e.g., Redis) if horizontal scaling is required in production environments.
