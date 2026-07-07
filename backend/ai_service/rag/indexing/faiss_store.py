# Use: Builds, persists and loads dense FAISS vector index alongside pickled metadata.
# Replaces the LangChain wrapper with native faiss + numpy so retrieval scores are real cosine similarity.

import json
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import faiss
import numpy as np

from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.indexing.faiss_store")


class FAISSIndexStore:
    """
    Stores and retrieves dense FAISS embeddings alongside chunk metadata.

    On-disk layout under persist_path/:
      index.faiss   — binary FAISS flat Inner Product index
      index.pkl     — pickled list of chunk dicts (metadata + text)
      items.json    — JSON duplicate (human-readable; useful for debugging)
    """

    def __init__(self, persist_path: str):
        self.persist_path = Path(persist_path)
        self.items: List[Dict[str, Any]] = []
        self.index: Optional[faiss.Index] = None

    # ── Build & Persist ────────────────────────────────────────────────────────

    def build_and_save(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]],
    ) -> None:
        """
        Builds the FAISS Inner-Product index, normalizes vectors for cosine
        similarity, and persists both index and metadata to disk.
        """
        if not chunks or not embeddings:
            logger.warning("faiss_store.empty_input", chunks=len(chunks), embeddings=len(embeddings))
            return

        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunk count ({len(chunks)}) and embedding count ({len(embeddings)}) must match."
            )

        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.items = chunks

        # 1. Persist metadata
        with open(self.persist_path / "index.pkl", "wb") as f:
            pickle.dump(chunks, f)

        # JSON sidecar for debugging (best-effort)
        try:
            (self.persist_path / "items.json").write_text(
                json.dumps(chunks, ensure_ascii=False, default=str), encoding="utf-8"
            )
        except Exception:
            pass

        # 2. Build binary FAISS index
        vecs = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(vecs)           # Normalize for cosine similarity via Inner Product
        dim = vecs.shape[1]
        index = faiss.IndexFlatIP(dim)     # IndexFlatIP + normalized vecs == cosine similarity
        index.add(vecs)

        faiss.write_index(index, str(self.persist_path / "index.faiss"))
        self.index = index

        logger.info(
            "faiss_store.built",
            path=str(self.persist_path),
            chunks=len(chunks),
            dim=dim,
        )

    # ── Load ──────────────────────────────────────────────────────────────────

    def load_index(self) -> None:
        """
        Loads the FAISS index and chunk metadata from disk into memory.
        Raises RuntimeError if the index files are missing.
        """
        pkl_file = self.persist_path / "index.pkl"
        json_file = self.persist_path / "items.json"
        idx_file = self.persist_path / "index.faiss"

        # Load metadata — prefer pickle, fall back to JSON
        if pkl_file.exists():
            with open(pkl_file, "rb") as f:
                self.items = pickle.load(f)
        elif json_file.exists():
            self.items = json.loads(json_file.read_text(encoding="utf-8"))
        else:
            raise RuntimeError(f"FAISS metadata not found at {self.persist_path}")

        # Load binary index
        if idx_file.exists():
            self.index = faiss.read_index(str(idx_file))
            logger.info("faiss_store.loaded", path=str(self.persist_path), items=len(self.items))
        else:
            logger.warning("faiss_store.index_file_missing", path=str(self.persist_path))

    # ── Search ────────────────────────────────────────────────────────────────

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 20,
    ) -> List[Tuple[int, float]]:
        """
        Searches the FAISS index and returns (item_index, cosine_score) pairs.
        Scores are in [0, 1] for normalized vectors with IndexFlatIP.
        """
        if self.index is None or not self.items:
            return []

        q = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(q)

        k_request = min(max(top_k, 20), len(self.items))
        D, I = self.index.search(q, k_request)

        results: List[Tuple[int, float]] = []
        for idx, score in zip(I[0].tolist(), D[0].tolist()):
            if idx == -1:
                continue
            results.append((int(idx), float(score)))

        return results[:top_k]

    def is_built(self) -> bool:
        """Returns True if the vectorstore exists on disk and appears complete."""
        return (
            (self.persist_path / "index.faiss").exists()
            and (self.persist_path / "index.pkl").exists()
        )
