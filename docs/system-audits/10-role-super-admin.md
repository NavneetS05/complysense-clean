# Role Audit - Super Admin

## Overview

Purpose: manage tenants/institutions, inspect audit trail, and view roles/permissions.

Frontend route file: `frontend/src/routes/SuperAdminRoutes.tsx`.

Sidebar entries: Dashboard, Tenants, Audit Trail, Roles & Permissions.

Current status: Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/super-admin/dashboard` | `Dashboard.tsx` | Connected to `/institutions/stats` & `/institutions/anomaly-alerts` |
| Tenants | `/super-admin/tenants` | `Tenants.tsx` | Connected to institutions APIs with Add Institution Modal & Delete Tenant Modal |
| Tenant Detail | `/super-admin/tenants/:institution_id` | `TenantDetail.tsx` | Connected to institution detail APIs, Users tab (with User Invite & Reset Password Modals), Audit tab (with MAC Address column) |
| Audit Trail | `/super-admin/audit-trail` | `AuditTrail.tsx` | Connected to audit logs with live MAC Address column, user search, institution filter, and CSV download |
| Roles | `/super-admin/roles` | `Roles.tsx` | Connected to RBAC matrix |

## Permissions

Backend permissions:

- `MANAGE_INSTITUTIONS`
- `VIEW_AUDIT_TRAIL`
- `VIEW_ROLES`

## Database Usage

PostgreSQL:

- `institutions`
- `users`
- `roles`
- `permissions`
- `role_permissions`
- `audit_logs` (with `mac_address` column and post-login CRUD activity tracking)
- operational aggregate reads from compliance/task/audit tables depending on institutions router endpoints.

MongoDB:

- No direct Super Admin MongoDB usage found.

## Implemented Enhancements & Features

- **Permanent Tenant Cascade Deletion**: Super Admin can permanently delete an institution and all dependent FK records via `DELETE /api/v1/institutions/{institution_id}` and UI modal in `/super-admin/tenants`.
- **Global User Password Reset**: Super Admin can reset any platform user's password via `POST /api/v1/users/{user_id}/reset-password`.
- **User Creation & Invite**: Modal UI in `/super-admin/tenants/:id` Users tab allows creating tenant users.
- **Live Device MAC & Activity Audit Logging**: Super Admin Audit Trail tracks real live client MAC addresses and all post-login user CRUD operations (`institution_created`, `institution_status_toggled`, `user_invited`, `admin_password_reset`, `department_created`, `event_created`).

