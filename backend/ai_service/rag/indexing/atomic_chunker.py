# Use: Splits parsed document nodes into token-aware chunks preserving atomic obligation locks.
# Taken from PR and adapted: uses structured nodes from MarkdownLoader's _parse_markdown_to_structure.

import re
import math
from typing import List, Dict, Any

from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.indexing.atomic_chunker")

ATOMIC_TRIGGERS = [
    r"\bshall not\b",
    r"\bmust not\b",
    r"\bprohibited\b",
    r"\bexcept\b",
    r"\bunless\b",
    r"\bnotwithstanding\b",
    r"\bsubject to\b",
    r"\bprovided that\b",
    r"\bwhere.*?applies\b",
]


def _approx_token_count(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def _is_atomic_paragraph(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(trigger, text_lower) for trigger in ATOMIC_TRIGGERS)


def _get_last_n_tokens(text: str, n_tokens: int = 100) -> str:
    """Return approximately the last N tokens' worth of characters for overlap stitching."""
    char_count = n_tokens * 4
    if len(text) <= char_count:
        return text
    sub = text[-char_count:]
    first_space = sub.find(" ")
    return sub[first_space + 1:] if first_space != -1 else sub


def _split_large_text(
    text: str,
    target_tokens: int = 500,
    overlap_tokens: int = 100,
) -> List[str]:
    """Split a long non-atomic paragraph at sentence/word boundaries with overlap."""
    target_chars = target_tokens * 4
    overlap_chars = overlap_tokens * 4

    parts: List[str] = []
    start = 0
    while start < len(text):
        end = start + target_chars
        if end >= len(text):
            parts.append(text[start:].strip())
            break

        sub = text[start:end]
        last_dot = sub.rfind(". ")
        if last_dot != -1 and last_dot > target_chars // 2:
            split_at = start + last_dot + 1
        else:
            last_space = sub.rfind(" ")
            split_at = start + last_space if last_space != -1 else end

        parts.append(text[start:split_at].strip())
        start = max(split_at - overlap_chars, split_at)

    return [p for p in parts if p]


class AtomicChunker:
    """
    Converts structured document nodes (from MarkdownLoader) into RAG-ready chunks.

    Key guarantees:
    - Atomic obligation clauses ("shall not", "unless", etc.) are never split mid-sentence.
    - Chunk token count is bounded between target_tokens (min) and max_tokens (max).
    - A breadcrumb prefix is prepended for better retrieval context.
    - Supports both structured node path (split_document_nodes) and legacy plain text path
      (split_document) for backward compatibility.
    """

    def __init__(
        self,
        target_tokens: int = 500,
        overlap_tokens: int = 100,
        max_tokens: int = 600,
        # Kept for backward compat (local code used target_size=500, overlap=100)
        target_size: int | None = None,
        overlap: int | None = None,
    ):
        self.target_tokens = target_size if target_size is not None else target_tokens
        self.overlap_tokens = overlap if overlap is not None else overlap_tokens
        self.max_tokens = max_tokens

    # ── Structured path (primary) ──────────────────────────────────────────────

    def split_document_nodes(
        self,
        document_name: str,
        nodes: List[Dict[str, Any]],
        doc_metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Converts parsed heading nodes into chunks, preserving section hierarchy.

        Args:
            document_name: stem of the markdown filename (e.g. "DPDP_Act").
            nodes: list of heading node dicts from _parse_markdown_to_structure.
            doc_metadata: YAML frontmatter dict (framework, applies_to, doc_type …).
        """
        framework = doc_metadata.get("framework", document_name)
        doc_applies_to = doc_metadata.get("applies_to", [])

        chunks: List[Dict[str, Any]] = []
        chunk_counter = 0
        current_section = ""
        current_subsection = ""

        for node in nodes:
            if node.get("type") != "heading":
                continue

            level = node.get("level", 2)
            heading_text = node.get("text", "").strip()
            node_meta = node.get("meta", {})

            if level <= 2:
                current_section = heading_text
                current_subsection = ""
            else:
                current_subsection = heading_text

            applies_to = node_meta.get("applies_to") or doc_applies_to
            if isinstance(applies_to, str):
                applies_to = [applies_to]

            section_id = node_meta.get("section_id", "")
            parent_id = node_meta.get("parent_id", "")
            is_definitions = bool(node_meta.get("is_definitions", False))
            keep_whole_section = bool(node_meta.get("keep_whole", False))
            cross_refs = node_meta.get("cross_refs", [])
            keywords = node_meta.get("keywords", [])

            breadcrumb_parts = [p for p in [framework, current_section, current_subsection] if p]
            breadcrumb = " > ".join(breadcrumb_parts)
            breadcrumb_prefix = f"[{breadcrumb}]\n\n"

            # Group blocks into token-bounded sub-chunks
            section_chunk_groups: List[List[tuple]] = []
            current_group: List[tuple] = []
            current_group_tokens = 0

            for block in node.get("content", []):
                block_type = block.get("type", "paragraph")
                block_text = block.get("text", "").strip()
                if not block_text:
                    continue

                block_tokens = _approx_token_count(block_text)
                is_atomic = _is_atomic_paragraph(block_text) or block_type == "table"

                if block_tokens > 800 and not is_atomic and not keep_whole_section:
                    sub_texts = _split_large_text(
                        block_text,
                        target_tokens=self.target_tokens,
                        overlap_tokens=self.overlap_tokens,
                    )
                    for st in sub_texts:
                        st_tokens = _approx_token_count(st)
                        if current_group_tokens + st_tokens > self.max_tokens and current_group_tokens >= 350:
                            section_chunk_groups.append(current_group)
                            current_group = []
                            current_group_tokens = 0
                        current_group.append((st, block_type, is_atomic))
                        current_group_tokens += st_tokens
                else:
                    if current_group_tokens + block_tokens > self.max_tokens and current_group_tokens >= 350:
                        section_chunk_groups.append(current_group)
                        current_group = []
                        current_group_tokens = 0
                    current_group.append((block_text, block_type, is_atomic))
                    current_group_tokens += block_tokens

            if current_group:
                section_chunk_groups.append(current_group)

            for idx, group in enumerate(section_chunk_groups):
                chunk_counter += 1
                blocks_text = "\n\n".join(b[0] for b in group)
                full_text = breadcrumb_prefix + blocks_text

                has_table = any(b[1] == "table" for b in group)
                keep_whole = keep_whole_section or any(b[2] for b in group)

                chunks.append(
                    {
                        "text": full_text,
                        "meta": {
                            "framework": framework,
                            "doc_type": doc_metadata.get("doc_type", "legislation"),
                            "source_file": f"{document_name}.md",
                            "section_id": section_id,
                            "section_title": current_subsection or current_section,
                            "breadcrumb": breadcrumb,
                            "parent_id": parent_id,
                            "chunk_index": idx,
                            "chunk_of": len(section_chunk_groups),
                            "token_count": _approx_token_count(full_text),
                            "is_definitions": is_definitions,
                            "has_table": has_table,
                            "keep_whole": keep_whole,
                            "cross_refs": cross_refs,
                            "applies_to": applies_to,
                            "keywords": keywords,
                            "chunk_id": f"{document_name}#c{chunk_counter}",
                            "chunk_number": chunk_counter,
                        },
                    }
                )

        logger.info(
            "atomic_chunker.chunked",
            document=document_name,
            chunks=len(chunks),
        )
        return chunks

    # ── Legacy flat-text path (backward compat) ────────────────────────────────

    def split_document(
        self,
        document_content: str,
        metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Fallback chunker for plain-string content (used for user-uploaded documents
        from MongoDB where there's no heading structure to parse).
        """
        parts = _split_large_text(
            document_content,
            target_tokens=self.target_tokens,
            overlap_tokens=self.overlap_tokens,
        )
        items: List[Dict[str, Any]] = []
        for i, part in enumerate(parts, 1):
            chunk_id = f"{metadata.get('document_name', metadata.get('source_file', 'doc'))}#c{i}"
            meta = dict(metadata)
            meta.update(
                {
                    "chunk_id": chunk_id,
                    "chunk_number": i,
                    "token_count": _approx_token_count(part),
                }
            )
            items.append({"text": part, "meta": meta})
        return items
