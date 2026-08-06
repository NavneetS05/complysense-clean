# Use: Performs BM25 + FAISS retrieval with RRF merge, role-gated framework filtering.
# Key fix: indices are loaded ONCE at lifespan startup and kept in memory.
# reload_indices() is only called by admin /reindex endpoint after a rebuild.

from typing import List, Dict, Any

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger
from ai_service.utils.constants import ROLE_FRAMEWORKS
from ai_service.rag.indexing.embeddings import EmbeddingsGenerator
from ai_service.rag.indexing.faiss_store import FAISSIndexStore
from ai_service.rag.indexing.bm25_store import BM25IndexStore
from ai_service.rag.retrieval.rrf import ReciprocalRankFusion

logger = StructuredLogger("ai_service.rag.retrieval.hybrid_retriever")


class HybridRetriever:
    """
    Stateful in-memory retriever.

    Important: instantiating HybridRetriever does NOT load the indices.
    Call reload_indices() explicitly (done once in main.py lifespan and again
    after admin /reindex). This prevents the 2+ minute index-reload penalty
    that was happening on every request in the previous implementation.
    """

    def __init__(self) -> None:
        settings = get_ai_settings()
        self.settings = settings
        # EmbeddingsGenerator is a singleton (model loaded once across all instances)
        self.embeddings = EmbeddingsGenerator(model_name=settings.embeddings_model)
        self.faiss_store = FAISSIndexStore(settings.vectorstore_path)
        self.bm25_store = BM25IndexStore(settings.vectorstore_path)
        self.rrf = ReciprocalRankFusion(k=60)
        self._loaded = False

    # ── Index management ───────────────────────────────────────────────────────

    def reload_indices(self) -> None:
        """
        Loads FAISS and BM25 indices from disk into memory.
        Called once during lifespan startup, and once after admin /reindex.
        """
        try:
            self.faiss_store.load_index()
            self.bm25_store.load_index()
            self._loaded = True
            logger.info(
                "hybrid_retriever.indices_loaded",
                faiss_items=len(self.faiss_store.items),
                bm25_chunks=len(self.bm25_store.chunks),
            )
        except Exception as exc:
            self._loaded = False
            logger.warning(
                "hybrid_retriever.load_failed",
                error=str(exc),
                detail="Service will operate in degraded mode until indices are built.",
            )

    # ── Retrieval ──────────────────────────────────────────────────────────────

    def retrieve(
        self,
        query_text: str,
        role: str,
        institution_id: str | None = None,
        limit: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top-K relevant chunks using Hybrid BM25 + FAISS search with RRF merge.

        Args:
            query_text: sanitized user query string.
            role: active role name (used to gate framework access).
            institution_id: used to enforce tenant isolation for user-uploaded docs.
            limit: maximum number of chunks to return to the caller.

        Returns:
            List of chunk dicts each carrying both 'text' and 'meta' keys.
        """
        if not self._loaded or self.faiss_store.index is None or not self.bm25_store.index:
            logger.warning(
                "hybrid_retriever.not_ready",
                detail="Indices not loaded. Returning empty results.",
            )
            return []

        # ── Dense retrieval ────────────────────────────────────────────────────
        query_embedding = self.embeddings.embed_query(query_text)
        dense_hits = self.faiss_store.search(query_embedding, top_k=20)

        # Convert (idx, score) pairs to chunk dicts with score attached
        dense_results: List[Dict[str, Any]] = []
        for idx, score in dense_hits:
            if idx < len(self.faiss_store.items):
                chunk = dict(self.faiss_store.items[idx])
                chunk["score"] = score           # real cosine similarity [0,1]
                dense_results.append(chunk)

        # ── Sparse retrieval ───────────────────────────────────────────────────
        sparse_results = self.bm25_store.search(query_text, top_k=20)

        # ── Role-based access filter ───────────────────────────────────────────
        # Normalize role key (e.g. "Compliance Officer" -> "compliance_officer")
        role_key = role.lower().replace(" ", "_")
        permitted_frameworks = ROLE_FRAMEWORKS.get(role_key) or ROLE_FRAMEWORKS.get(role, [])

        def _is_permitted(chunk: Dict[str, Any]) -> bool:
            meta = chunk.get("meta", chunk.get("metadata", {}))
            source = meta.get("source")

            # User-uploaded docs: enforce tenant isolation
            if source == "user_upload":
                chunk_inst_id = meta.get("institution_id")
                return chunk_inst_id is not None and str(chunk_inst_id) == str(institution_id)

            # Framework docs: enforce role access matrix
            fw = str(meta.get("framework") or "").strip().upper()
            if not fw:
                return True

            if not permitted_frameworks:
                return True

            for p in permitted_frameworks:
                p_upper = p.strip().upper()
                p_token = p_upper.split()[0]
                if p_upper in fw or fw in p_upper or p_token in fw:
                    return True

            return False

        filtered_dense = [c for c in dense_results if _is_permitted(c)]
        filtered_sparse = [c for c in sparse_results if _is_permitted(c)]

        # ── RRF merge ──────────────────────────────────────────────────────────
        merged = self.rrf.merge_rankings(filtered_dense, filtered_sparse)

        logger.info(
            "hybrid_retriever.retrieved",
            dense=len(filtered_dense),
            sparse=len(filtered_sparse),
            merged=len(merged),
            returned=min(limit, len(merged)),
        )

        return merged[:limit]
