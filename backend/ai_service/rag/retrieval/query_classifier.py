# Use: Detects lookup, gap analysis, vendor review or other supported query types.

from ai_service.utils.constants import QueryType


class QueryClassifier:
    def classify_query(self, query_text: str) -> str:
        """
        Classifies incoming user query to decide retrieval structure or model routing.
        """
        if not query_text:
            return QueryType.LOOKUP.value
            
        lower_query = query_text.lower()
        
        if any(w in lower_query for w in ["gap", "matrix", "remediation", "mitigation"]):
            return QueryType.GAP_ANALYSIS.value
            
        if any(w in lower_query for w in ["validate", "conflict", "contradict", "policy"]):
            return QueryType.POLICY_VALIDATION.value
            
        if any(w in lower_query for w in ["vendor", "contract", "dpa", "soc2", "agreement"]):
            return QueryType.VENDOR_REVIEW.value
            
        if any(w in lower_query for w in ["cert-in", "incident", "breach", "timer", "countdown"]):
            return QueryType.CERT_IN_REPORT.value
            
        if any(w in lower_query for w in ["digest", "summary", "morning", "overview"]):
            return QueryType.DIGEST.value
            
        if any(w in lower_query for w in ["translate", "jargon", "plain english", "explain"]):
            return QueryType.TRANSLATION.value
            
        return QueryType.LOOKUP.value
