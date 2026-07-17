# ComplySense Backend Contract
## Addendum — Institutions, Department AI, Admin Risk-Heatmap, and the /chat Pattern

This extends `ai-response-contract.md`. Nothing here changes that doc's six-shape
contract — it adds endpoints that were missed in the first pass, plus two
endpoints that fall outside the shared contract entirely.

---

### 1. Missed endpoint class — every role also has a generic `/chat`

The original AI contract doc documented only the primary task endpoint per role
(triage, cert-in-draft, analyze-contract, conflict-detect, executive-summary,
assessor chat). It missed that **every** `ai_service` router also exposes a
generic conversational endpoint, all routing through the same `execute()` and
therefore the same six-shape contract already documented:

| Endpoint | File | Permission gate |
|---|---|---|
| `POST /compliance/chat` | `ai_service/routers/compliance.py` | `VIEW_CONTROLS` |
| `POST /security/chat` | `ai_service/routers/security.py` | `VIEW_CONTROLS` |
| `POST /vendor/chat` | `ai_service/routers/vendor.py` | `VIEW_CONTROLS` |
| `POST /audit/chat` | `ai_service/routers/audit.py` | `VIEW_CONTROLS` |
| `POST /dept/chat` | `ai_service/routers/dept.py` | `VIEW_CONTROLS` |

No corresponding backend-proxy wrapper (`backend/app/routers/ai/*.py`) has been
confirmed for any of these `/chat` variants except where already documented
(assessor). If the frontend needs any of these, a proxy route doesn't yet exist
for it and would need to be added — same pattern as the other proxies.

---

### 2. Two agent-construction patterns exist — not a defect, but worth naming

Six roles use a **named subclass** of `BaseAgent` (`AssessorAgent`,
`ComplianceAgent`, `SecurityAgent`, `VendorAgent`, `PolicyAgent`, `AuditAgent`),
each wrapping `execute()` with role-specific method names and task prompts.

Two places use **raw `BaseAgent` instantiation** with no subclass at all:

- `ai_service/routers/dept.py` — `_agent = BaseAgent(role="dept_reviewer", endpoint_name="translate_control")`, module-level singleton, reused across all three of its routes (`translate-control`, `preflight-check`, `chat`).
- `ai_service/routers/digest.py` — constructs a **new** `BaseAgent` per request, with `role` set dynamically from `user_ctx.active_role_name` rather than a fixed string. This is the only agent construction in the codebase that is role-adaptive at request time rather than fixed at router-load time.

Both patterns produce the same six-shape response — there's no functional
difference to the frontend. The difference is purely internal: dept has no
dedicated agent class (no custom methods, just inline `execute()` calls with
different prompts per route), and digest is the only per-request dynamic-role
construction in the system.

---

### 3. `POST /dept/translate-control` and `POST /dept/preflight-check`

Both confirmed to route through `BaseAgent.execute()` — inherits the exact
six-shape contract already documented in `ai-response-contract.md` section 2.
No special-casing needed beyond noting these use the no-subclass pattern above.

**Request shapes (from backend proxy, `backend/app/routers/ai/dept.py`):**

```
GET /api/v1/ai/dept/translate/{control_id}
  (no body — control_id from path; backend fetches control_text server-side
   from control_assignments.notes)
  Cached 7 days via in-memory TTL cache in the backend proxy layer —
  NOT in ai_service. Cache key: "translate:{control_id}:en"

POST /api/v1/ai/dept/preflight-check
  {
    "control_id": string,
    "file_name": string,
    "file_size_kb": int,
    "mime_type": string,
    "file_content_preview": string,
    "conversation_id": string | null
  }
```

