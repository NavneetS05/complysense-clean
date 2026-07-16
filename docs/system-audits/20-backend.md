# Backend Implementation Audit

Backend roots:

- Main API: `backend/app`.
- AI service: `backend/ai_service`.

## Main FastAPI Application

Implemented:

- Entry point: `backend/app/main.py`.
- App factory: `create_app`.
- Lifespan closes MongoDB client on shutdown.
- CORS uses `settings.cors_origins`.
- Exception handlers registered through `backend/app/core/exceptions.py`.
- Routers are assembled by `backend/app/routers/__init__.py::build_api_router`.

## Configuration

Implemented:

- Main settings: `backend/app/config.py`.
- AI settings: `backend/ai_service/config.py`.
- `.env` loading uses `env_file="../.env"` relative to backend working directory.

Configuration areas:

- PostgreSQL `database_url`.
- MongoDB URI/database/collection names.
- Supabase URL/service key/bucket.
- JWT secret/algorithm/expiry.
- SMTP credentials.
- Main API URL and AI service URL.
- Gemini API key.

## Database Layer

Implemented:

- SQLAlchemy async engine/session in `backend/app/database.py`.
- PostgreSQL health check.
- MongoDB Motor client in `backend/app/mongodb.py`.
- Supabase client in `backend/app/supabase_client.py`.

Partially Implemented:

- Repositories exist for auth/RBAC/session/audit/users.
- Many routers still execute raw SQL directly instead of routing through repositories.

## Core Modules

Implemented:

- `core/security.py`: password hashing, JWT creation/decoding, reset token generation.
- `core/deps.py`: current-user resolution.
- `core/permissions.py`: permission guard dependency.
- `core/exceptions.py`: custom application errors.
- `core/logging.py`: structured logging setup.

Implemented:

- Login lockout uses a 5-minute `_BLOCK_SECONDS` value and raises `LockedError` with HTTP 423 and `blocked_until`.

## Routers

Implemented or partially implemented routers:

- `auth.py`
- `rbac.py`
- `modules.py`
- `institutions.py`
- `users.py`
- `departments.py`
- `compliance.py`
- `controls.py`
- `assessments.py`
- `evidence.py`
- `gaps.py`
- `incidents.py`
- `vendors.py`
- `tasks.py`
- `policies.py`
- `audit.py`
- `calendar.py`
- `health.py`
- `routers/ai/*`

Not implemented:

- `notifications.py` defines only an empty router.

## Services

Implemented:

- `AuthService` handles register, login, logout, refresh, password reset, validate reset token, and role assumption exit.
- `MailService` handles password reset email fallback.

Partially Implemented:

- Role assumption start is absent.
- Admin reset password endpoint simulates email rather than using `AuthService.forgot_password`.

## Repositories

Implemented:

- `repositories/users.py`
- `repositories/sessions.py`
- `repositories/rbac.py`
- `repositories/audit.py`

Partially Implemented:

- Many resource routers use direct SQL rather than repository classes.
- Transaction boundaries are route/service-specific; no unit-of-work abstraction found.

## Middleware

Implemented:

- CORS middleware in main app.

Not Implemented:

- No custom request logging middleware found.
- No rate-limit middleware found.
- No CSRF middleware found.

## Background Jobs and Schedulers

Partially Implemented:

- `backend/app/jobs.py` exists.
- `backend/app/events.py` exists.

Not confirmed:

- No scheduler registration or background worker startup was confirmed in `backend/app/main.py`.

## Logging

Implemented:

- Main API logging configuration exists.
- AI service uses `StructuredLogger`.
- Audit logs are stored in PostgreSQL.

Partially Implemented:

- Audit logging now covers critical non-auth write paths added in this remediation, but still needs automated coverage to prevent drift.

## AI Integration

Implemented:

- Main API proxy forwards AI requests to `settings.ai_service_url`.
- AI proxy forwards Authorization header.
- AI service has independent router registration and health endpoints.

- AI service depends on main app auth modules and DB-backed permissions.
- AI proxy and direct AI route permissions have been aligned for the remediated endpoints.
- Browser direct AI client exists in frontend but is unused.

## Validation

Implemented:

- Pydantic request models are used across most routers.
- Evidence review status transitions are implemented in `evidence.review_evidence` and gated by `REVIEW_EVIDENCE`.
- Policy approve/reject use dedicated `APPROVE_POLICIES` endpoints; draft/update remains separate under `DRAFT_POLICIES`.
- Policy redrafts can link to `parent_policy_id` and increment `version_number`.
- Assessment submit replaces prior generated result/gaps for the assessment before recalculating, preventing duplicate derived rows on resubmit.

Partially Implemented:

- Remediated routers now use enum validation for key status/severity fields.
- Evidence upload now validates size/type, streams file writes, calls a malware-scan hook, and writes MongoDB metadata/extracted text.

## Transactions

Implemented:

- Routes explicitly call `session.commit()` or rollback in many places.

Partially Implemented:

- Critical remediated routes now check returned rows before commit.
- Evidence upload rolls back database work and removes the streamed file if downstream metadata/audit writes fail before commit.
- Error handling consistency varies by router.

## Backend Missing Work

- Implement notifications router.
- Implement role assumption start flow.
- Add test coverage.
- Consolidate repeated SQL into repositories where useful.
- Add rate limiting for auth and sensitive endpoints.
- Add production report generation.
