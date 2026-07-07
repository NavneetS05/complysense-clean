# Use: Base agent implementing the shared RAG orchestration flow.
# Updated: citation extraction uses 'meta' key; validator receives retrieved_chunks.

from typing import Any, Dict, List

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger
from ai_service.security.sanitizer import InputSanitizer
from ai_service.security.guards import RoleGuard
from ai_service.rag.retrieval.hybrid_retriever import HybridRetriever
from ai_service.rag.retrieval.cross_reference import CrossReferenceInjector
from ai_service.rag.retrieval.context_builder import ContextBuilder
from ai_service.rag.retrieval.confidence import ConfidenceScorer
from ai_service.rag.retrieval.query_classifier import QueryClassifier
from ai_service.rag.generation.prompt_builder import PromptBuilder
from ai_service.rag.generation.response_validator import ResponseValidator
from ai_service.utils.llm import LLMService
from ai_service.prompts.system import BASE_SYSTEM
from ai_service.prompts.role_contexts import get_role_context

logger = StructuredLogger("ai_service.agents.base")

# ── Process-level singletons ──────────────────────────────────────────────────
# Initialised once and reused across all agent instantiations.
_retriever: HybridRetriever | None = None
_cross_ref: CrossReferenceInjector | None = None


def _get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def _get_cross_ref() -> CrossReferenceInjector:
    global _cross_ref
    if _cross_ref is None:
        _cross_ref = CrossReferenceInjector()
    return _cross_ref


class BaseAgent:
    """
    Orchestrates the full RAG pipeline for every agent role:
    1.  Role authorization (RoleGuard)
    2.  Input sanitization (InputSanitizer)
    3.  Query classification (QueryClassifier)
    4.  Hybrid retrieval — FAISS + BM25 + RRF (HybridRetriever singleton)
    5.  Confidence gate (ConfidenceScorer)
    6.  Cross-reference injection (CrossReferenceInjector)
    7.  Context assembly (ContextBuilder)
    8.  Prompt construction (PromptBuilder)
    9.  LLM call (Gemini 2.5 Flash via LLMService)
    10. Response validation — jailbreak + citation grounding (ResponseValidator)
    11. Return structured dict.
    """

    def __init__(self, role: str, endpoint_name: str = "chat") -> None:
        self.role = role
        self.endpoint_name = endpoint_name
        self.settings = get_ai_settings()
        self.sanitizer = InputSanitizer()
        self.role_guard = RoleGuard()
        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()
        self.response_validator = ResponseValidator()
        self.confidence_scorer = ConfidenceScorer(threshold=self.settings.similarity_threshold)
        self.query_classifier = QueryClassifier()
        self.llm = LLMService(api_key=self.settings.gemini_api_key)

    async def execute(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
        task_prompt: str = "",
        extra_context: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Runs the full RAG orchestration pipeline.

        Returns a dict with keys:
            role, response, citations, query_type, chunks_used
        On error: additionally includes 'error' key.
        """
        # ── Step 1: Role authorization ─────────────────────────────────────────
        endpoint = kwargs.get("endpoint_name", self.endpoint_name)
        if not self.role_guard.verify_role_access(self.role, endpoint):
            return {
                "role": self.role,
                "response": "Access denied: your role is not permitted to use this feature.",
                "citations": [],
                "error": "UNAUTHORIZED",
            }

        # ── Step 2: Sanitize input ─────────────────────────────────────────────
        try:
            sanitized_query = self.sanitizer.sanitize_input(query)
        except ValueError:
            return {
                "role": self.role,
                "response": (
                    "Your request could not be processed: it contains patterns "
                    "flagged for security review."
                ),
                "citations": [],
                "error": "INJECTION_BLOCKED",
            }

        wrapped_extra = ""
        if extra_context:
            try:
                wrapped_extra = self.sanitizer.wrap_external_content(extra_context)
            except ValueError:
                wrapped_extra = ""

        # ── Step 3: Classify query ─────────────────────────────────────────────
        query_type = self.query_classifier.classify_query(sanitized_query)

        # ── Step 4: Hybrid retrieval ───────────────────────────────────────────
        retriever = _get_retriever()
        retrieved_chunks = retriever.retrieve(
            query_text=sanitized_query,
            role=self.role,
            institution_id=institution_id,
            limit=7,
        )

        # ── Step 5: Confidence gate ────────────────────────────────────────────
        confident = self.confidence_scorer.check_confidence(retrieved_chunks)
        if not confident and not retrieved_chunks:
            return {
                "role": self.role,
                "response": "This query is not covered in the provided regulatory frameworks.",
                "citations": [],
                "query_type": query_type,
            }

        # ── Step 6: Cross-reference injection ─────────────────────────────────
        cross_ref = _get_cross_ref()
        secondary_chunks = cross_ref.inject_references(retrieved_chunks)

        # ── Step 7: Context assembly ───────────────────────────────────────────
        context_str = self.context_builder.build_context(
            primary_chunks=retrieved_chunks,
            secondary_chunks=secondary_chunks,
            max_tokens=self.settings.max_input_tokens,
        )
        if wrapped_extra:
            context_str = f"{context_str}\n\nUSER-SUBMITTED DOCUMENT:\n{wrapped_extra}"

        # ── Step 8: Prompt construction ────────────────────────────────────────
        task_query = (
            f"{task_prompt}\n\n{sanitized_query}".strip() if task_prompt else sanitized_query
        )
        messages = self.prompt_builder.build_prompt(
            system_prompt=BASE_SYSTEM,
            role_context=get_role_context(self.role),
            retrieved_context=context_str,
            history=conversation_history,
            user_query=task_query,
        )

        # ── Step 9: LLM call ───────────────────────────────────────────────────
        try:
            llm_response = await self.llm.call(
                messages=messages,
                model=self.settings.llm_model,
            )
        except Exception as exc:
            logger.error("base_agent.llm_error", error=str(exc))
            return {
                "role": self.role,
                "response": f"AI service error: {exc}",
                "citations": [],
                "error": "LLM_ERROR",
            }

        # ── Step 10: Response validation ───────────────────────────────────────
        # Pass retrieved_chunks so citation grounding can verify framework mentions.
        if not self.response_validator.validate_response(llm_response, retrieved_chunks):
            return {
                "role": self.role,
                "response": (
                    "The AI-generated response was blocked by safety filters. "
                    "Please rephrase your query."
                ),
                "citations": [],
                "error": "VALIDATION_FAILED",
            }

        # ── Step 11: Build citation list ───────────────────────────────────────
        # Chunks now carry metadata under 'meta'; 'metadata' is the legacy key.
        cited_frameworks = list(
            {
                (c.get("meta") or c.get("metadata") or {}).get("framework", "")
                for c in retrieved_chunks
                if (c.get("meta") or c.get("metadata") or {}).get("framework")
            }
        )

        logger.info(
            "base_agent.response_generated",
            role=self.role,
            query_type=query_type,
            chunks_used=len(retrieved_chunks),
            citations=cited_frameworks,
        )

        return {
            "role": self.role,
            "response": llm_response,
            "citations": cited_frameworks,
            "query_type": query_type,
            "chunks_used": len(retrieved_chunks),
        }
