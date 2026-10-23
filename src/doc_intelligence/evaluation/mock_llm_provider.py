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

    def __init__(self, prompt_response_map: Optional[Dict[str, str]] = None):
        """
        Initializes the MockLLMProvider with a mapping of prompts to responses.

        Args:
            prompt_response_map (Optional[Dict[str, str]]): A dictionary containing predefined prompt-response pairs.
                                                           Defaults to None.
        """
        self._initial_responses = prompt_response_map if prompt_response_map is not None else {}
        self._responses = self._initial_responses.copy()


    def reset(self) -> None:
        """Clears all predefined prompt-response mappings."""
        self._responses = self._initial_responses.copy()

    def __call__(self, prompt: str, **kwargs) -> str:
        """
        Allows the provider instance to be called directly as a function.

        Args:
            prompt (str): The input prompt to the LLM.
            **kwargs: Additional optional arguments.

        Returns:
            str: The predefined response corresponding to the prompt.
        """
        return self.generate_response(prompt, **kwargs)

    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generates a response based on the input prompt using the predefined map.

        Args:
            prompt (str): The input prompt to the LLM.
            **kwargs: Additional optional arguments.

        Returns:
            str: The predefined response corresponding to the prompt.

        Raises:
            KeyError: If the prompt is not found in the prompt-response map.
        """
        if prompt not in self._responses:
            raise KeyError(f"Prompt not found in mock provider: {prompt}")
        return self._responses[prompt]
