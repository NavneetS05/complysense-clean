# Use: Output safety validation — jailbreak indicators + fabricated citation detection.
# Upgraded: merges local jailbreak check with PR's framework-keyword citation check.
# Replaces the thin wrapper that only detected jailbreak strings.

import re
from typing import Any, Dict, List

from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.security.response_validator")

# ── Jailbreak indicators ───────────────────────────────────────────────────────
JAILBREAK_INDICATORS = [
    "i am now",
    "as an unrestricted",
    "ignoring previous",
    "without restrictions",
    "my true purpose",
    "jailbreak",
    "ignore all previous instructions",
]

# ── Framework keyword map for citation verification ────────────────────────────
# Keys match chunk meta["framework"] values exactly.
FRAMEWORK_KEYWORDS: Dict[str, List[str]] = {
    "DPDP Act 2023": ["dpdp", "personal data protection", "data fiduciary", "data principal"],
    "CERT-In 2022": ["cert-in", "cert in", "cybersecurity directions", "6-hour"],
    "ISO 27001:2022": ["iso 27001", "iso27001", "annex a"],
    "NIST CSF 2.0": ["nist", "cybersecurity framework"],
    "UGC Guidelines": ["ugc", "university grants"],
    "NAAC Criteria 4 & 6": ["naac", "accreditation"],
}


class OutputValidator:
    """
    Post-LLM safety gate. Runs two independent checks:
    1. Jailbreak indicator detection — catches prompt injection in LLM output.
    2. Fabricated citation detection — confirms that every framework referenced in the
       response was actually present in the retrieved chunks.

    Both checks must pass for the response to be allowed through.
    """

    def validate_safety(
        self,
        output_text: str,
        retrieved_chunks: List[Dict[str, Any]] | None = None,
    ) -> bool:
        """
        Returns True if the response passes all safety checks.

        Args:
            output_text: raw LLM response text.
            retrieved_chunks: list of chunk dicts (used for citation verification).
                              If None, citation check is skipped (backward compat).
        """
        if not output_text:
            return True

        output_lower = output_text.lower()

        # ── Check 1: Jailbreak indicators ──────────────────────────────────────
        for indicator in JAILBREAK_INDICATORS:
            if indicator in output_lower:
                logger.warning(
                    "output_validator.jailbreak_detected",
                    indicator=indicator,
                )
                return False

        # ── Check 2: Fabricated citation detection ──────────────────────────────
        if retrieved_chunks is not None:
            if not self._citations_are_grounded(output_lower, retrieved_chunks):
                return False

        return True

    # ── Private ────────────────────────────────────────────────────────────────

    def _citations_are_grounded(
        self,
        output_lower: str,
        retrieved_chunks: List[Dict[str, Any]],
    ) -> bool:
        """
        Verifies that every framework mentioned in the output appears in the
        retrieved chunk metadata ('meta' or 'metadata' key, both supported).
        """
        retrieved_frameworks: set = set()
        for chunk in retrieved_chunks:
            # Support both 'meta' (new) and 'metadata' (legacy) keys
            meta = chunk.get("meta") or chunk.get("metadata") or {}
            fw = meta.get("framework")
            if fw:
                retrieved_frameworks.add(fw.strip())
            # User documents are always allowed as a citation source
            if meta.get("source") == "user_upload":
                retrieved_frameworks.add("User Document")

        # If nothing was retrieved there is nothing to validate against
        if not retrieved_frameworks:
            return True

        for framework, keywords in FRAMEWORK_KEYWORDS.items():
            mentioned = any(kw in output_lower for kw in keywords)
            if not mentioned:
                continue

            # Framework is mentioned — verify it was retrieved
            is_matched = any(
                r_fw.lower().strip() == framework.lower().strip()
                for r_fw in retrieved_frameworks
            )
            if not is_matched:
                logger.warning(
                    "output_validator.fabricated_citation",
                    framework=framework,
                    retrieved=list(retrieved_frameworks),
                )
                return False

        return True
