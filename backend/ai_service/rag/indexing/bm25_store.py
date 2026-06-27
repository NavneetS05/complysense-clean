# Use: Builds and persists sparse BM25 keyword index.

from typing import List, Dict, Any


class BM25IndexStore:
    def __init__(self, persist_path: str):
        self.persist_path = persist_path
        self.index: Any = None

    def build_and_save(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Tokenizes chunks, builds BM25 index, and serializes to disk.
        """
        pass

    def load_index(self) -> None:
        """
        De-serializes BM25 index from disk.
        """
        pass
