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
| Authentication | Partially Implemented | `backend/app/routers/auth.py`, `backend/app/services/auth_service.py`, `frontend/src/lib/auth.ts` |
| RBAC | Implemented | `backend/app/domain/rbac.py`, `backend/app/core/permissions.py`, `frontend/src/routes/RoleRoute.tsx` |
| Session handling | Implemented | `backend/app/repositories/sessions.py`, `user_sessions` table |
| Role assumption exit | Partially Implemented | `AuthService.exit_role_assumption`; no matching assume endpoint found |
| Compliance controls | Implemented | `backend/app/routers/controls.py` |
| Assessments and gaps | Partially Implemented | `backend/app/routers/assessments.py`, `backend/app/routers/gaps.py` |
| Evidence upload | Partially Implemented | `backend/app/routers/evidence.py` |
| Incidents | Implemented | `backend/app/routers/incidents.py` |
| Vendors | Implemented | `backend/app/routers/vendors.py` |
| Policies | Partially Implemented | `backend/app/routers/policies.py` |
| Audit workspace | Partially Implemented | `backend/app/routers/audit.py` |
| Notifications | Not Implemented | Empty router in `backend/app/routers/notifications.py` |
| AI/RAG | Partially Implemented | `backend/ai_service/rag`, `backend/ai_service/agents` |
| MongoDB document storage | Partially Implemented | helpers exist; limited route usage found |

## Verification Results

Commands run during audit:

- `python -m compileall backend`: passed.
- `npm.cmd run typecheck`: passed.
- `npm.cmd run lint`: failed with 76 errors and 10 warnings, mostly unused imports, `any`, and hook dependency warnings.
- `rg --files -g "*test*" -g "*spec*"`: no test/spec files found.

## High-Risk Findings

1. Login lockout behavior is inconsistent. `AuthService` uses `_BLOCK_SECONDS = 5`, while comments/UI describe five minutes. It also raises `UnauthorizedError` instead of `LockedError`, while the frontend expects 423/429 behavior.
2. Refresh tokens are stored in `localStorage` despite comments suggesting HttpOnly cookies.
3. AI service CORS allows `*` with credentials in `backend/ai_service/main.py`.
4. Main AI proxy and AI service route permissions disagree in some places, especially compliance triage and regulatory change.
5. Evidence upload reads the full file into memory and writes to local disk without size/type/security validation.
6. There are duplicate or stale route artifacts such as `frontend/src/routes/index.tsx` alongside the active `AppRouter.tsx`.

