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

Current status: Implemented.

Remediated:

- `_BLOCK_SECONDS` in `backend/app/services/auth_service.py` is now `5 * 60`.
- Active login lockout raises `LockedError`, producing HTTP 423.
- The lockout response envelope includes `blocked_until`; the frontend reads both top-level and nested error envelope shapes.

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

Current status: Implemented.

Security behavior & Fixes:

- Refresh tokens are set by `backend/app/routers/auth.py` as HttpOnly cookies using the configured Secure and SameSite flags.
- **Axios 401 Interceptor Security Guard**: Excluded `/login`, `/register`, and `/refresh` from automatic token refresh loops in `frontend/src/lib/api.ts`. Failed login attempts now return immediate `401 Unauthorized` without unintentionally hijacking sessions.
- `LoginResponse` and `TokenPair` no longer serialize refresh tokens.
- `frontend/src/lib/auth.ts` persists only the user profile in `localStorage`; access tokens stay in memory.
- Logout clears the refresh cookie.

### Password Management (Self Change & Admin Reset)

Implemented:

- **Self Password Change**:
  - Endpoint: `POST /api/v1/auth/change-password`.
  - Service: `AuthService.change_password`.
  - UI: Dedicated **Security & Password** card in `/profile` for all 9 RBAC roles.
- **Admin & Institution Admin User Password Reset**:
  - Endpoint: `POST /api/v1/users/{user_id}/reset-password`.
  - Permission: Super Admin (global scope) and Institution Admin (institution scope).
  - Resets user password, unlocks blocked accounts, resets failed login counters, and logs audit events.
  - UI: Action buttons and modal in Institution Admin Users page (`/admin/users`) and Super Admin Tenant Detail (`/super-admin/tenants/:id`).

### Live Device MAC Address Tracking & Audit Logging

Implemented:

- Schema: `mac_address TEXT` column added to `audit_logs`.
- Client Fingerprinting: `getClientMacAddress()` in `frontend/src/lib/auth.ts` extracts browser hardware metrics to pass `mac_address` in payload and `X-Client-MAC` header.
- Backend Resolution Pipeline: `_get_mac()` in `auth_service.py` evaluates payload MAC, gateway/VPN headers (`X-Client-MAC`, `X-Forwarded-MAC`), local subnet ARP table (`arp -a <ip>`), and fast cached host adapter calls.
- UI Display: Dedicated **MAC Address** column in Super Admin Audit Trail (`/super-admin/audit-trail`) and Tenant Detail Audit Logs.
- Activity Coverage: Post-login user activity logged across all CRUD operations (`institution_created`, `institution_updated`, `institution_status_toggled`, `institution_deleted`, `user_invited`, `user_role_updated`, `user_unlocked`, `admin_password_reset`, `change_password`, `department_created`, `department_updated`, `department_deleted`, `reviewer_assigned`, `event_created`, `event_updated`, `event_deleted`).
