from typing import List, Any, Callable

# Assume a base Evaluator class exists with an 'evaluate' method.
# For this implementation, we'll define it implicitly.
class Evaluator:
    def evaluate(self, **kwargs) -> float:
        raise NotImplementedError

class FaithfulnessEvaluator(Evaluator):
    """
    Evaluates the faithfulness of an answer to a given context.

    Faithfulness measures whether the generated answer is factually supported
    by the provided context.
    """

    def __init__(self, llm_client: Callable[..., str]):
        """
        Initializes the FaithfulnessEvaluator.

        Args:
            llm_client: A callable that simulates an LLM, accepting a prompt
                        and returning a generated string.
        """
        self.llm_client = llm_client

    def evaluate(self, question: str, context: str, answer: str) -> float:
        """
        Evaluates the faithfulness of the answer based on the context and question.

        Args:
            question: The original question asked.
            context: The retrieved context used to generate the answer.
            answer: The generated answer.

        Returns:
            A float score between 0 and 1, where 1 indicates perfect faithfulness.
        """
        prompt = f"""Given the following question and context, is the answer factually supported by the context?
Question: {question}
Context: {context}
Answer: {answer}

Respond with a score between 0 and 1, where 1 means the answer is fully supported by the context and 0 means it is not supported at all. Only provide the score.
"""
        try:
            response = self.llm_client(prompt)
            # Attempt to parse the response as a float.
            score = float(response.strip())
            # Clamp the score between 0 and 1.
            return max(0.0, min(1.0, score))
        except (ValueError, TypeError):
            # If parsing fails, return a default low score or handle as appropriate.
            # For now, returning 0.0 to indicate potential lack of faithfulness or an issue.
            return 0.0
