from typing import Dict, Callable, List, Optional

class MockLLMProvider:
    """
    A mock LLM provider for deterministic testing of evaluation metrics.

    This class simulates an LLM by returning predefined responses based on input prompts.
    It's initialized with a dictionary mapping prompts to their corresponding responses.

    Attributes:
        prompt_response_map (Dict[str, str]): A dictionary where keys are prompts and values
                                             are the predefined responses.
    """

    def __init__(self, prompt_response_map: Dict[str, str]):
        """
        Initializes the MockLLMProvider with a mapping of prompts to responses.

        Args:
            prompt_response_map (Dict[str, str]): A dictionary containing predefined prompt-response pairs.
        """
        self.prompt_response_map = prompt_response_map

    def generate(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """
        Generates a response based on the input prompt using the predefined map.

        Args:
            prompt (str): The input prompt to the LLM.
            stop (Optional[List[str]]): A list of stop sequences (currently ignored by this mock provider).

        Returns:
            str: The predefined response corresponding to the prompt, or a default message if the prompt is not found.
        """
        # In a real LLM, 'stop' sequences would be used to truncate generation.
        # For this mock, we directly return the mapped response.
        return self.prompt_response_map.get(prompt, "Mock response: Prompt not found.")
