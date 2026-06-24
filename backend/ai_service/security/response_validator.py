from __future__ import annotations

import re
from typing import Any

JAILBREAK_PATTERNS = [
    r"I am now",
    r"ignoring previous",
    r"as an unrestricted",
    r"disregard.*previous",
]

CITATION_PATTERN = re.compile(r"Per \[(?P<framework>[^\]]+)\], \[(?P<section>[^\]]+)\]:")


def validate_response(response: str, context: dict[str, Any]) -> dict[str, Any]:
    normalized = response.lower()
    for pattern in JAILBREAK_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return {"error": "LLM_INJECTION_DETECTED", "message": "Unsafe LLM output rejected."}

    retrieved_frameworks = {chunk["metadata"]["framework"] for chunk in context.get("retrieved_chunks", []) if chunk.get("metadata")}
    for match in CITATION_PATTERN.finditer(response):
        if match.group("framework") not in retrieved_frameworks:
            return {"error": "FABRICATED_CITATION", "message": "Response cites a framework not present in retrieved documents."}

    return {"result": response}
