# Use: Prompt injection and malicious input sanitization.

import re

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"you\s+are\s+now",
    r"disregard\s+(your|all|the)",
    r"(system|assistant)\s*:",
    r"<\|im_start\|>",
    r"prompt\s+injection",
    r"reveal\s+(your|the|this)\s+(prompt|instructions|system)",
    r"act\s+as\s+(if\s+you\s+are|a|an)",
    r"jailbreak",
    r"DAN\s+mode",
]


class InputSanitizer:
    def sanitize_input(self, input_text: str) -> str:
        """
        Scans input for prompt injection keywords and raises ValueError if any match is found.
        Also strips out potential markdown injection tags.
        """
        if not input_text:
            return ""
            
        # Scan for injection patterns
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                raise ValueError("Potential prompt injection detected.")
                
        # Clean special tokens to prevent template breaks
        sanitized = input_text.replace("<external_content>", "").replace("</external_content>", "")
        return sanitized

    def wrap_external_content(self, text: str) -> str:
        """
        Wraps user-submitted text in XML delimiters to protect against downstream jailbreaks.
        """
        cleaned = self.sanitize_input(text)
        return f"<external_content>\n{cleaned}\n</external_content>"