Note: the backend proxy's in-memory cache for translate-control is
process-local — it will not survive a restart and will not be shared across
multiple backend instances if the API is ever horizontally scaled. If that
matters for your deployment, this cache needs to move to Redis (the stack
already has Redis available per the project's documented architecture).

---

### 4. `GET /api/v1/institutions/anomaly-alerts` — confirmed to be a static mock, not AI-generated

Despite the summary "Get active AI-detected platform anomalies," this endpoint
has no AI service call at all. It returns a hardcoded single-item array:

```json
{
  "alerts": [
    {
      "id": "alert-1",
      "severity": "amber",
      "message": "AI Alert: Unusual admin activity detected at Jaipur National University — 14 role changes in the last hour.",
      "timestamp": "2 minutes ago",
      "link": "/super-admin/audit-trail?action_type=role_changed"
    }
  ]
}
```

`severity` values seen: `"amber"` — no enum enforced in code, so other values
are possible but unconfirmed. `link` is a relative frontend route, not an API
path. This is explicitly a placeholder ("Mocking AI anomaly alert banner
response as specified in specs") — worth flagging plainly: if this ships to
production as-is, the Super Admin dashboard will always show this exact
hardcoded message regardless of actual platform activity. Not a bug, but a
known stub that should be tracked as a real "AI-detected anomaly" feature to
build, not documented as if it already works.

**Verification, not assumption:** the code shown is unambiguous — a literal
hardcoded dict with no query, no AI call, no variable input. There is nothing
left to verify about *whether* it's a stub. What's unverified is whether the
Super Admin dashboard frontend already displays this and whether anyone has
signed off on it going live in this state. That's a product question for you,
not something further code-reading resolves.

---

### 5. `GET /api/v1/institutions/stats`

Confirmed real, but with silent fallbacks baked in:

```json
{
  "total_institutions": int,
  "active_users": int,
  "weekly_incidents": int,
  "avg_compliance": float
}
```

- `weekly_incidents`: real query against `incidents` table, but falls back to
  hardcoded `2` if the query throws for any reason (bare `except Exception`).
- `avg_compliance`: real query against `control_assignments`, falls back to
  hardcoded `74.0` on any exception, and the query itself defaults to `74.0`
  via SQL `coalesce` if there are literally zero rows.

Same caution as anomaly-alerts: these numbers can silently be fabricated
defaults rather than real zero/empty states, and nothing in the response
distinguishes "real data" from "fallback fired." If this matters for
compliance-reporting integrity, the fallback should either be removed (let the
500 propagate) or the response should include a flag indicating a fallback
was used.

**Verification, not assumption:** the `except Exception: weekly_incidents = 2`
and `except Exception: pass` (leaving `avg_compliance` at its pre-set `74.0`)
are both directly visible in the pasted source — not inferred. What's
unverified is *how often* these except blocks actually fire in practice (e.g.
does the `incidents` table reliably exist in every environment, or does this
fallback trigger routinely). That would need a runtime check (logs, or
deliberately breaking the query in a test environment) — not something
resolvable from source alone.

---

### 6. `GET /api/v1/institutions/dashboard` — confirmed real, no mock fallback

Unlike the two above, this one (Institution Admin dashboard) is a full,
straightforward set of real queries — gap stats, overdue controls, incident
counts, framework compliance trend with computed `up`/`down`/`flat` trend
labels, department scores, and a genuine top-5 open-gaps list reused as
`ai_risks` (despite the name, this is a direct SQL query, not an AI call —
same naming looseness as the anomaly-alerts endpoint, worth being aware of
when reading the field name literally).

---

### 7. `POST /admin/reindex` and `GET /admin/diagnostics` (ai_service side) — not part of the six-shape contract, infra-only

These are internal RAG-maintenance endpoints, gated by a static `X-Admin-Key`
header (not user JWT auth, not `PermissionKey`-based). They do not go through
`BaseAgent.execute()` at all — separate code path entirely. Mentioned here only
so they aren't mistaken for missing role-facing functionality; they're
operational tooling for whoever manages the knowledge base index, not
something the ComplySense frontend calls.

---

### 8. `POST /digest/generate` — included, but flagged UNVERIFIED against frontend

This endpoint exists and is fully wired (routes through `execute()`, same
six-shape contract, request body `{ context: string | null, conversation_id }`).
It was not part of the original frontend audit or any role UI spec reviewed so
far, and — critically — **no backend proxy route
(`backend/app/routers/ai/*.py`) has been shown to exist for it at all.**
Every other `ai_service` endpoint has a matching proxy in `backend/app/routers/ai/`
that the frontend actually calls; this one does not, based on everything shown
so far. That absence is itself a signal, not proof — the proxy file may simply
not have been included in what's been shared.

**Do not treat this as a working feature until verified.** Two outcomes are
possible: (a) no proxy exists, no frontend calls it, and this is unused/
half-built code sitting in `ai_service` with no way to reach it from the
product today — safe to ignore or flag for cleanup; or (b) a proxy exists that
simply hasn't been shown yet, in which case this needs the same contract
treatment as every other endpoint in this doc.

**Verification needed (not yet run):**
```
Paste RAW FACTS only. Say "NOT FOUND" if missing.

1. Search the entire backend/app/routers/ folder (including ai/ subfolder)
   for any call to "/digest/generate" or forward_to_ai_service("/digest...".
   Paste the file and function if found, or say NOT FOUND.

2. Search the entire frontend/src folder for any string match on "digest"
   (case-insensitive) — component names, API calls, route paths. List every
   file that matches, or say NOT FOUND.

3. If neither is found, confirm: is there any reference to a "digest" or
   "morning summary" feature anywhere in docs/ or the UI spec documents?
```

Until this comes back, treat `/digest/generate` as **unreachable from the
product** and exclude it from any frontend-facing contract commitments.