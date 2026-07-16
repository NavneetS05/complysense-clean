# ComplySense Backend Contract
## AI Proxy Response Shape — All Role Endpoints

Status: Contract confirmed from source (`ai_service/agents/base.py`). This is documentation of an existing, real, single shared contract — not a new design. No `response_model` is enforced anywhere in the code today, which is the actual gap this doc closes.

---

### 1. Why this is one contract, not five

Every AI-facing role endpoint routes through `BaseAgent.execute()`:

| Frontend caller | Backend proxy route | AI service route | Agent method |
|---|---|---|---|
| `assessor/Chat.tsx` | `POST /api/v1/ai/assessor/chat` | `POST /assessor/chat` | `AssessorAgent.chat` |
| Compliance AI panel | `POST /api/v1/ai/compliance/triage` | `POST /compliance/triage` | `ComplianceAgent.triage` |
| Compliance AI panel | `POST /api/v1/ai/compliance/regulatory-change` | `POST /compliance/regulatory-change` | `ComplianceAgent.regulatory_change` |
| Security incident detail | `POST /api/v1/ai/security/cert-in-draft/{id}` | `POST /security/cert-in-draft` | `SecurityAgent.cert_in_draft` |
| Vendor AI panel | `POST /api/v1/ai/vendor/analyze-contract` | `POST /vendor/analyze-contract` | `VendorAgent.analyze_contract` |
| Policy review AI | `POST /api/v1/ai/policy/analyze/{id}` (calls both below in parallel) | `POST /policy/conflict-detect` + `POST /policy/executive-summary` | `PolicyAgent.conflict_detect`, `PolicyAgent.executive_summary` |

Every one of these agent methods is a thin wrapper — each just calls `self.execute(...)` with a different `task_prompt` and `extra_context`. `execute()` is the only place the response dict is actually constructed. **There is exactly one contract. Any frontend component consuming any of these endpoints should be built against the same shape.**

---

### 2. The contract is a six-shape discriminated union

`execute()` has six distinct return points. The presence or absence of the `error` key is what the frontend must branch on first — `query_type` and `chunks_used` are **only** guaranteed present on the success path.

| # | Branch | Trigger | Keys present | `error` value |
|---|---|---|---|---|
| 1 | Success | Normal completion | `role, response, citations, query_type, chunks_used` | — (absent) |
| 2 | Unauthorized | `RoleGuard.verify_role_access` fails | `role, response, citations` | `"UNAUTHORIZED"` |
| 3 | Injection blocked | `InputSanitizer.sanitize_input` raises `ValueError` | `role, response, citations` | `"INJECTION_BLOCKED"` |
| 4 | No confident retrieval | No chunks retrieved and confidence check fails | `role, response, citations, query_type` | — (absent, but `chunks_used` also absent) |
| 5 | LLM error | Exception raised during `LLMService.call` | `role, response, citations` | `"LLM_ERROR"` |
| 6 | Validation failed | `ResponseValidator.validate_response` returns false | `role, response, citations` | `"VALIDATION_FAILED"` |

**Field types, all branches:**

- `role`: string, always the agent's role identifier (e.g. `"compliance_officer"`)
- `response`: string, always present — either the LLM's real answer or a fixed human-readable message for the error branches
- `citations`: array of strings — framework names only (e.g. `["ISO 27001:2022", "DPDP Act 2023"]`), never chunk-level objects with page/section detail. On every error branch this is an empty array `[]`.
- `query_type`: string — only present on branches 1 and 4. Frontend must not assume this key exists.
- `chunks_used`: integer — only present on branch 1 (success). Frontend must not assume this key exists on any other branch, including branch 4, which retrieves zero confident chunks but does not include this key at all.
- `error`: string literal, one of `"UNAUTHORIZED" | "INJECTION_BLOCKED" | "LLM_ERROR" | "VALIDATION_FAILED"` — present only on branches 2, 3, 5, 6. Its absence (not a null/empty check — actual key absence) is what signals a normal or "not covered" response.

