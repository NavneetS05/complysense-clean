# API Inventory Audit

Base prefix for main API: `/api/v1`.

## Authentication

| Method | Route | Router | Auth | Status |
|---|---|---|---|---|
| POST | `/auth/register` | `auth.py` | Public | Implemented |
| POST | `/auth/login` | `auth.py` | Public | Implemented |
| POST | `/auth/logout` | `auth.py` | Bearer/session | Implemented |
| POST | `/auth/refresh` | `auth.py` | HttpOnly refresh cookie | Implemented |
| POST | `/auth/change-password` | `auth.py` | Bearer/session | Implemented |
| GET | `/auth/me` | `auth.py` | Bearer/session | Implemented |
| PATCH | `/auth/me` | `auth.py` | Bearer/session | Implemented |
| POST | `/auth/forgot-password` | `auth.py` | Public | Implemented |
| POST | `/auth/reset-password` | `auth.py` | Reset token | Implemented |
| GET | `/auth/validate-reset-token` | `auth.py` | Public token check | Implemented |
| POST | `/auth/exit-role-assumption` | `auth.py` | Bearer/session | Partially Implemented |

## RBAC and Modules

| Method | Route | Status |
|---|---|---|
| GET | `/rbac/roles` | Implemented |
| GET | `/rbac/matrix` | Implemented |
| GET | `/modules` | Implemented |

## Core Operational APIs

| Router | Main routes | Status |
|---|---|---|
| `institutions.py` | `/institutions`, `/status`, `/stats`, `DELETE /institutions/{id}` | Implemented |
| `users.py` | `/users`, `/users/invite`, `POST /users/{id}/reset-password`, role/status paths | Implemented |
| `departments.py` | `/departments...` | Implemented |
| `controls.py` | `/controls`, detail, status, notes | Implemented |
| `assessments.py` | `/assessments`, responses, submit | Implemented; submit is idempotent for derived result/gap rows |
| `assessor.py` | `/assessor/dashboard-stats`, `/assessor/top-risks`, conversation history reads | Implemented read-only |
| `gaps.py` | `/gaps`, detail | Implemented |
| `evidence.py` | `/evidence`, upload, detail, review | Implemented for validated upload, metadata, and review transition |
| `incidents.py` | `/incidents`, stats, detail, update | Implemented |
| `vendors.py` | `/vendors`, detail, create, update, risk-assessment upsert | Implemented |
| `tasks.py` | `/tasks`, detail, create, update, submit | Implemented |
| `policies.py` | `/policies`, content, approve/reject, reports wrapper | Implemented for approval lifecycle and redraft versioning |
| `audit.py` | `/audit/recent`, `/logs` (with live MAC tracking), observations, reports | Implemented |
| `calendar.py` | `/calendar...` | Implemented |
| `notifications.py` | `/notifications`, `/read`, `/read-all` | Implemented |

## AI Proxy APIs

| Method | Route | Purpose | Status |
|---|---|---|---|
| POST | `/ai/compliance/triage` | Triage open gaps | Implemented; permission-aligned |
| POST | `/ai/compliance/regulatory-change` | Analyze circular against posture | Implemented; permission-aligned |
| POST | `/ai/security/cert-in-draft/{incident_id}` | Draft CERT-In report | Partially Implemented |
| POST | `/ai/audit/smart-sample` | Smart evidence sample | Canonical implementation |
| POST | `/ai/audit/draft-observation` | Draft audit observation | Canonical implementation |
| POST | `/ai/policy/analyze/{policy_id}` | Analyze policy | Partially Implemented |
| POST | `/ai/vendor/analyze-contract` | Analyze vendor contract and persist risk assessment | Implemented |
| POST | `/ai/assessor/chat` | Read-only assessor Q&A | Implemented; permission-aligned |
| GET | `/ai/dept/translate/{control_id}` | Translate control | Partially Implemented |
| POST | `/ai/dept/preflight-check` | Evidence preflight | Partially Implemented |
| POST | `/ai/admin/risk-heatmap` | Risk heatmap | Partially Implemented |

## Validation

Implemented:

- Pydantic models on most create/update payloads.

Partially Implemented:

- Some fields still accept raw strings for dates/status/severity outside the remediated routers.
- Evidence upload has size/type validation, streaming writes, a malware-scan hook, and MongoDB metadata/extracted-text writes; full AV integration remains an operational dependency.
