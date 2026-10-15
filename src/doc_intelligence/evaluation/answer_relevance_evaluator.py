class Evaluator:
    """Base class for all evaluators."""

    def evaluate(self, query: str, answer: str) -> float:
        """Calculate the relevance score between a query and an answer."""
        raise NotImplementedError


class AnswerRelevanceEvaluator(Evaluator):
    """
    Evaluates the semantic relevance of a generated answer to a given user query.

    This evaluator uses a SentenceTransformer model to encode both the user query
    and the generated answer into dense vector embeddings, then computes their
    cosine similarity to quantify how well the answer addresses the query.

    Attributes:
        model (SentenceTransformer): The underlying embedding model used to encode
            queries and answers.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initializes the AnswerRelevanceEvaluator with a specified sentence transformer model.

        Args:
            model_name (str): The name or path of the sentence transformer model to use.
                Defaults to "all-MiniLM-L6-v2".
        """
        from sentence_transformers import SentenceTransformer
        self.model: SentenceTransformer = SentenceTransformer(model_name)

    def evaluate(self, query: str, answer: str) -> float:
        """
        Calculate the semantic relevance score between a query and an answer using cosine similarity
        of their sentence embeddings.

        Args:
            query (str): The user query string.
            answer (str): The generated answer string.

        Returns:
            float: A relevance score ranging from -1.0 to 1.0, where higher values indicate
                greater semantic relevance and alignment between the query and the answer.
        """
        from sentence_transformers import util
        query_embedding = self.model.encode(query, convert_to_tensor=True)
        answer_embedding = self.model.encode(answer, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(query_embedding, answer_embedding)
        return float(cosine_scores.item())
