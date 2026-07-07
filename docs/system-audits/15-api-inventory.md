# API Inventory Audit

Base prefix for main API: `/api/v1`.

## Authentication

| Method | Route | Router | Auth | Status |
|---|---|---|---|---|
| POST | `/auth/register` | `auth.py` | Public | Implemented |
| POST | `/auth/login` | `auth.py` | Public | Partially Implemented |
| POST | `/auth/logout` | `auth.py` | Bearer/session | Implemented |
| POST | `/auth/refresh` | `auth.py` | Refresh token payload | Implemented |
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
| GET | `/rbac/matrix` | Partially Implemented |
| GET | `/modules` | Implemented |

## Core Operational APIs

| Router | Main routes | Status |
|---|---|---|
| `institutions.py` | `/institutions...` | Implemented/Partially Implemented |
| `users.py` | `/users`, `/users/invite`, role/status/reset paths | Partially Implemented |
| `departments.py` | `/departments...` | Implemented |
| `controls.py` | `/controls`, detail, status, notes | Implemented |
| `assessments.py` | `/assessments`, responses, submit | Partially Implemented |
| `gaps.py` | `/gaps`, detail | Implemented |
| `evidence.py` | `/evidence`, upload, detail | Partially Implemented |
| `incidents.py` | `/incidents`, stats, detail, update | Implemented |
| `vendors.py` | `/vendors`, detail, create, update | Partially Implemented |
| `tasks.py` | `/tasks`, detail, create, update, submit | Implemented |
| `policies.py` | `/policies`, content, reports | Partially Implemented |
| `audit.py` | `/audit/recent`, `/logs`, observations, reports | Partially Implemented |
| `calendar.py` | `/calendar...` | Implemented |
| `notifications.py` | `/notifications` | Not Implemented |

## AI Proxy APIs

| Method | Route | Purpose | Status |
|---|---|---|---|
| POST | `/ai/compliance/triage` | Triage open gaps | Partially Implemented |
| POST | `/ai/compliance/regulatory-change` | Analyze circular against posture | Partially Implemented |
| POST | `/ai/security/cert-in-draft/{incident_id}` | Draft CERT-In report | Partially Implemented |
| POST | `/ai/audit/smart-sample` | Smart evidence sample | Partially Implemented |
| POST | `/ai/audit/draft-observation` | Draft audit observation | Partially Implemented |
| POST | `/ai/policy/analyze/{policy_id}` | Analyze policy | Partially Implemented |
| POST | `/ai/vendor/analyze-contract` | Analyze vendor contract | Partially Implemented |
| GET | `/ai/dept/translate/{control_id}` | Translate control | Partially Implemented |
| POST | `/ai/dept/preflight-check` | Evidence preflight | Partially Implemented |
| POST | `/ai/admin/risk-heatmap` | Risk heatmap | Partially Implemented |

## Validation

Implemented:

- Pydantic models on most create/update payloads.

Partially Implemented:

- Many fields accept raw strings for dates/status/severity instead of enums.
- Evidence upload validation is weak.