**Frontend consumption rule:** check `"error" in data` before reading `query_type` or `chunks_used`. Do not default-fallback these fields silently (e.g. `data.chunks_used ?? 0`) without being aware that a `0` in an error branch is indistinguishable from a genuine zero-chunks success — because the key is simply never sent on error branches, not sent as `0`.

---

### 3. Per-endpoint request shapes (already fixed, confirmed from router source — no ambiguity here)

```
POST /api/v1/ai/assessor/chat
  { "query": string, "conversation_id": string | null }

POST /api/v1/ai/compliance/triage
  { "conversation_id": string | null }
  (incident_log is built server-side from compliance_gaps table, not sent by frontend)

POST /api/v1/ai/compliance/regulatory-change
  { "circular_text": string, "conversation_id": string | null }

POST /api/v1/ai/security/cert-in-draft/{incident_id}
  { "conversation_id": string | null }
  (incident_details built server-side from incidents + incident_timeline tables)

POST /api/v1/ai/vendor/analyze-contract
  { "vendor_id": string, "contract_text": string, "conversation_id": string | null }

POST /api/v1/ai/policy/analyze/{policy_id}
  { "conversation_id": string | null }
  (policy_content pulled server-side from generated_policies table;
   internally fans out to conflict-detect + executive-summary in parallel)
```

`policy/analyze/{policy_id}` response is a wrapped composite, not a bare `execute()` result:

```json
{
  "executive_summary": { /* one of the 6 shapes above */ },
  "conflicts": { /* one of the 6 shapes above */ }
}
```

Each of `executive_summary` and `conflicts` independently follows the six-shape contract — they can be in different branches simultaneously (e.g. conflicts succeeds, summary hits `LLM_ERROR`), since `asyncio.gather` runs them independently and neither's failure affects the other's shape.

---

### 4. Known defect — flagging, not documenting as if it were reliable

`backend/app/routers/ai/vendor.py` contains extraction helpers that assume fields which **do not exist anywhere in the actual contract**:

```python
def _extract_risk_level(result: dict[str, Any]) -> str | None:
    risk_level = result.get("risk_level") or result.get("severity")
    ...
```

Neither `risk_level` nor `severity` is ever present in `execute()`'s output — the only keys are `role, response, citations, query_type, chunks_used, error`. The function's only functioning path is its fallback: regex/substring-matching keywords like `"high risk"` inside the free-text `response` string. Same applies to `_extract_dpdp_compliant()`, which checks a `dpdp_compliant` key that never exists — this function has no working path at all beyond returning `None`.

**Practical impact:** rows written to `vendor_risk_assessments.risk_level` and `.dpdp_compliant` are either keyword-matched guesses from free text, or `null`, not a structured signal from the AI service. This should not be presented to Compliance/Vendor Reviewer UIs as a reliable structured field until one of these is done:

- **Option A:** Add explicit structured fields to `VendorAgent.analyze_contract()` (would require either a second, non-`execute()`-routed code path, or extending `execute()` itself to optionally return extra structured fields — the latter would affect all 5 agents, so needs care)
- **Option B:** Accept the keyword-matching approach as a known, documented limitation and surface it as "AI-suggested, unverified" in the UI rather than a definitive value

This is a decision to raise with whoever owns the AI service, not something resolvable purely at the documentation layer.

---

### 5. What this doc does not cover

- The internal RAG pipeline (`HybridRetriever`, `ConfidenceScorer`, `CrossReferenceInjector` etc.) — not needed for the frontend/backend-proxy contract, only `execute()`'s output matters for consumers.
- Streaming behavior — `forward_to_ai_service` uses a single blocking `httpx` POST with a 45s timeout, no SSE/streaming observed. If any AI panel expects token-by-token streaming, that is not currently implemented and would be a separate, larger change.
- Error responses from `forward_to_ai_service`'s own layer (401/403/429/503/500+/timeout) — these are HTTP-level `HTTPException`s raised before the six-shape contract above even applies, and are already handled distinctly in `proxy.py`. Do not confuse these with the `error` key inside a 200 response — they are a separate failure mode at a different layer.