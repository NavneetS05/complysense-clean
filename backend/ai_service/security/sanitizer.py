from __future__ import annotations

import re

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"disregard.*previous",
    r"system:",
    r"assistant:",
    r"<\|im_start\|>",
    r"\bI am now\b",
    r"\bas an unrestricted\b",
]

MAX_LENGTH = 2000


def sanitize_input(user_input: str) -> str:
    cleaned = user_input
    for pattern in INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    if len(cleaned) > MAX_LENGTH:
        cleaned = cleaned[:MAX_LENGTH]
    return f"<external_content>{cleaned}</external_content>"
