# Use: Builds the final prompt (system + role + history + retrieved chunks + task).

from typing import List, Dict, Any


class PromptBuilder:
    def build_prompt(
        self,
        system_prompt: str,
        role_context: str,
        history: List[Dict[str, str]],
        context_text: str,
        task_prompt: str,
        user_query: str
    ) -> str:
        """
        Assembles all segments of the system instructions, role context, retrieved chunks,
        history, and current query into a single string prompt.
        """
        return ""
