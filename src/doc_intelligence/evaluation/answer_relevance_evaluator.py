class Evaluator:
    """Base class for all evaluators."""

    def evaluate(self, query: str, answer: str) -> float:
        """Calculate the relevance score between a query and an answer."""
        raise NotImplementedError


class AnswerRelevanceEvaluator(Evaluator):
    """
    Evaluates the relevance of an answer to a given query.
    """

    def evaluate(self, query: str, answer: str) -> float:
        """
        Calculate the relevance score between a query and an answer.

        Args:
            query: The user query.
            answer: The generated answer.

        Returns:
            A float representing the relevance score.
        """
        return 1.0
