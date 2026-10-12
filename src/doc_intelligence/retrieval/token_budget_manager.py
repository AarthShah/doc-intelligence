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

    def _truncate_to_budget(self, text: str, remaining_tokens: int) -> str:
        """Truncate a single text so that its token count does not exceed remaining_tokens."""
        tokens = self.tokenizer(text)
        if len(tokens) <= remaining_tokens:
            return text
        if remaining_tokens <= 0:
            return ""
        # Assuming tokenizer returns a list of token strings or objects that can be joined or sliced
        # If tokenizer returns strings, joining them back or slicing list depending on tokenizer behavior.
        # Typically tokenizers return List[str] or List[int]. Since tokenizer signature is Callable[[str], List[str]]:
        truncated_tokens = tokens[:remaining_tokens]
        # If tokens are string representations, we can join them or if they are words/characters.
        # Let's check how other parts handle it or join with empty string or space if needed.
        # Usually joining with empty or space depends on token type, but joining with empty string is standard for subword tokenizers.
        return "".join(truncated_tokens)

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
