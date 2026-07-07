# Use: Generation-layer response validation wrapper.
# Consolidates jailbreak + citation checks via OutputValidator.
# CitationValidator is now redundant (logic merged into OutputValidator) — kept for legacy compat.

from typing import Any, Dict, List

from ai_service.security.response_validator import OutputValidator
from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.generation.response_validator")


class ResponseValidator:
    """
    Validates LLM output before it is returned to the caller.

    Checks (via OutputValidator):
    1. Jailbreak indicator patterns in the response text.
    2. Fabricated citations — frameworks referenced but not in retrieved chunks.
    """

    def __init__(self) -> None:
        self.output_validator = OutputValidator()

    def validate_response(
        self,
        response_text: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> bool:
        """
        Returns True if the response passes all safety and grounding checks.
        """
        passed = self.output_validator.validate_safety(
            output_text=response_text,
            retrieved_chunks=retrieved_chunks,
        )
        if not passed:
            logger.warning(
                "response_validator.blocked",
                chunks_count=len(retrieved_chunks),
            )
        return passed
