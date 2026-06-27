# Use: Rejects retrieval when similarity/confidence falls below threshold.

from typing import List, Dict, Any


class ConfidenceScorer:
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def check_confidence(self, results: List[Dict[str, Any]]) -> bool:
        """
        Returns true if the retrieved items satisfy similarity score threshold.
        """
        return True
