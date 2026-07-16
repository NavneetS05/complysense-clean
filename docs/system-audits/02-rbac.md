# RBAC Audit

## RBAC Model

Implemented:

- Roles are defined in `backend/app/domain/rbac.py::RoleName`.
- Permissions are defined in `backend/app/domain/rbac.py::PermissionKey`.
- Runtime permissions are loaded from PostgreSQL through `RbacRepository.permissions_for_role`.
- Backend route guard is `require_permission(permission)`.
- Frontend route guard is `RoleRoute`.
- Frontend menu visibility is centralized in `frontend/src/components/shared/Sidebar.tsx`.

PostgreSQL:

- `roles`
- `permissions`
- `role_permissions`
- `allowed_role_transitions`
- `role_assumption_sessions`
- `user_sessions.active_role_id`

Current status: Implemented.

## Roles

| Role | Frontend route prefix | Menu source | Current status |
|---|---|---|---|
| Super Admin | `/super-admin` | `NAV_MAP` | Implemented |
| Institution Admin | `/admin` | `NAV_MAP` | Implemented |
| Compliance Officer | `/compliance` | `NAV_MAP` | Implemented |
| IT Security Officer | `/security` | `NAV_MAP` | Implemented |
| Auditor | `/auditor` | `NAV_MAP` | Implemented |
| Department Reviewer | `/dept` | `NAV_MAP` | Implemented |
| Vendor Reviewer | `/vendor` | `NAV_MAP` | Implemented |
| Policy Approver | `/policy` | `NAV_MAP` | Implemented |
| Read-Only Assessor | `/assessor` | `NAV_MAP` | Implemented |

## Backend Guards

Implemented:

- Core API routes use `require_permission` or `get_current_user`.
- Example: `controls` uses `VIEW_CONTROLS` and `MANAGE_CONTROLS`.
- Example: `incidents` uses `VIEW_INCIDENTS` and `MANAGE_INCIDENTS`.
- Example: `audit` uses `VIEW_AUDIT_TRAIL`, `VIEW_AUDIT_REPORTS`, `ADD_AUDIT_OBSERVATIONS`, `GENERATE_AUDIT_REPORTS`.

Partially Implemented:

- Some routes still use direct permission checks or mixed styles instead of a uniform `require_permission` dependency.
- The remediated AI proxy/direct service routes are aligned, but future AI routes should include permission parity checks.

## Frontend Guards

Implemented:

- `ProtectedRoute` blocks unauthenticated access.
- `RoleRoute` checks `active_role_name ?? role_name`.
- Sidebar uses active role for menu selection.

Issue:

- If a user with an assumed role fails a `RoleRoute`, redirect uses `roleDashboard(user.role_name)` instead of active role dashboard. This may be intentional but can conflict with role assumption UX.

## Role Assumption

Partially Implemented:

- Session model supports `active_role_id`.
- `AuthService.exit_role_assumption` resets active role to primary role.
- `PermissionKey.USE_ROLE_ASSUMPTION` exists.
- `allowed_role_transitions` and `role_assumption_sessions` tables exist.

Not Implemented:

- No backend endpoint that starts role assumption was found.
- No service method that inserts `role_assumption_sessions` was found.

## RBAC API

Implemented:

- `GET /api/v1/rbac/roles`
- `GET /api/v1/rbac/matrix`

Partially Implemented:

- `/rbac/matrix` contains fallback static behavior if DB mappings are missing. Useful for development, but risky if production data seeding fails because the UI can appear functional while DB authorization is incomplete.
