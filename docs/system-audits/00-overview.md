# System Implementation Audit - Overview

Status markers:

- Implemented: present in the repository and wired into the app.
- Partially Implemented: present but incomplete, inconsistent, mocked, or missing production guardrails.
- Not Implemented: requested capability is absent from the inspected code.

This audit is based on the current repository structure under `frontend`, `backend/app`, `backend/ai_service`, `schema.sql`, and the visible documentation/configuration files.

## System Shape

Implemented:

- React/Vite frontend in `frontend/src`.
- Main FastAPI API in `backend/app/main.py`.
- Separate FastAPI AI service in `backend/ai_service/main.py`.
- PostgreSQL schema in `schema.sql`.
- MongoDB helpers in `backend/app/mongodb.py` and storage abstractions in `backend/app/storage`.
- Supabase storage client in `backend/app/supabase_client.py`.
- Root scripts in `package.json` for frontend, main API, and AI service.

Partially Implemented:

- AI routes are exposed both through `backend/app/routers/ai` proxy routes and directly by `backend/ai_service/routers`.
- Some frontend pages are connected to APIs, while others are shell/dashboard pages or use derived/mock-like summaries.
- README and comments drift from code: README references OpenAI, while the current AI service uses Gemini through `langchain-google-genai`.

Not Implemented:

- Automated test suite was not found.
- CI/CD configuration was not found.
- Production deployment configuration was not found.

## Major Modules

| Module | Current Status | Evidence |
|---|---|---|
| Authentication | Implemented | `backend/app/routers/auth.py`, `backend/app/services/auth_service.py`, `frontend/src/lib/auth.ts` |
| Security Interceptor & Auth Exclusions | Implemented | `frontend/src/lib/api.ts` excludes `/login`, `/register`, `/refresh` from 401 refresh loops |
| Self Password Change & Admin Reset | Implemented | `POST /api/v1/auth/change-password`, `POST /api/v1/users/{user_id}/reset-password` |
| MAC Address Audit Tracking | Implemented | `mac_address` column in `audit_logs`, `getClientMacAddress()` fingerprinting, 5-tier backend pipeline |
| Post-Login CRUD Audit Logging | Implemented | `AuditLogRepository.write` in all CRUD endpoints across institutions, users, depts, calendar |
| RBAC | Implemented | `backend/app/domain/rbac.py`, `backend/app/core/permissions.py`, `frontend/src/routes/RoleRoute.tsx` |
| Session handling | Implemented | `backend/app/repositories/sessions.py`, `user_sessions` table |
| Tenant Cascade Deletion | Implemented | `DELETE /api/v1/institutions/{id}` deletes tenant & all dependent FK records |
| Compliance controls & Dynamic Score | Implemented | `backend/app/routers/controls.py`, `institutions.py` dynamic framework scoring |
| Assessments and gaps | Implemented | `backend/app/routers/assessments.py`, `backend/app/routers/gaps.py` |
| Evidence upload | Implemented | `backend/app/routers/evidence.py` |
| Incidents | Implemented | `backend/app/routers/incidents.py` |
| Vendors | Implemented | `backend/app/routers/vendors.py` |
| Policies | Implemented | `backend/app/routers/policies.py` |
| Audit workspace & AI Smart Sampling | Implemented | `backend/app/routers/audit.py`, `backend/app/routers/ai/audit.py` |
| Notifications | Implemented | `backend/app/routers/notifications.py`, `backend/app/repositories/notification.py` |
| AI/RAG | Implemented | `backend/ai_service/rag`, `backend/ai_service/agents` |
| MongoDB document storage | Implemented | helper CRUD exists; evidence metadata/extracted-text writes are wired |

## Verification Results

Commands run during audit:

- `python -m compileall backend`: passed.
- `npm.cmd run typecheck`: passed.
- `npm.cmd run lint`: failed with 76 errors and 10 warnings, mostly unused imports, `any`, and hook dependency warnings.
- `rg --files -g "*test*" -g "*spec*"`: no test/spec files found.

## High-Risk Findings

1. No automated test suite or CI/CD configuration was found.
2. Role assumption start flow is absent, and any valid but unauthorized `user_sessions.active_role_id` value would be trusted until an exit/reset path corrects it.
3. Notifications backend remains empty while frontend notification/pending UI exists.
4. Production report generation remains basic record generation rather than a complete document pipeline.
5. Evidence-to-RAG/Supabase KB ingestion still needs an explicit production flow.
