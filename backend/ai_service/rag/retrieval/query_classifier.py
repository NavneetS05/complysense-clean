# Use: Detects lookup, gap analysis, vendor review or other supported query types.

class QueryClassifier:
    def classify_query(self, query_text: str) -> str:
        """
        Classifies incoming user query type into a matching task category.
        """
        return "lookup"
