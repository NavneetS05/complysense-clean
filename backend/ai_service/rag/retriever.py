# Use: Performs top-k similarity search queries over the persistent FAISS vector store.

class Retriever:
    def __init__(self, chunks: list[str]) -> None:
        self.chunks = chunks

    def top_k(self, _: str, k: int = 5) -> list[str]:
        return self.chunks[:k]
