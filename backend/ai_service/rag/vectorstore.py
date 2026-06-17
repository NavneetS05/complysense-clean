# Use: Builds, persists, and loads the FAISS vector store database.

from pathlib import Path


def vectorstore_path() -> Path:
    return Path(__file__).resolve().parent / "vectorstore"
