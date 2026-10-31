from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from src.doc_intelligence.api.rate_limiter import RateLimiter
from src.doc_intelligence.chunking.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from src.doc_intelligence.models import Document
from src.doc_intelligence.retrieval.hybrid_retriever import HybridRetriever
from src.doc_intelligence.retrieval.reranker import Reranker
from src.doc_intelligence.retrieval.token_budget_manager import TokenBudgetManager

# router will be defined after get_rate_limiter

# Dependencies
def get_retriever() -> HybridRetriever:
    # In a real application, this would fetch the retriever from a shared state or dependency injection
    # For now, we'll mock it up.
    # NOTE: This is a placeholder and needs to be replaced with actual retriever initialization.
    # Ensure that the retriever is properly initialized with embeddings and vector stores.
    print("Initializing HybridRetriever (placeholder)...")
    # Placeholder for actual retriever initialization
    # Example: retriever = HybridRetriever(vector_store=..., embedding_model=...)
    # Returning a dummy instance for now.
    # A more robust solution would involve passing necessary components like embedding models and vector stores.
    # Ensure the dummy retriever has necessary methods like 'search' for the endpoint to work.
    class DummyHybridRetriever:
        def search(self, query: str, k: int = 5) -> List[Document]:
            print(f"DummyHybridRetriever searching for: {query}")
            # Simulate returning some dummy documents
            return [
                Document(page_content="This is a dummy document 1.", metadata={"source": "doc1.txt"}),
                Document(page_content="This is another dummy document 2.", metadata={"source": "doc2.txt"}),
                Document(page_content="And a third dummy document 3.", metadata={"source": "doc3.txt"}),
            ]

    return DummyHybridRetriever() # type: ignore


def get_reranker() -> Reranker:
    # In a real application, this would fetch the reranker from a shared state or dependency injection
    # For now, we'll mock it up.
    print("Initializing Reranker (placeholder)...")
    # Placeholder for actual reranker initialization
    # Example: reranker = Reranker(model_name="...")
    class DummyReranker:
        def rerank(self, query: str, documents: List[Document], top_n: int = 5) -> List[Document]:
            print(f"DummyReranker reranking for query: {query}")
            # Simulate reranking by returning the documents as is or in a different order
            return documents[:top_n]

    return DummyReranker() # type: ignore


def get_token_budget_manager() -> TokenBudgetManager:
    # Placeholder for actual TokenBudgetManager initialization
    print("Initializing TokenBudgetManager (placeholder)...")
    # A real implementation would configure max_tokens and the tokenizer appropriately.
    # For this example, let's assume a simple tokenizer and a budget.
    # The tokenizer should match the one used by the LLM and embedding models.
    # For demonstration, we use a simple split by space.
    return TokenBudgetManager(max_tokens=1500, tokenizer=lambda text: text.split())


_rate_limiter_instance: Optional[RateLimiter] = None

def get_rate_limiter() -> RateLimiter:
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        print("Initializing RateLimiter (singleton)...")
        # Initialize the RateLimiter with desired parameters (matching the original values)
        _rate_limiter_instance = RateLimiter(requests_per_unit=60, unit_seconds=60)
    return _rate_limiter_instance

router = APIRouter(prefix="/api/v1/search", tags=["Search"], dependencies=[Depends(get_rate_limiter)])


from src.doc_intelligence.api.models import SearchRequest, SearchResponse, SearchResult


# API Endpoint
@router.post("/", response_model=SearchResponse)
async def search_endpoint(
    request: SearchRequest,
    http_request: Request,
    retriever: HybridRetriever = Depends(get_retriever),
    reranker: Reranker = Depends(get_reranker),
    token_budget_manager: TokenBudgetManager = Depends(get_token_budget_manager),
):
    """
    Performs a hybrid search, re-ranks the results, and optionally compresses context.

    Args:
        request: The search request object containing the query and parameters.
        retriever: The hybrid retriever instance.
        reranker: The reranker instance.
        token_budget_manager: The token budget manager instance.

    Returns:
        A SearchResponse containing the top-k search results.

    Raises:
        HTTPException: If the search or reranking process fails.
    """
    try:
        # Apply rate limiting
        # Rate limiting is applied via the router dependency; no explicit call needed here.

        # 1. Hybrid Search
        print(f"Performing hybrid search for query: {request.query}")
        retrieved_docs = retriever.search(query=request.query, k=request.rerank_top_n)
        if not retrieved_docs:
            return SearchResponse(results=[])

        # 2. Re-ranking
        print(f"Reranking {len(retrieved_docs)} documents...")
        reranked_docs = reranker.rerank(query=request.query, documents=retrieved_docs, top_n=request.k)

        # 3. Context Compression (if token count exceeds budget)
        # Calculate the total token count of the reranked documents
        total_tokens = sum(token_budget_manager.token_count(doc.page_content) for doc in reranked_docs)

        if total_tokens > token_budget_manager.max_tokens:
            print(f"Total tokens ({total_tokens}) exceed budget ({token_budget_manager.max_tokens}). Compressing context...")
            # If compression is needed, we need a way to compress.
            # For now, we'll just return the top k documents without compression if budget is exceeded,
            # as the compression logic is not yet implemented in the provided context.
            # A proper implementation would involve a context compression mechanism.
            # Example placeholder:
            # compressed_docs = context_compressor.compress(query=request.query, documents=reranked_docs)
            # This example assumes no specific compressor is available.
            # For the purpose of this endpoint, we will just return the top k results as is,
            # assuming the reranker has already selected the most relevant ones up to request.k.
            # If actual compression is required, a context compressor module/class needs to be integrated.
            print("Context compression not implemented in this version. Returning top K results as is.")
            # In a real scenario, you'd re-evaluate token count after compression and potentially truncate.
            final_docs = reranked_docs[:request.k] # Ensure we return at most k documents
        else:
            print("Token count within budget. No compression needed.")
            final_docs = reranked_docs[:request.k] # Ensure we return at most k documents

        # Prepare the final response
        search_results = [
            SearchResult(document=doc, score=0.0) for doc in final_docs # Score is not directly available from reranked_docs in this mock setup
        ]

        return SearchResponse(results=search_results)

    except Exception as e:
        from doc_intelligence.exceptions import RetrievalError, VectorStoreError, DocumentIntelligenceError
        print(f"An error occurred during search: {e}")
        if isinstance(e, RetrievalError):
            raise HTTPException(status_code=400, detail=str(e))
        elif isinstance(e, VectorStoreError):
            raise HTTPException(status_code=500, detail=str(e))
        elif isinstance(e, DocumentIntelligenceError):
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail="An error occurred during the search process.")
