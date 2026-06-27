# Use: Creates embedding vectors for chunks using BAAI/bge-m3 (free, local, via sentence-transformers).

from typing import List
from sentence_transformers import SentenceTransformer


class EmbeddingsGenerator:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        # Loads model locally on first run, cached to disk thereafter (~2.2 GB download once)
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Returns dense embedding vectors for a list of chunk texts.
        Called during indexing only.
        """
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, query_text: str) -> List[float]:
        """
        Returns a single dense embedding vector for a user query.
        Called at retrieval time for every incoming query.
        IMPORTANT: Must use the same model used during indexing.
        """
        return self.model.encode(query_text, normalize_embeddings=True).tolist()
