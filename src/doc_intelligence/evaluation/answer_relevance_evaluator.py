class Evaluator:
    """Base class for all evaluators."""

    def evaluate(self, query: str, answer: str) -> float:
        """Calculate the relevance score between a query and an answer."""
        raise NotImplementedError


class AnswerRelevanceEvaluator(Evaluator):
    """
    Evaluates the relevance of an answer to a given query.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initializes the AnswerRelevanceEvaluator.

        Args:
            model_name: The name of the sentence transformer model to use.
                        Defaults to "all-MiniLM-L6-v2".
        """
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def evaluate(self, query: str, answer: str) -> float:
        """
        Calculate the relevance score between a query and an answer using cosine similarity
        of their embeddings.

        Args:
            query: The user query.
            answer: The generated answer.

        Returns:
            A float representing the relevance score, ranging from -1.0 to 1.0.
        """
        from sentence_transformers import util
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        answer_embedding = self.model.encode(answer, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(query_embedding, answer_embedding)
        return cosine_scores.item()
