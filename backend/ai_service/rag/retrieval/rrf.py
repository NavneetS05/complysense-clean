# Use: Reciprocal Rank Fusion to merge dense and sparse retrieval results.

from typing import List, Dict, Any


class ReciprocalRankFusion:
    def __init__(self, k: int = 60):
        self.k = k

    def merge_rankings(
        self,
        dense_results: List[Dict[str, Any]],
        sparse_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Combines two lists of ranked search results using RRF score formula: 1 / (k + rank)
        """
        rrf_scores = {}
        chunks_by_key = {}
        
        # Helper to generate a unique key for each chunk
        def _get_key(chunk: Dict[str, Any]) -> tuple:
            # We can use text or meta values
            meta = chunk.get("meta") or chunk.get("metadata") or {}
            return (
                meta.get("framework", "Unknown"),
                meta.get("section_id", "Unknown"),
                meta.get("chunk_index", 0),
                chunk.get("text", "")[:50]  # first 50 chars as fallback
            )

        # Dense ranking
        for rank, chunk in enumerate(dense_results):
            key = _get_key(chunk)
            chunks_by_key[key] = chunk
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (self.k + rank + 1)
            
        # Sparse ranking
        for rank, chunk in enumerate(sparse_results):
            key = _get_key(chunk)
            chunks_by_key[key] = chunk
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1.0 / (self.k + rank + 1)
            
        # Sort by RRF score descending
        sorted_keys = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        merged = []
        for key in sorted_keys:
            chunk = chunks_by_key[key].copy()
            # Injected RRF score
            chunk["rrf_score"] = rrf_scores[key]
            merged.append(chunk)
            
        return merged

