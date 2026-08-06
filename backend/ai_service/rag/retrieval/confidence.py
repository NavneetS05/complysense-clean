# Use: Rejects retrieval when similarity/confidence falls below threshold.
# Updated: checks both 'score' (root, from HybridRetriever) and 'rrf_score' keys.

from typing import Any, Dict, List

from ai_service.utils.logger import StructuredLogger

logger = StructuredLogger("ai_service.rag.retrieval.confidence")


class ConfidenceScorer:
    """
    Inspects the top retrieved chunk's score to decide whether retrieval is meaningful.

    After the HybridRetriever RRF merge the chunks carry an 'rrf_score' key.
    Dense-only candidates may carry a 'score' key (cosine similarity in [0,1]).
    BM25-only candidates carry a 'score' key (BM25 raw score > 0).

    The check is intentionally permissive: if any score is present and non-zero
    we trust the retrieval. A hard block is only issued when there are *no* results.
    """

    def __init__(self, threshold: float = 0.35) -> None:
        self.threshold = threshold

    def check_confidence(self, results: List[Dict[str, Any]]) -> bool:
        """
        Returns True if the retrieved results meet the confidence bar.
        Returns False only when results are completely empty.
        """
        if not results:
            logger.info("confidence_scorer.no_results")
            return False

        top = results[0]
        if "rrf_score" in top:
            # RRF score scale is reciprocal rank sum (~0.016 to ~0.04).
            passed = float(top["rrf_score"]) > 0.001
            return passed

        score = top.get("score")
        if score is not None:
            passed = float(score) >= 0.15
            if not passed:
                logger.info(
                    "confidence_scorer.below_threshold",
                    score=score,
                    threshold=0.15,
                )
            return passed

        return True
