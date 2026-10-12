from doc_intelligence.retrieval.token_budget_manager import TokenBudgetManager


class DummyTokenizer:
    def __call__(self, text: str) -> list[str]:
        if not text:
            return []
        return text.split()


def test_token_count():
    tokenizer = DummyTokenizer()
    manager = TokenBudgetManager(max_tokens=10, tokenizer=tokenizer)
    assert manager.token_count("hello world") == 2
    assert manager.token_count("") == 0


def test_manage_budget_fits_all():
    tokenizer = DummyTokenizer()
    manager = TokenBudgetManager(max_tokens=10, tokenizer=tokenizer)
    texts = ["one two", "three"]
    result = manager.manage_budget(texts)
    assert result == ["one two", "three"]


def test_manage_budget_partial_truncation():
    tokenizer = DummyTokenizer()
    manager = TokenBudgetManager(max_tokens=3, tokenizer=tokenizer)
    texts = ["one two", "three four five"]
    result = manager.manage_budget(texts)
    # First text takes 2 tokens. Remaining budget is 1 token.
    # Second text "three four five" gets truncated to fit 1 token -> "three"
    assert result == ["one two", "three"]


def test_manage_budget_zero_budget():
    tokenizer = DummyTokenizer()
    manager = TokenBudgetManager(max_tokens=0, tokenizer=tokenizer)
    texts = ["one two", "three"]
    result = manager.manage_budget(texts)
    assert result == []
