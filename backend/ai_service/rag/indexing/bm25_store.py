# Use: Builds and persists the sparse BM25 keyword index.
# Updated: structured logging; search returns chunks with 'meta' key (consistent with FAISS store).

import os
import pickle
from typing import Any, Dict, List

from rank_bm25 import BM25Okapi

from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.indexing.bm25_store")


class BM25IndexStore:
    """
    Wraps BM25Okapi to provide consistent sparse retrieval.

    On-disk file: <persist_path>/bm25.pkl — pickled dict with 'index' and 'chunks'.
    Chunks follow the same schema as FAISSIndexStore items: {"text": str, "meta": dict}.
    """

    def __init__(self, persist_path: str) -> None:
        self.persist_path = persist_path
        self.index: BM25Okapi | None = None
        self.chunks: List[Dict[str, Any]] = []

    # ── Build & Persist ────────────────────────────────────────────────────────

    def build_and_save(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Tokenizes chunk texts, builds BM25Okapi index, and serializes to disk.
        """
        if not chunks:
            logger.warning("bm25_store.empty_input")
            return

        self.chunks = chunks
        tokenized_corpus = [self._tokenize(c.get("text", "")) for c in chunks]
        self.index = BM25Okapi(tokenized_corpus)

        file_path = self._pkl_path()
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump({"index": self.index, "chunks": self.chunks}, f)

        logger.info("bm25_store.built", chunks=len(chunks), path=file_path)

    # ── Load ──────────────────────────────────────────────────────────────────

    def load_index(self) -> None:
        """
        De-serializes the BM25 index and chunks from disk.
        Raises RuntimeError if the file is missing.
        """
        file_path = self._pkl_path()
        if not os.path.exists(file_path):
            raise RuntimeError(f"BM25 index file missing: {file_path}")

        with open(file_path, "rb") as f:
            data = pickle.load(f)

        self.index = data["index"]
        self.chunks = data["chunks"]
        logger.info("bm25_store.loaded", chunks=len(self.chunks), path=file_path)

    # ── Search ────────────────────────────────────────────────────────────────

    def search(self, query_text: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Tokenizes query, scores all chunks, and returns the top_k results
        with a root-level 'score' key attached (consistent with FAISSIndexStore).
        """
        if not self.index or not self.chunks:
            return []

        query_tokens = self._tokenize(query_text)
        scores = self.index.get_scores(query_tokens)

        results: List[Dict[str, Any]] = []
        for idx, score in enumerate(scores):
            if score > 0:
                chunk = dict(self.chunks[idx])
                chunk["score"] = float(score)
                results.append(chunk)

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    # ── Private ────────────────────────────────────────────────────────────────

    def _tokenize(self, text: str) -> List[str]:
        if not text:
            return []
        return [t.lower() for t in text.split() if t.isalnum()]

    def _pkl_path(self) -> str:
        if self.persist_path.endswith(".pkl"):
            return self.persist_path
        return os.path.join(self.persist_path, "bm25.pkl")
