# Use: Loads regulatory markdown files and chunks them at heading boundaries.

from pathlib import Path


"""
Loads regulatory markdown files from knowledge_base/, parses YAML frontmatter,
and splits at ## heading boundaries into LangChain Documents.

Every .md file MUST start with a YAML frontmatter block:

    ---
    framework: "CERT-In 2022"
    version: "2022"
    applies_to: ["it_security", "compliance_officer"]
    last_updated: "2025-01-01"
    ---

Each ## section becomes one chunk. ### sub-headings stay inside their parent chunk
so tables and numbered lists are never split across vectors.
"""

import re
from pathlib import Path

import yaml
from langchain.schema import Document

KB_DIR = Path(__file__).resolve().parent / "knowledge_base"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (meta_dict, body_text)."""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    raw = content[3:end].strip()
    body = content[end + 3:].strip()
    try:
        meta = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        meta = {}
    return meta, body


def _split_sections(body: str) -> list[tuple[str, str]]:
    """
    Split on ## headings. Returns list of (heading_title, section_body).
    Content before the first ## is treated as an 'Overview' section.
    """
    parts = re.split(r"\n(?=## )", body)
    sections: list[tuple[str, str]] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        lines = part.split("\n", 1)
        if lines[0].startswith("##"):
            heading = lines[0].lstrip("# ").strip()
            body_text = lines[1].strip() if len(lines) > 1 else ""
        else:
            heading = "Overview"
            body_text = part
        sections.append((heading, body_text))
    return sections


def load_framework_file(path: Path) -> list[Document]:
    """Load one .md file → list of Documents with metadata per chunk."""
    content = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(content)

    framework = meta.get("framework", path.stem)
    applies_to: list[str] = meta.get("applies_to", [])
    version: str = meta.get("version", "")

    docs: list[Document] = []
    for idx, (heading, text) in enumerate(_split_sections(body)):
        section_id = re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")
        docs.append(Document(
            page_content=f"[{framework}] {heading}\n\n{text}",
            metadata={
                "framework": framework,
                "version": version,
                "section_id": section_id,
                "section_title": heading,
                "source_file": path.name,
                "applies_to": applies_to,
                "chunk_index": idx,
            },
        ))
    return docs


def load_all_frameworks(kb_dir: Path = KB_DIR) -> list[Document]:
    """Load every .md file (except WRITING_GUIDE.md) → flat Document list."""
    md_files = [
        p for p in sorted(kb_dir.glob("*.md"))
        if p.name != "WRITING_GUIDE.md"
    ]
    if not md_files:
        raise FileNotFoundError(
            f"No framework .md files found in {kb_dir}. "
            "Add the 6 regulatory framework files before starting the AI service."
        )
    all_docs: list[Document] = []
    for path in md_files:
        chunks = load_framework_file(path)
        all_docs.extend(chunks)
        print(f"  {path.name}: {len(chunks)} chunks")
    print(f"  Total: {len(all_docs)} chunks across {len(md_files)} frameworks")
    return all_docs


def load_from_supabase(bucket: str = "knowledge-base") -> list[Document]:
    """
    Download missing .md files from Supabase 'knowledge-base' bucket into KB_DIR,
    then call load_all_frameworks(). Used when local KB_DIR is empty on a fresh deploy.
    Silently falls back to local if Supabase is not configured.
    """
    import os

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("  Supabase not configured — falling back to local knowledge_base/.")
        return load_all_frameworks()

    try:
        from supabase import create_client
        client = create_client(url, key)
        files = client.storage.from_(bucket).list()
        KB_DIR.mkdir(exist_ok=True)
        for f in files:
            name: str = f["name"]
            if not name.endswith(".md") or name == "WRITING_GUIDE.md":
                continue
            local = KB_DIR / name
            if local.exists():
                continue
            data = client.storage.from_(bucket).download(name)
            local.write_bytes(data)
            print(f"  Downloaded {name} from Supabase.")
    except Exception as exc:
        print(f"  Supabase download failed ({exc}) — using local files.")

    return load_all_frameworks()