# Use: Shared constants, thresholds and reusable enums.

from enum import Enum

# --- Embeddings Model (free, local via sentence-transformers) ---
EMBEDDINGS_MODEL = "BAAI/bge-m3"
EMBEDDINGS_DIMENSIONS = 1024      # bge-m3 output dimensionality

# --- LLM Model (Google Gemini, free tier available) ---
DEFAULT_LLM_MODEL = "gemini-2.5-flash"

# --- Retrieval Thresholds ---
RRF_K = 60                        # RRF rank fusion constant
FAISS_CANDIDATE_LIMIT = 20        # Max dense results before RRF
BM25_CANDIDATE_LIMIT = 20         # Max sparse results before RRF
PRIMARY_CHUNK_LIMIT = 7           # Final chunks passed to LLM
MAX_SECONDARY_XREFS = 2           # Max cross-reference injections

# --- Token Budgets ---
MAX_INPUT_TOKENS = 3200
MAX_OUTPUT_TOKENS = 1500
MIN_CHUNK_TOKENS = 100
TARGET_CHUNK_TOKENS_MIN = 350
TARGET_CHUNK_TOKENS_MAX = 600
MAX_CHUNK_TOKENS = 800
MAX_TABLE_CHUNK_TOKENS = 1000
CHUNK_OVERLAP_TOKENS = 100
HISTORY_TURNS_CONVERSATIONAL = 6
HISTORY_TURNS_RETRIEVAL_HEAVY = 4
HISTORY_TURNS_SINGLE_SHOT = 0

# --- Model Routing ---
# All tasks use gemini-2.5-flash (single model, no paid tier needed)
GEMINI_MODEL = "gemini-2.5-flash"

# --- Role → Permitted Frameworks ---
ROLE_FRAMEWORKS: dict[str, list[str]] = {
    "compliance_officer": [
        "DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0",
        "UGC Guidelines", "NAAC Criteria 4 & 6",
    ],
    "it_security": ["CERT-In 2022", "DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0"],
    "auditor": ["ISO 27001:2022", "NIST CSF 2.0", "NAAC Criteria 4 & 6", "UGC Guidelines"],
    "dept_reviewer": ["UGC Guidelines", "NAAC Criteria 4 & 6"],
    "vendor_reviewer": ["DPDP Act 2023", "ISO 27001:2022"],
    "policy_approver": ["DPDP Act 2023", "ISO 27001:2022", "UGC Guidelines"],
    "institution_admin": ["DPDP Act 2023", "NAAC Criteria 4 & 6", "UGC Guidelines"],
    "read_only_assessor": [
        "DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0",
        "CERT-In 2022", "UGC Guidelines", "NAAC Criteria 4 & 6",
    ],
    "super_admin": [],  # Does not use RAG
}


class QueryType(str, Enum):
    LOOKUP = "lookup"
    GAP_ANALYSIS = "gap_analysis"
    POLICY_VALIDATION = "policy_validation"
    VENDOR_REVIEW = "vendor_review"
    CERT_IN_REPORT = "certin_report"
    DIGEST = "digest"
    TRANSLATION = "translation"


class DocType(str, Enum):
    LEGISLATION = "legislation"
    STANDARD = "standard"
    GUIDELINE = "guideline"
    FRAMEWORK = "framework"
