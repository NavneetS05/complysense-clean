# Use: Loads regulatory markdown files and chunks them at heading boundaries.

from pathlib import Path


def load_markdown_chunks(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8")
    return [chunk.strip() for chunk in content.split("\n## ") if chunk.strip()]
