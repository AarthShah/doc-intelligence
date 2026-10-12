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

    def _truncate_to_budget(self, text: str, remaining: int) -> str:
        """Truncate a single text so that its token count does not exceed remaining tokens."""
        if remaining <= 0:
            return ""
        tokens = self.tokenizer(text)
        if len(tokens) <= remaining:
            return text
        truncated_tokens = tokens[:remaining]
        return " ".join(truncated_tokens)

    def truncate(self, texts: List[str]) -> List[str]:
        """Iteratively adds texts while total token count <= max_tokens, truncating the last text if necessary."""
        result = []
        current_tokens = 0

        for text in texts:
            t_count = self.token_count(text)
            if current_tokens + t_count <= self.max_tokens:
                result.append(text)
                current_tokens += t_count
            else:
                remaining = self.max_tokens - current_tokens
                if remaining > 0:
                    truncated_text = self._truncate_to_budget(text, remaining)
                    if truncated_text:
                        result.append(truncated_text)
                break

        return result
