# Use: Builds, persists, and loads the FAISS vector store database.

"""
Builds and manages the FAISS vector index over the regulatory knowledge base.

Lifecycle:
  startup  → is_built()? load_vectorstore() : build_vectorstore(docs)
  rebuild  → delete vectorstore/ directory, restart service
  runtime  → get_vectorstore() returns the in-memory instance
"""

import os
from pathlib import Path

from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

STORE_DIR = Path(__file__).resolve().parent / "vectorstore"
_EMBED_MODEL = "text-embedding-3-small"   # cheap, fast, 1536-dim, sufficient for regulatory text

_store: FAISS | None = None


def _embeddings() -> OpenAIEmbeddings:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY not set — cannot build or load vectorstore.")
    return OpenAIEmbeddings(model=_EMBED_MODEL, openai_api_key=key)


def build_vectorstore(docs: list[Document]) -> FAISS:
    """Embed all docs, build FAISS index, persist to disk."""
    global _store
    print(f"  Embedding {len(docs)} chunks with {_EMBED_MODEL}...")
    _store = FAISS.from_documents(docs, _embeddings())
    STORE_DIR.mkdir(parents=True, exist_ok=True)
    _store.save_local(str(STORE_DIR))
    print(f"  FAISS index saved → {STORE_DIR}")
    return _store


def load_vectorstore() -> FAISS:
    """Load persisted FAISS index from disk into memory."""
    global _store
    if _store is not None:
        return _store
    _store = FAISS.load_local(
        str(STORE_DIR),
        _embeddings(),
        allow_dangerous_deserialization=True,  # safe — we wrote this file ourselves
    )
    return _store


def get_vectorstore() -> FAISS:
    """Return the in-memory store. Raises RuntimeError if not initialised."""
    if _store is None:
        raise RuntimeError(
            "Vectorstore not initialised. "
            "Call build_vectorstore() or load_vectorstore() on startup."
        )
    return _store


def is_built() -> bool:
    """True if a persisted index exists on disk."""
    return STORE_DIR.exists() and any(STORE_DIR.iterdir())
