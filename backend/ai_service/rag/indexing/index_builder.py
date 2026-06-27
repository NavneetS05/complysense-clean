# Use: Complete indexing pipeline orchestrator (Markdown → Metadata → Chunk → Embedding → Indices).

class IndexBuilder:
    def __init__(self):
        pass

    def run_reindex_pipeline(self) -> None:
        """
        Orchestrates full re-indexing pipeline:
        1. Download latest .md files.
        2. Clean and chunk texts.
        3. Build FAISS and BM25 store.
        4. Atomic switch and load.
        """
        pass
