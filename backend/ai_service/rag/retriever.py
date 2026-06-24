# Use: Performs top-k similarity search queries over the persistent FAISS vector store.

"""
Similarity search over the FAISS index with role-based and framework-based filtering.

Design: single index, post-filter.
  FAISS does not support server-side metadata filters natively.
  We over-fetch (k×4) and filter in Python. For a ~500-chunk knowledge base
  this is effectively instant.
"""

from langchain.schema import Document

from ai_service.rag.vectorstore import get_vectorstore

# Maps each role to the frameworks it should search.
# Dept Reviewer gets UGC/NAAC only — no CERT-In noise.
# Assessor gets everything — they ask broad strategic questions.
ROLE_FRAMEWORKS: dict[str, list[str]] = {
    "compliance_officer": [
        "DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0",
        "UGC Guidelines", "NAAC Criteria 4 & 6",
    ],
    "it_security": [
        "CERT-In 2022", "DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0",
    ],
    "auditor": [
        "ISO 27001:2022", "NIST CSF 2.0", "NAAC Criteria 4 & 6", "UGC Guidelines",
    ],
    "dept_reviewer": [
        "UGC Guidelines", "NAAC Criteria 4 & 6",
    ],
    "vendor_reviewer": [
        "DPDP Act 2023", "ISO 27001:2022",
    ],
    "policy_approver": [
        "DPDP Act 2023", "ISO 27001:2022", "UGC Guidelines",
    ],
    "institution_admin": [
        "DPDP Act 2023", "NAAC Criteria 4 & 6", "UGC Guidelines",
    ],
    "read_only_assessor": [
        "DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0",
        "CERT-In 2022", "UGC Guidelines", "NAAC Criteria 4 & 6",
    ],
    "super_admin": [],  # Super Admin does not use RAG endpoints
}

ALL_FRAMEWORKS = set(
    fw for fws in ROLE_FRAMEWORKS.values() for fw in fws
)


def retrieve(
    query: str,
    k: int = 5,
    frameworks: list[str] | None = None,
    role: str | None = None,
) -> list[Document]:
    """
    Retrieve top-k relevant chunks.

    Filter priority:
      1. Explicit frameworks list
      2. Role-derived frameworks via ROLE_FRAMEWORKS
      3. No filter — full index (fallback)
    """
    vs = get_vectorstore()

    target = frameworks
    if not target and role:
        target = ROLE_FRAMEWORKS.get(role, [])

    if target:
        candidates = vs.similarity_search(query, k=k * 4)
        filtered = [d for d in candidates if d.metadata.get("framework") in target]
        return filtered[:k]

    return vs.similarity_search(query, k=k)


def retrieve_for_frameworks(query: str, frameworks: list[str], k: int = 6) -> list[Document]:
    """Convenience: retrieve for a specific framework list."""
    return retrieve(query, k=k, frameworks=frameworks)


def format_context(docs: list[Document]) -> str:
    """
    Format retrieved docs into a context block for system prompt injection.
    Each chunk is prefixed with its source so the LLM can cite accurately.
    """
    parts: list[str] = []
    for doc in docs:
        fw = doc.metadata.get("framework", "Unknown Framework")
        section = doc.metadata.get("section_title", "")
        parts.append(f"--- {fw} | {section} ---\n{doc.page_content}")
    return "\n\n".join(parts)


def retrieved_framework_names(docs: list[Document]) -> set[str]:
    """Extract the set of framework names present in retrieved docs."""
    return {doc.metadata.get("framework", "") for doc in docs if doc.metadata.get("framework")}
