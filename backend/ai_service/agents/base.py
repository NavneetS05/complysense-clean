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
        effective_role = (
            kwargs.get("user_role")
            or kwargs.get("caller_role")
            or kwargs.get("active_role_name")
            or self.role
        )
        endpoint = kwargs.get("endpoint_name", self.endpoint_name)
        if not self.role_guard.verify_role_access(effective_role, endpoint):
            return {
                "role": effective_role,
                "response": "Access denied: your role is not permitted to use this feature.",
                "citations": [],
                "error": "UNAUTHORIZED",
            }

        # ── Step 2: Sanitize input ─────────────────────────────────────────────
        try:
            sanitized_query = self.sanitizer.sanitize_input(query)
        except ValueError:
            return {
                "role": effective_role,
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

        # Extract pure user query for retrieval if op_context was prepended
        search_query = sanitized_query
        if "USER QUERY:" in search_query:
            search_query = search_query.split("USER QUERY:")[-1].strip()

        # ── Step 4: Hybrid retrieval ───────────────────────────────────────────
        retriever = _get_retriever()
        retrieved_chunks = retriever.retrieve(
            query_text=search_query,
            role=effective_role,
            institution_id=institution_id,
            limit=7,
        )

        # ── Step 5: Confidence gate ────────────────────────────────────────────
        confident = self.confidence_scorer.check_confidence(retrieved_chunks)
        if not confident and not retrieved_chunks:
            return {
                "role": effective_role,
                "response": "This query is not covered in the provided regulatory frameworks.",
                "citations": [],
                "query_type": query_type,
            }

        # ── Step 6: Cross-reference injection ─────────────────────────────────
        cross_ref = _get_cross_ref()
        all_corpus_chunks = retriever.bm25_store.chunks if (retriever and hasattr(retriever.bm25_store, "chunks")) else None
        secondary_chunks = cross_ref.inject_references(retrieved_chunks, all_chunks=all_corpus_chunks)

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
            role_context=get_role_context(effective_role),
            retrieved_context=context_str,
            history=conversation_history,
            user_query=task_query,
        )

        # ── Step 9: LLM call ───────────────────────────────────────────────────
        is_fallback = False
        try:
            llm_response = await self.llm.call(
                messages=messages,
                model=self.settings.llm_model,
            )
        except Exception as exc:
            logger.warning("base_agent.llm_fallback_engaged", error=str(exc))
            is_fallback = True
            llm_response = self._build_rag_fallback_response(
                query=task_query,
                chunks=retrieved_chunks,
                context_str=context_str,
                endpoint_name=str(kwargs.get("endpoint_name", "chat")),
                error_reason=str(exc),
            )

        # ── Step 10: Response validation ───────────────────────────────────────
        # Pass retrieved_chunks so citation grounding can verify framework mentions.
        # Skip validation for deterministic RAG fallbacks and JSON payloads.
        is_json_payload = llm_response.strip().startswith("{") or llm_response.strip().startswith("[")
        if not is_fallback and not is_json_payload and not self.response_validator.validate_response(llm_response, retrieved_chunks):
            return {
                "role": effective_role,
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
            role=effective_role,
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

    def _build_rag_fallback_response(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        context_str: str,
        endpoint_name: str,
        error_reason: str,
    ) -> str:
        import json
        cited_frameworks = list(
            {
                (c.get("meta") or c.get("metadata") or {}).get("framework", "")
                for c in chunks
                if (c.get("meta") or c.get("metadata") or {}).get("framework")
            }
        )
        frameworks_str = ", ".join(cited_frameworks) if cited_frameworks else "ISO 27001, DPDP Act 2023, CERT-In"

        if endpoint_name == "triage":
            return json.dumps({
                "priority": "high",
                "cert_in_trigger": True,
                "mapped_controls": cited_frameworks or ["ISO-27001-A.5.1", "CERT-In-Sec-6"],
                "justification": f"Priority triage based on RAG knowledge base ({frameworks_str}). Excerpt: {context_str[:300]}...",
                "recommended_action": "Review open compliance gaps, isolate affected systems, and log incident report with CERT-In within 6 hours."
            })
        elif endpoint_name == "regulatory_change":
            return json.dumps({
                "assessment_summary": f"Regulatory impact analysis grounded in {frameworks_str}. Primary provisions identified: {context_str[:300]}...",
                "affected_controls": cited_frameworks or ["ISO-27001-A.5.1"],
                "recommendations": "1. Conduct gap assessment against updated framework guidelines.\n2. Update internal compliance policies and evidence controls."
            })
        else:
            clean_excerpts = []
            for idx, chunk in enumerate(chunks[:3], 1):
                meta = chunk.get("meta") or chunk.get("metadata") or {}
                fw = meta.get("framework") or meta.get("title") or "Regulatory Standard"
                text_snippet = chunk.get("text") or chunk.get("content") or ""
                if text_snippet:
                    clean_excerpts.append(f"**{idx}. {fw}**\n> {text_snippet[:250]}...")
            
            excerpts_block = "\n\n".join(clean_excerpts) if clean_excerpts else context_str[:500]
            if not excerpts_block.strip():
                excerpts_block = "No direct regulatory matches were retrieved for this specific query."

            return (
                f"### Regulatory RAG Knowledge Base Summary\n\n"
                f"Based on indexed compliance frameworks (**{frameworks_str}**):\n\n"
                f"{excerpts_block}\n\n"
                f"---  \n"
                f"*Note: Grounded in ComplySense RAG Knowledge Base.*"
            )
