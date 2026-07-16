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
| RBAC | Implemented | `backend/app/domain/rbac.py`, `backend/app/core/permissions.py`, `frontend/src/routes/RoleRoute.tsx` |
| Session handling | Implemented | `backend/app/repositories/sessions.py`, `user_sessions` table |
| Role assumption exit | Partially Implemented | `AuthService.exit_role_assumption`; no matching assume endpoint found |
| Compliance controls | Implemented | `backend/app/routers/controls.py` |
| Assessments and gaps | Partially Implemented | `backend/app/routers/assessments.py`, `backend/app/routers/gaps.py` |
| Evidence upload | Implemented for upload validation and metadata writes | `backend/app/routers/evidence.py` |
| Incidents | Implemented | `backend/app/routers/incidents.py` |
| Vendors | Implemented | `backend/app/routers/vendors.py` |
| Policies | Partially Implemented | `backend/app/routers/policies.py` |
| Audit workspace | Partially Implemented | `backend/app/routers/audit.py` |
| Notifications | Not Implemented | Empty router in `backend/app/routers/notifications.py` |
| AI/RAG | Partially Implemented | `backend/ai_service/rag`, `backend/ai_service/agents` |
| MongoDB document storage | Partially Implemented | helper CRUD exists; evidence metadata/extracted-text writes are wired |

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
