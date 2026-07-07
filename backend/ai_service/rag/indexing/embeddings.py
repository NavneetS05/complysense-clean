# Use: Creates embedding vectors for chunks using BAAI/bge-m3 (local via sentence-transformers).
# Provides a deterministic Blake2b fallback if sentence-transformers is unavailable (CI / lightweight dev).

import hashlib
from typing import List

from ai_service.config import get_ai_settings
from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.indexing.embeddings")


# ── Singleton model cache ──────────────────────────────────────────────────────
# Loading BAAI/bge-m3 (~2.2 GB) is expensive. We store a single instance here
# so every module that imports EmbeddingsGenerator shares the same loaded model.
_MODEL_INSTANCES: dict = {}


def _local_hash_vector(text: str, dim: int = 1024) -> List[float]:
    """
    Deterministic fallback embedding via Blake2b hashing.
    Not semantically meaningful — used for local dev / unit tests when
    sentence-transformers is not installed.
    """
    digest = b""
    counter = 0
    while len(digest) < dim:
        chunk_size = min(64, dim - len(digest))
        h = hashlib.blake2b(digest_size=chunk_size)
        h.update(f"{counter}:{text}".encode("utf-8", errors="ignore"))
        digest += h.digest()
        counter += 1
    # Scale bytes to normalized range [-1.0, 1.0]
    return [((b / 255.0) * 2.0 - 1.0) for b in digest[:dim]]


class EmbeddingsGenerator:
    """
    Wraps the BAAI/bge-m3 SentenceTransformer model.
    On first instantiation the model is loaded from disk (or downloaded once).
    Subsequent instantiations with the same model_name share the cached object.
    Falls back to deterministic Blake2b hashing when the package is unavailable.
    """

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        settings = get_ai_settings()
        self.model_name = model_name or settings.embeddings_model
        self._model = None
        self._mode = "local"
        self._dim = 1024

        # Attempt to load/reuse the singleton SentenceTransformer model
        if self.model_name not in _MODEL_INSTANCES:
            try:
                from sentence_transformers import SentenceTransformer
                _MODEL_INSTANCES[self.model_name] = SentenceTransformer(self.model_name)
                logger.info("embeddings.model_loaded", model=self.model_name)
            except Exception as exc:
                logger.warning(
                    "embeddings.model_unavailable",
                    model=self.model_name,
                    fallback="blake2b",
                    error=str(exc),
                )
                _MODEL_INSTANCES[self.model_name] = None

        self._model = _MODEL_INSTANCES[self.model_name]
        if self._model is not None:
            self._mode = "transformer"
            self._dim = self._model.get_sentence_embedding_dimension() or 1024

    @property
    def dim(self) -> int:
        return self._dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Returns dense embedding vectors for a list of chunk texts.
        Called during indexing only.
        normalize_embeddings=True is required for cosine similarity to work.
        """
        if self._mode == "transformer" and self._model is not None:
            try:
                return self._model.encode(texts, normalize_embeddings=True).tolist()
            except Exception as exc:
                logger.warning("embeddings.encode_failed", error=str(exc), fallback="blake2b")

        # Fallback: deterministic Blake2b hashing
        return [_local_hash_vector(t, dim=self._dim) for t in texts]

    def embed_query(self, query_text: str) -> List[float]:
        """
        Returns a single dense embedding vector for a user query.
        Must use the same model as indexing time.
        """
        return self.embed_documents([query_text])[0]
