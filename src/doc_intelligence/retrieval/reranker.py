from typing import List, Tuple

from sentence_transformers import SentenceTransformer

class Reranker:
    """
    Re-ranks a list of candidate documents based on their relevance to a query.

    This class uses a SentenceTransformer model to compute similarity scores
    between the query and each candidate document. It then returns the top_k
    candidates sorted by these new scores.

    Attributes:
        model (SentenceTransformer): The SentenceTransformer model used for re-ranking.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the Reranker with a specified SentenceTransformer model.

        Args:
            model_name (str): The name of the SentenceTransformer model to load.
                              Defaults to "all-MiniLM-L6-v2".
        """
        self.model = SentenceTransformer(model_name)

    def rerank(self, query: str, candidates: List[Tuple[str, str, float]], top_k: int) -> List[Tuple[str, str, float]]:
        """
        Re-ranks a list of candidate documents and returns the top_k results.

        Args:
            query (str): The search query.
            candidates (List[Tuple[str, str, float]]): A list of candidate documents,
                where each candidate is a tuple containing (doc_id, doc_content, original_score).
            top_k (int): The number of top candidates to return.

        Returns:
            List[Tuple[str, str, float]]: A list of the top_k re-ranked candidates,
                sorted by their new similarity scores in descending order.
        """
        if not candidates:
            return []

        candidate_contents = [content for _, content, _ in candidates]
        query_embedding = self.model.encode(query)
        candidate_embeddings = self.model.encode(candidate_contents)

        from sentence_transformers import util

        # Compute cosine similarity scores
        similarity_scores = util.cos_sim(query_embedding, candidate_embeddings)[0].tolist()

        # Combine original candidate info with new scores
        reranked_candidates = []
        for i, (doc_id, doc_content, _) in enumerate(candidates):
            reranked_candidates.append((doc_id, doc_content, similarity_scores[i]))

        # Sort candidates by the new similarity scores in descending order
        reranked_candidates.sort(key=lambda x: x[2], reverse=True)

        return reranked_candidates[:top_k]
