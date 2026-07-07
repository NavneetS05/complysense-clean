# Use: Loads regulatory markdown files from local knowledge_base or downloads from Supabase.
# Updated: Uses decoupled Supabase client (no app.* imports). Supports structured node parsing.

import os
from typing import List, Dict, Any
from pathlib import Path

from ai_service.config import get_ai_settings
from ai_service.utils.supabase import download_file_from_bucket
from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.indexing.markdown_loader")

FRAMEWORK_MAPPING = {
    "dpdp": "DPDP Act 2023",
    "cert-in": "CERT-In 2022",
    "iso27001": "ISO 27001:2022",
    "ugc": "UGC Guidelines",
    "naac": "NAAC Criteria 4 & 6",
    "nist": "NIST CSF 2.0",
}

FILES_TO_DOWNLOAD: List[tuple] = [
    ("dpdp", "dpdp/DPDP_Act.md"),
    ("cert-in", "cert-in/CERT_IN_Directions.md"),
    ("iso27001", "iso27001/ISO27001_2022.md"),
    ("ugc", "ugc/UGC_Guidelines.md"),
    ("naac", "naac/NAAC_Framework.md"),
    ("nist", "nist/NIST_CSF.md"),
]


# ── Structured node parser (taken from PR) ─────────────────────────────────────

import re
from typing import Tuple


def _parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter at the beginning of the markdown file."""
    meta: Dict[str, Any] = {}
    remaining = text.strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            remaining = parts[2].strip()
            for line in parts[1].splitlines():
                line = line.strip()
                if not line or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                k, v = k.strip(), v.strip()
                if v.startswith("[") and v.endswith("]"):
                    v = [
                        item.strip().strip('"').strip("'")
                        for item in v[1:-1].split(",")
                        if item.strip()
                    ]
                else:
                    v = v.strip('"').strip("'")
                meta[k] = v
    return meta, remaining


def _parse_meta_comment(comment_text: str) -> Dict[str, Any]:
    """Parse <!-- meta: ... --> inline metadata comments."""
    meta: Dict[str, Any] = {}
    pattern = r'(\w+)\s*=\s*(?:\[(.*?)\]|"(.*?)"|(\w+))'
    for match in re.findall(pattern, comment_text):
        k = match[0]
        if match[1]:
            val = [x.strip().strip('"').strip("'") for x in match[1].split(",") if x.strip()]
        elif match[2]:
            val = match[2]
        else:
            val = match[3]
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
        meta[k] = val
    return meta


def _parse_markdown_to_structure(
    path: Path,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Structured parser: produces frontmatter dict + list of heading nodes."""
    raw_text = path.read_text(encoding="utf-8")
    frontmatter, remaining_text = _parse_frontmatter(raw_text)

    nodes: List[Dict[str, Any]] = []
    lines = remaining_text.splitlines()
    i = 0
    current_node = None

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("#"):
            if current_node:
                nodes.append(current_node)
                current_node = None

            heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                meta: Dict[str, Any] = {}
                if i + 1 < len(lines) and "<!-- meta:" in lines[i + 1]:
                    meta = _parse_meta_comment(lines[i + 1])
                    i += 1
                current_node = {
                    "type": "heading",
                    "level": level,
                    "text": text,
                    "meta": meta,
                    "content": [],
                }
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if "<!-- meta:" in stripped:
            meta = _parse_meta_comment(stripped)
            if current_node:
                current_node["meta"].update(meta)
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            table_text = "\n".join(table_lines)
            if current_node is None:
                current_node = {
                    "type": "heading",
                    "level": 2,
                    "text": "Introduction",
                    "meta": {},
                    "content": [],
                }
            current_node["content"].append({"type": "table", "text": table_text})
            continue

        # Standard paragraph
        para_lines = []
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].strip().startswith("#")
            and not lines[i].strip().startswith("|")
            and "<!-- meta:" not in lines[i]
        ):
            para_lines.append(lines[i].strip())
            i += 1
        para_text = " ".join(para_lines)
        if para_text:
            if current_node is None:
                current_node = {
                    "type": "heading",
                    "level": 2,
                    "text": "Introduction",
                    "meta": {},
                    "content": [],
                }
            current_node["content"].append({"type": "paragraph", "text": para_text})
        continue

    if current_node:
        nodes.append(current_node)

    return frontmatter, nodes


# ── MarkdownLoader ─────────────────────────────────────────────────────────────

class MarkdownLoader:
    """
    Loads regulatory markdown files:
    1. Checks local knowledge_base/ folder first.
    2. Falls back to downloading from Supabase Storage when local is empty.
    3. Returns structured list of (frontmatter, nodes) for each document.
    """

    def __init__(self, use_supabase: bool = True):
        self.use_supabase = use_supabase
        self.settings = get_ai_settings()
        self.local_kb_dir = Path(__file__).resolve().parents[2] / "knowledge_base"

    def load_documents(self) -> List[Dict[str, Any]]:
        """
        Returns a list of dicts:
        {
            "document_name": str,       # stem of the markdown file
            "path": Path,               # absolute path to the file
            "metadata": dict,           # parsed frontmatter
            "nodes": list,              # structured heading nodes
            # legacy keys for backward compat:
            "framework": str,
            "file_name": str,
            "content": str,
            "source": str,
        }
        """
        self.local_kb_dir.mkdir(parents=True, exist_ok=True)
        local_files = self._scan_local()

        if not local_files and self.use_supabase:
            logger.info(
                "markdown_loader.local_empty",
                detail="Downloading knowledge base files from Supabase Storage...",
            )
            self._download_from_supabase()
            local_files = self._scan_local()

        if not local_files:
            logger.warning(
                "markdown_loader.no_documents",
                kb_dir=str(self.local_kb_dir),
            )
            return []

        documents: List[Dict[str, Any]] = []
        for file_path in sorted(local_files):
            try:
                frontmatter, nodes = _parse_markdown_to_structure(file_path)
                parent_dir = file_path.parent.name
                framework = FRAMEWORK_MAPPING.get(
                    parent_dir,
                    frontmatter.get("framework", "Unknown Framework"),
                )
                content = file_path.read_text(encoding="utf-8")
                documents.append(
                    {
                        # Structured keys (used by AtomicChunker)
                        "document_name": file_path.stem,
                        "path": file_path,
                        "metadata": frontmatter,
                        "nodes": nodes,
                        # Legacy keys (backward compat with IndexBuilder flat path)
                        "framework": framework,
                        "file_name": file_path.name,
                        "content": content,
                        "source": "knowledge_base",
                    }
                )
            except Exception as exc:
                logger.error(
                    "markdown_loader.read_error",
                    file=str(file_path),
                    error=str(exc),
                )

        logger.info("markdown_loader.loaded", count=len(documents))
        return documents

    # ── Private ────────────────────────────────────────────────────────────────

    def _scan_local(self) -> List[Path]:
        """Returns all .md files recursively under knowledge_base/."""
        return [p for p in self.local_kb_dir.glob("**/*.md") if p.is_file()]

    def _download_from_supabase(self) -> None:
        bucket = self.settings.supabase_knowledge_bucket
        for folder, path_in_bucket in FILES_TO_DOWNLOAD:
            try:
                file_bytes = download_file_from_bucket(bucket, path_in_bucket)
                if file_bytes is None:
                    continue
                local_path = self.local_kb_dir / folder / os.path.basename(path_in_bucket)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.write_bytes(file_bytes)
                logger.info("markdown_loader.downloaded", path=path_in_bucket)
            except Exception as exc:
                logger.error(
                    "markdown_loader.download_failed",
                    path=path_in_bucket,
                    error=str(exc),
                )
