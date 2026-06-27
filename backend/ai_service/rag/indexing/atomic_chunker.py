# Use: Splits Markdown into Atomic Units while preserving legal and semantic boundaries.

from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter


class AtomicChunker:
    def __init__(self, target_size: int = 500, overlap: int = 100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=target_size,
            chunk_overlap=overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
        )

    def split_document(self, document_content: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Splits markdown file content into chunks, preserving atomic units matching negations/rules.
        """
        return []
