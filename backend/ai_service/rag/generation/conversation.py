# Use: Manages conversation history, trimming and token-aware context inclusion.

from typing import List, Dict


class ConversationManager:
    def __init__(self, limit: int = 6):
        self.limit = limit

    def get_trimmed_history(self, history: List[Dict[str, str]], max_tokens: int) -> List[Dict[str, str]]:
        """
        Retrieves the latest turns from history, trimming dynamically based on max token limit.
        """
        return []
