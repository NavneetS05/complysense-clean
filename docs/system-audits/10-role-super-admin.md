# Role Audit - Super Admin

## Overview

Purpose: manage tenants/institutions, inspect audit trail, and view roles/permissions.

Frontend route file: `frontend/src/routes/SuperAdminRoutes.tsx`.

Sidebar entries: Dashboard, Tenants, Audit Trail, Roles & Permissions.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/super-admin/dashboard` | `Dashboard.tsx` | Uses institution/audit summaries |
| Tenants | `/super-admin/tenants` | `Tenants.tsx` | Connected to institutions APIs |
| Tenant Detail | `/super-admin/tenants/:institution_id` | `TenantDetail.tsx` | Connected to institution detail APIs |
| Audit Trail | `/super-admin/audit-trail` | `AuditTrail.tsx` | Connected to audit logs |
| Roles | `/super-admin/roles` | `Roles.tsx` | Connected to RBAC matrix |

## Permissions

Backend permissions:

- `MANAGE_INSTITUTIONS`
- `VIEW_AUDIT_TRAIL`
- `VIEW_ROLES`
- `USE_ROLE_ASSUMPTION` exists but start flow not found.

## Database Usage

PostgreSQL:

- `institutions`
- `users`
- `roles`
- `permissions`
- `role_permissions`
- `audit_logs`
- operational aggregate reads from compliance/task/audit tables depending on institutions router endpoints.

MongoDB:

- No direct Super Admin MongoDB usage found.

## Missing Features and Improvements

- Tenant lifecycle appears API-backed, but production provisioning workflows are not fully documented in code.
- Role matrix fallback behavior can hide DB seeding problems.
- Role assumption start is absent.

