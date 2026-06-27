# Use: Base agent implementing the shared RAG orchestration flow.

from typing import Any, Dict, List


class BaseAgent:
    def __init__(self, role: str):
        self.role = role

    async def execute(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Executes the shared RAG orchestration flow:
        1. Sanitize the query text.
        2. Classify query type.
        3. Query the retriever to get relevant chunks.
        4. Inject cross-references.
        5. Build prompt with history, contexts, and task rules.
        6. Query LLM.
        7. Validate citations & response structure.
        """
        return {
            "role": self.role,
            "response": "Placeholder response",
            "citations": [],
        }
