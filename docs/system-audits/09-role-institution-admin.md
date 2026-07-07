# Role Audit - Institution Admin

## Overview

Purpose: manage institution users, departments, calendar, reports, and scoped audit visibility.

Frontend route file: `frontend/src/routes/AdminRoutes.tsx`.

Sidebar entries: Dashboard, Departments, Users, Calendar, Reports.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/admin/dashboard` | `Dashboard.tsx` | Uses summary data |
| Departments | `/admin/departments` | `Departments.tsx` | Connected to departments APIs |
| Users | `/admin/users` | `Users.tsx` | Connected to users APIs |
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
- `audit_logs`
- `compliance_calendar`
- `audit_reports`
- Institution-scoped operational tables for dashboard/report summaries.

MongoDB:

- No direct Institution Admin route usage found.

## Notable Implementation Details

- User create/invite use hardcoded setup password `SetupTemp123!` in `backend/app/routers/users.py`.
- User management writes audit logs directly with SQL.
- Department reviewer linking is handled by updating `departments.reviewer_user_id`.

## Missing Features and Improvements

- User invitation email delivery is not implemented in `invite_user`; it creates a user with a hardcoded temporary password.
- Role assumption start flow is not implemented even though exit flow exists.
- Admin reset password endpoint returns a simulated message and does not issue a reset token.

