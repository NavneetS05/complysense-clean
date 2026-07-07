# Use: Injects explicitly linked sections into retrieved context.

from typing import List, Dict, Any


class CrossReferenceInjector:
    def __init__(self, all_chunks: List[Dict[str, Any]] | None = None):
        self.all_chunks = all_chunks or []
        self.chunks_map = {}
        self._build_map()

    def _build_map(self):
        self.chunks_map = {}
        for chunk in self.all_chunks:
            meta = chunk.get("meta") or chunk.get("metadata") or {}
            fw = meta.get("framework")
            sid = meta.get("section_id")
            if fw and sid:
                self.chunks_map[(fw, sid)] = chunk

    def inject_references(
        self,
        primary_chunks: List[Dict[str, Any]],
        all_chunks: List[Dict[str, Any]] | None = None
    ) -> List[Dict[str, Any]]:
        """
        Inspects cross_refs in chunk metadata, fetches referenced chunks, and appends them
        as secondary context (capped at 2 total secondary injections).
        """
        if all_chunks is not None:
            self.all_chunks = all_chunks
            self._build_map()
            
        secondary_chunks = []
        injected_keys = set()
        
        for chunk in primary_chunks:
            meta = chunk.get("meta") or chunk.get("metadata") or {}
            cross_refs = meta.get("cross_refs", [])
            fw = meta.get("framework")
            
            if not cross_refs or not fw:
                continue
                
            for ref in cross_refs:
                key = (fw, ref)
                if key in self.chunks_map and key not in injected_keys:
                    if len(secondary_chunks) >= 2:
                        break
                    ref_chunk = self.chunks_map[key].copy()
                    ref_chunk["is_secondary"] = True
                    secondary_chunks.append(ref_chunk)
                    injected_keys.add(key)
                    
            if len(secondary_chunks) >= 2:
                break
                
        return secondary_chunks

