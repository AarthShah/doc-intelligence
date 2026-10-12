from typing import Callable, List


class TokenBudgetManager:
    """
    Manages prompt token budgets and optimizes context window limits with dynamic truncation.

    This manager ensures that a list of context texts fits within a specified maximum token budget
    by retaining as many full texts as possible and truncating the final fitting text if necessary.

    Attributes:
        max_tokens (int): The maximum allowed number of tokens for the combined texts.
        tokenizer (Callable[[str], List[str]]): A callable that splits a string into a list of token strings.

    Example:
        >>> whitespace_tokenizer = lambda text: text.split()
        >>> manager = TokenBudgetManager(max_tokens=5, tokenizer=whitespace_tokenizer)
        >>> texts = ["Hello world", "this is a test prompt"]
        >>> manager.truncate(texts)
        ['Hello world', 'this is']
    """

    def __init__(self, max_tokens: int, tokenizer: Callable[[str], List[str]]) -> None:
        """
        Initialize the TokenBudgetManager.

        Args:
            max_tokens (int): The maximum token budget allowed.
            tokenizer (Callable[[str], List[str]]): A function or callable to tokenize text.
        """
        self.max_tokens = max_tokens
        self.tokenizer = tokenizer

    def token_count(self, text: str) -> int:
        """
        Return the number of tokens in the given text using the configured tokenizer.

        Args:
            text (str): The text string to count tokens for.

        Returns:
            int: The total number of tokens.

        Example:
            >>> manager = TokenBudgetManager(max_tokens=10, tokenizer=lambda t: t.split())
            >>> manager.token_count("Hello world")
            2
        """
        return len(self.tokenizer(text))

    def _truncate_to_budget(self, text: str, remaining: int) -> str:
        """
        Truncate a single text so that its token count does not exceed the remaining token budget.

        Args:
            text (str): The text string to truncate.
            remaining (int): The maximum number of tokens allowed for this text.

        Returns:
            str: The truncated text joined by single spaces.

        Example:
            >>> manager = TokenBudgetManager(max_tokens=10, tokenizer=lambda t: t.split())
            >>> manager._truncate_to_budget("Hello beautiful world", remaining=2)
            'Hello beautiful'
        """
        if remaining <= 0:
            return ""
        tokens = self.tokenizer(text)
        if len(tokens) <= remaining:
            return text
        truncated_tokens = tokens[:remaining]
        return " ".join(truncated_tokens)

    def truncate(self, texts: List[str]) -> List[str]:
        """
        Iteratively add texts while total token count is within max_tokens, truncating the last text if necessary.

        Args:
            texts (List[str]): A list of text strings to process and fit into the budget.

        Returns:
            List[str]: A filtered and potentially truncated list of texts fitting within max_tokens.

        Example:
            >>> manager = TokenBudgetManager(max_tokens=4, tokenizer=lambda t: t.split())
            >>> manager.truncate(["alpha beta", "gamma delta epsilon"])
            ['alpha beta', 'gamma delta']
        """
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
