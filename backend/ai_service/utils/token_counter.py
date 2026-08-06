# Use: Counts prompt and completion tokens for budgeting and analytics.

from typing import List, Dict
import tiktoken


class TokenCounter:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            try:
                self.encoding = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoding = None

    def count_tokens(self, text: str) -> int:
        """
        Returns an approximate token count for the given text.
        Uses tiktoken under the hood when available, falls back to word-based estimate.
        """
        if not text:
            return 0
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception:
                pass
        # Fallback to word-based estimate (approx 1.33 tokens per word)
        return int(len(text.split()) * 1.33)

    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Returns the total token count across a list of chat messages.
        """
        return sum(self.count_tokens(m.get("content", "")) for m in messages)

    def fits_within_budget(self, prompt: str, max_tokens: int = 3200) -> bool:
        """
        Returns True if the prompt is within the allowed input token budget.
        """
        return self.count_tokens(prompt) <= max_tokens

