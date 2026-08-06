# Current Project Status

These percentages are engineering estimates from inspected implementation depth, test script validations, and runtime verification.

| Area | Estimated status |
|---|---:|
| Overall | 95% |
| Frontend | 96% |
| Backend API | 96% |
| Authentication | 98% |
| RBAC | 96% |
| MAC Address Audit Tracking | 100% |
| Post-Login CRUD Audit Logging | 98% |
| Tenant & User Management | 98% |
| Notifications System | 95% |
| AI service | 85% |
| PostgreSQL | 95% |
| MongoDB | 60% |
| RAG | 85% |
| Knowledge base management | 80% |

## Major Completed Modules

- **Authentication & Security Interceptor**:
  - Main FastAPI app auth router (`POST /login`, `/register`, `/refresh`, `/logout`, `/change-password`, `/reset-password`).
  - Axios 401 response interceptor auth endpoint exclusion guard (`/login`, `/register`, `/refresh`) preventing unauthorized session rotation loops.
  - User self password change in `/profile` across all 9 RBAC roles.
  - Admin & Institution Admin password reset with account unlock & login counter reset.

- **MAC Address Audit Trail & Post-Login Logging**:
  - `mac_address` column added to `audit_logs` table schema.
  - Client-side browser hardware device fingerprinting (`getClientMacAddress()`).
  - 5-tier backend MAC resolution pipeline (`_get_mac()` with fast host adapter caching, payload MAC, proxy/VPN headers, and ARP table lookup).
  - MAC Address column displayed in Super Admin Audit Trail (`/super-admin/audit-trail`) and Tenant Detail Audit Logs.
  - Comprehensive post-login user activity logging across all CRUD operations (`institution_created`, `institution_updated`, `institution_status_toggled`, `institution_deleted`, `user_invited`, `user_role_updated`, `user_unlocked`, `admin_password_reset`, `change_password`, `department_created`, `department_updated`, `department_deleted`, `reviewer_assigned`, `event_created`, `event_updated`, `event_deleted`).

- **Tenant & User Management**:
  - Permanent tenant cascade deletion API (`DELETE /api/v1/institutions/{id}`) and frontend modal.
  - Institution User Creation / Invite modal and action buttons in Institution Admin (`/admin/users`) and Super Admin Tenant Detail (`/super-admin/tenants/:id`).
  - Dynamic compliance score calculation per framework live (fixed 78% static score bug).

- **Notifications System**:
  - `notifications` table schema, repository, and router endpoints (`/api/v1/notifications`).
  - Read/unread status toggles, user notification feeds, and topbar badges.

- **AI Service & Auditor Tools**:
  - AI Service integration with RAG orchestration.
  - Auditor AI Smart Sampling tool fixed & wired to AI endpoint.
  - Role-specific system prompts providing clear guidance on active role, assigned tasks, and responsibilities.

- **Core GRC Infrastructure**:
  - React route tree and 9 role-based dashboards.
  - PostgreSQL schema for controls, tasks, incidents, vendors, policies, assessments, gaps, and audit reports.

## High-Priority Remaining Work

1. Complete automated integration test suite coverage in CI pipeline.
2. Complete full PDF document export pipeline for audit reports.
3. Enhance role assumption lifecycle active session integrity checks.

## Technical Debt & Architecture Remediations

- Direct AI service proxy calls routed cleanly through main API gateway.
- Repositories used across all CRUD endpoints for SQL encapsulation.
- Document paths and OpenAI legacy references updated to Google Gemini (`langchain-google-genai`).

