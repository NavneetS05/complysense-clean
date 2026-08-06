# Role Audit - Institution Admin

## Overview

Purpose: manage institution users, departments, calendar, reports, and scoped audit visibility.

Frontend route file: `frontend/src/routes/AdminRoutes.tsx`.

Sidebar entries: Dashboard, Departments, Users, Calendar, Reports.

Current status: Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/admin/dashboard` | `Dashboard.tsx` | Connected to `/institutions/dashboard` with dynamic framework compliance scores |
| Departments | `/admin/departments` | `Departments.tsx` | Connected to departments APIs (create, edit, reviewer assignment, delete) |
| Users | `/admin/users` | `Users.tsx` | Connected to users APIs with User Invite Modal & Password Reset Modal |
| Calendar | `/admin/calendar` | `Calendar.tsx` | Connected to calendar APIs |
| Reports | `/admin/reports` | `Reports.tsx` | Uses reports APIs |

## Permissions

Backend permissions:

- `MANAGE_USERS`
- `MANAGE_DEPARTMENTS`
- `VIEW_CALENDAR`
- `MANAGE_CALENDAR`
- `VIEW_AUDIT_TRAIL`
- `VIEW_GAPS`

## Database Usage

PostgreSQL:

- `users`
- `departments`
- `roles`
- `audit_logs` (with `mac_address` tracking and post-login CRUD logging)
- `compliance_calendar`
- `audit_reports`
- Institution-scoped operational tables for dashboard/report summaries.

MongoDB:

- No direct Institution Admin route usage found.

## Implemented Enhancements & Features

- **User Password Reset**: Institution Admin can reset user passwords via `POST /api/v1/users/{user_id}/reset-password`, resetting password hash, clearing failed login counters, unlocking accounts, and writing audit logs.
- **User Invite & Creation**: Modal UI in `/admin/users` allows direct invitation/creation of users with specific roles.
- **Department Reviewer Assignment**: Department reviewer linking updates `departments.reviewer_user_id` and logs audit events (`reviewer_assigned`).
- **Live Device MAC & Activity Audit Logging**: Institution Admin audit trail tracks client device MAC address and all post-login user CRUD operations.

