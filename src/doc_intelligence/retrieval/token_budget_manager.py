from typing import Callable, List


class TokenBudgetManager:
    """
    Manages prompt token budgets and optimizes context window limits with dynamic truncation.
    """

    def __init__(self, max_tokens: int, tokenizer: Callable[[str], List[str]]) -> None:
        self.max_tokens = max_tokens
        self.tokenizer = tokenizer

    def token_count(self, text: str) -> int:
        """Return the number of tokens in the given text using the tokenizer."""
        return len(self.tokenizer(text))
