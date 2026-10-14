from typing import List, Any, Callable

# Assume a base Evaluator class exists with an 'evaluate' method.
# For this implementation, we'll define it implicitly.
class Evaluator:
    def evaluate(self, **kwargs) -> float:
        raise NotImplementedError

class FaithfulnessEvaluator(Evaluator):
    """
    Evaluates the faithfulness of an answer to a given context in a RAG pipeline.

    Faithfulness measures whether the generated answer is factually supported
    by the provided retrieved context, preventing hallucinations and ensuring
    that claims made in the answer stem directly from the retrieved sources.

    Attributes:
        llm_client (Callable[..., str]): A callable client used to query an LLM
            with formatted evaluation prompts.

    Example:
        >>> def mock_llm(prompt: str) -> str:
        ...     return "0.95"
        >>> evaluator = FaithfulnessEvaluator(llm_client=mock_llm)
        >>> score = evaluator.evaluate(
        ...     question="What is the capital of France?",
        ...     context="France is a country in Europe. Its capital is Paris.",
        ...     answer="The capital of France is Paris."
        ... )
        >>> print(score)
        0.95
    """

    def __init__(self, llm_client: Callable[..., str]):
        """
        Initializes the FaithfulnessEvaluator with an LLM client.

        Args:
            llm_client (Callable[..., str]): A callable that simulates an LLM, accepting a prompt
                string and returning a generated string response containing the evaluation score.
        """
        self.llm_client = llm_client

    def evaluate(self, question: str, context: str, answer: str) -> float:
        """
        Evaluates the factual faithfulness of the generated answer against the retrieved context.

        Constructs an evaluation prompt combining the question, context, and answer, queries
        the language model via the LLM client, and parses the resulting score. The score is
        clamped between 0.0 and 1.0.

        Args:
            question (str): The original user query or question.
            context (str): The retrieved text context used to ground the generation.
            answer (str): The generated answer produced by the RAG system.

        Returns:
            float: A score between 0.0 and 1.0, where 1.0 indicates that the answer is fully
            supported by the context and 0.0 indicates complete lack of support or hallucination.
            Returns 0.0 if the LLM response cannot be successfully parsed as a float.
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
