# AI Module Audit

## Architecture

Implemented:

- AI service entry: `backend/ai_service/main.py`.
- Routers: `backend/ai_service/routers`.
- Agents: `backend/ai_service/agents`.
- Shared orchestration: `backend/ai_service/agents/base.py::BaseAgent`.
- RAG indexing: `backend/ai_service/rag/indexing`.
- RAG retrieval: `backend/ai_service/rag/retrieval`.
- RAG generation: `backend/ai_service/rag/generation`.
- Security helpers: `backend/ai_service/security`.
- LLM wrapper: `backend/ai_service/utils/llm.py`.

Current status: Partially Implemented overall; security-critical proxy permissions and CORS have been remediated.

## Runtime Startup

Implemented:

- `lifespan` in `backend/ai_service/main.py` builds or loads FAISS/BM25 indexes at startup.
- `/health/live` and `/health/ready` are available.
- `_index_ready` is set after successful index load/rebuild.

Risk:

- Cold start can be slow because index build may run during service startup.

## LLM

Implemented:

- Uses `ChatGoogleGenerativeAI` through `langchain-google-genai`.
- Default model: `gemini-2.5-flash`.
- Config: `backend/ai_service/config.py`.

Documentation drift:

- README mentions OpenAI, but code uses Gemini.

## RAG Flow

Implemented in `BaseAgent.execute`:

1. Role authorization through `RoleGuard`.
2. Input sanitization through `InputSanitizer`.
3. Query classification through `QueryClassifier`.
4. Hybrid retrieval through `HybridRetriever`.
5. Confidence gate through `ConfidenceScorer`.
6. Cross-reference injection.
7. Context assembly.
8. Prompt construction.
9. LLM call.
10. Response validation.
11. Citation list construction.

## AI Features

| Feature | Main API proxy | AI service route | Agent | Status |
|---|---|---|---|---|
| Compliance triage | `/api/v1/ai/compliance/triage` | `/compliance/triage` | `ComplianceAgent` | Implemented; proxy/service both require `VIEW_CONTROLS` |
| Regulatory change | `/api/v1/ai/compliance/regulatory-change` | `/compliance/regulatory-change` | `ComplianceAgent` | Implemented; proxy/service both require `VIEW_CONTROLS` |
| Compliance chat | Not found in proxy | `/compliance/chat` | `ComplianceAgent` | Partially Implemented |
| CERT-In draft | `/api/v1/ai/security/cert-in-draft/{incident_id}` | security router | `SecurityAgent` | Partially Implemented |
| Audit smart sample | `/api/v1/ai/audit/smart-sample` | audit router | `AuditAgent` | Canonical implementation; old local audit endpoint redirects |
| Audit draft observation | `/api/v1/ai/audit/draft-observation` | audit router | `AuditAgent` | Canonical implementation; old local audit endpoint redirects |
| Policy analysis | `/api/v1/ai/policy/analyze/{policy_id}` | policy router | `PolicyAgent` | Partially Implemented |
| Vendor contract analysis | `/api/v1/ai/vendor/analyze-contract` | vendor router | `VendorAgent` | Implemented with `vendor_risk_assessments` persistence |
| Department translation | `/api/v1/ai/dept/translate/{control_id}` | dept router | Dept route/agent logic | Partially Implemented |
| Department preflight | `/api/v1/ai/dept/preflight-check` | dept router | Dept route/agent logic | Partially Implemented |
| Admin risk heatmap | `/api/v1/ai/admin/risk-heatmap` | admin router | Admin route/agent logic | Partially Implemented |
| Assessor chat | `/api/v1/ai/assessor/chat` | assessor router | `AssessorAgent` | Implemented with `USE_ASSESSOR_CHAT` and `assessor_qa` conversation persistence |

## Supabase

Implemented:

- Settings include Supabase URL, service key, and knowledge bucket.
- Main API has `check_supabase`.
- AI indexing has Supabase-aware configuration.

Partially Implemented:

- End-to-end upload to Supabase knowledge base and trigger reindex flow is present only in parts; exact production data flow could not be confirmed from inspected routes.

## PostgreSQL

Implemented:

- AI service imports `app.core.permissions`, `app.schemas.auth`, and depends on main app auth context.
- Conversations table exists: `ai_conversations`.
- `ConversationManager` handles conversation history when IDs are provided.

## MongoDB

Implemented:

- Config exists for MongoDB document collection.
- Document storage helpers exist.
- Evidence upload writes document metadata and extracted text previews through `DocumentStore`.

## Response Validation

Implemented:

- `backend/ai_service/rag/generation/response_validator.py`.
- `backend/ai_service/security/response_validator.py`.

Partially Implemented:

- Validation blocks responses when citation/safety checks fail, but no route-level observability for blocked output was found.

## Caching

Partially Implemented:

- LLM clients are cached per model in `LLMService`.
- Retriever and cross-reference injector are process singletons.
- No distributed cache or request cache found.

## RBAC Concerns

- Main proxy and AI service route permissions are aligned for the remediated compliance, audit, policy, vendor, security, and assessor endpoints.
- AI service imports main app dependencies, which couples the microservice to main API code and DB config.
- AI service CORS no longer combines `allow_credentials=True` with wildcard origins; origins are configured via `AI_CORS_ORIGINS`.
