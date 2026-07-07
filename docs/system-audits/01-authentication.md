# Authentication and Authorization Audit

## Authentication Flow

### Login

Implemented:

- Frontend login page: `frontend/src/pages/auth/Login.tsx`.
- API helper: `frontend/src/lib/auth.ts` uses `POST /api/v1/auth/login`.
- Backend route: `backend/app/routers/auth.py::login`.
- Service logic: `backend/app/services/auth_service.py::AuthService.login`.
- User lookup: `backend/app/repositories/users.py::find_active_by_email`.
- Password verification: `backend/app/core/security.py::verify_password`.
- Session creation: `backend/app/repositories/sessions.py::create`.
- Audit log write: `AuditLogRepository.write` called from `AuthService.login`.

PostgreSQL:

- Reads `users`, `roles`, `role_permissions`, `permissions`.
- Inserts `user_sessions`.
- Inserts `audit_logs`.
- Updates `users.failed_login_attempts`, `users.blocked_until`, `users.last_login`.

Current status: Partially Implemented.

Issues:

- `_BLOCK_SECONDS = 5` in `backend/app/services/auth_service.py`, but code comments and UX describe a 5-minute lockout.
- Lockout raises `UnauthorizedError` with status 401 instead of using `LockedError` with status 423.
- Frontend expects 423/429 and `blocked_until` in `frontend/src/pages/auth/Login.tsx`, but backend returns an `error` envelope for custom errors and login currently raises `UnauthorizedError`.

### Registration

Implemented:

- Backend route: `POST /api/v1/auth/register`.
- Service: `AuthService.register`.
- Password hashing: `hash_password`.
- User insert: `UserRepository.create`.
- Session creation and audit logging after registration.

PostgreSQL:

- Reads `users`.
- Inserts `users`, `user_sessions`, `audit_logs`.

Current status: Implemented.

Gaps:

- No email verification flow was found.
- Registration accepts existing institution and role IDs but does not implement invitation-only enforcement.

### Logout

Implemented:

- Frontend helper: `logoutApi`.
- Backend route: `POST /api/v1/auth/logout`.
- Service: `AuthService.logout`.
- Deletes current `user_sessions` row.
- Writes audit log.

Current status: Implemented.

### Refresh Token

Implemented:

- Frontend interceptor: `frontend/src/lib/api.ts`.
- Backend route: `POST /api/v1/auth/refresh`.
- Service: `AuthService.refresh`.
- JWT refresh tokens include `type=refresh` and `session_id`.
- Existing session is deleted and a new session is created.

Current status: Partially Implemented.

Security concern:

- Refresh tokens are stored in `localStorage` by `persistSession` in `frontend/src/lib/auth.ts`.
- `api.ts` sets `withCredentials: true` and comments mention HttpOnly cookies, but the backend does not set refresh-token cookies in the inspected code.

### Password Reset

Implemented:

- Frontend helpers: `forgotPassword`, `validateResetToken`, `resetPassword`.
- Backend routes:
  - `POST /api/v1/auth/forgot-password`
  - `GET /api/v1/auth/validate-reset-token`
  - `POST /api/v1/auth/reset-password`
- Service: `AuthService.forgot_password`, `validate_reset_token`, `reset_password`.
- Token generation: `generate_reset_token`.
- Mail fallback: `MailService.send_password_reset`; when email delivery is unavailable, reset URL is returned.

PostgreSQL:

- Uses `password_reset_tokens`.
- Updates `users.password_hash`.
- Deletes all sessions for the user.
- Writes `audit_logs`.

Current status: Implemented for reset links, Partially Implemented for email delivery.

### Email Verification

Current status: Not Implemented.

No email verification table, token flow, or route was found.

## Session Handling

Implemented:

- Access JWT must include `type=access`, `sub`, and `session_id`.
- `get_current_user` in `backend/app/core/deps.py` decodes JWT, verifies session row, loads user context, and loads permissions for active role.
- `user_sessions` stores `user_id`, `active_role_id`, user agent, IP, and expiry.

Current status: Implemented.

## JWT

Implemented:

- Created in `backend/app/core/security.py`.
- Uses `python-jose`.
- Signed using `settings.secret_key`.
- Algorithm defaults to HS256.

Current status: Implemented.

## Cookies

Current status: Not Implemented for auth tokens.

Evidence:

- Frontend persists access and refresh tokens in `localStorage`.
- No backend `Set-Cookie` behavior was found in auth routes.

## Middleware and Guards

Implemented:

- CORS in `backend/app/main.py`.
- Auth dependency: `get_current_user`.
- Permission guard: `require_permission`.
- Frontend protected route: `frontend/src/routes/ProtectedRoute.tsx`.
- Frontend role guard: `frontend/src/routes/RoleRoute.tsx`.

Current status: Implemented.

## Authentication Providers

Current status: Not Implemented.

Only first-party email/password authentication is visible.

## Audit and Logging

Implemented:

- Auth service writes `register`, `login`, `failed_login`, `user_blocked`, `logout`, `refresh_token`, `password_reset_requested`, `password_change`, and `exit_role_assumption` events.
- Audit storage table: `audit_logs`.
- Audit repository: `backend/app/repositories/audit.py`.

Partially Implemented:

- Security logs are represented as audit log events, not a separate security log stream.
- Activity logging is inconsistent across routers; user/admin operations write some audit rows directly, while many CRUD operations do not.

