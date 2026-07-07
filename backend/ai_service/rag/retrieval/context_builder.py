# Use: Assembles final retrieval context while respecting token budget.

from typing import List, Dict, Any
from ai_service.utils.token_counter import TokenCounter


class ContextBuilder:
    def __init__(self):
        self.token_counter = TokenCounter()

    def build_context(
        self,
        primary_chunks: List[Dict[str, Any]],
        secondary_chunks: List[Dict[str, Any]],
        max_tokens: int = 3200
    ) -> str:
        """
        Assembles a formatted context string for LLM consumption, enforcing token budgets.
        Trims secondary context first if token budget is exceeded.
        """
        # A helper to render context string
        def _render(primaries: List[Dict[str, Any]], secondaries: List[Dict[str, Any]]) -> str:
            lines = ["REGULATORY CONTEXT:"]

            for chunk in primaries:
                meta = chunk.get("meta") or chunk.get("metadata") or {}
                fw = meta.get("framework", "Unknown")
                sec_id = meta.get("section_id", "N/A")
                title = meta.get("section_title", "")
                text = chunk.get("text", "")
                lines.append(f"--- {fw} | Section {sec_id} — {title} ---")
                lines.append(text)
                lines.append("")

            for chunk in secondaries:
                meta = chunk.get("meta") or chunk.get("metadata") or {}
                fw = meta.get("framework", "Unknown")
                sec_id = meta.get("section_id", "N/A")
                title = meta.get("section_title", "")
                text = chunk.get("text", "")
                lines.append(f"--- REFERENCED SECTION: {fw} | Section {sec_id} — {title} ---")
                lines.append(text)
                lines.append("")

            return "\n".join(lines)

        # First, try to render with all secondary chunks
        context_str = _render(primary_chunks, secondary_chunks)
        tokens = self.token_counter.count_tokens(context_str)
        
        # If over budget, trim secondary chunks one by one
        while tokens > max_tokens and secondary_chunks:
            secondary_chunks = secondary_chunks[:-1]
            context_str = _render(primary_chunks, secondary_chunks)
            tokens = self.token_counter.count_tokens(context_str)
            
        return context_str

