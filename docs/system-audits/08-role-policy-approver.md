# Role Audit - Policy Approver

## Overview

Purpose: review submitted policies, approve/reject policy drafts, and view history.

Frontend route file: `frontend/src/routes/PolicyRoutes.tsx`.

Sidebar entries: Inbox, Policy History.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Inbox | `/policy/inbox` | `Inbox.tsx` | Uses policies list/status filtering |
| Review | `/policy/:id/review` | `PolicyReview.tsx` | Uses policy detail/update |
| History | `/policy/history` | `History.tsx` | Uses policies list/history |

## Permissions

Backend permissions:

- `VIEW_POLICIES`
- `APPROVE_POLICIES`
- `DRAFT_POLICIES`

Issue:

- `backend/app/routers/policies.py::update_policy` requires `DRAFT_POLICIES`; this may not match a pure Policy Approver workflow unless seeded role permissions include drafting.

## Database Usage

PostgreSQL:

- Reads/writes `generated_policies`.
- Reads/writes `audit_reports` for report listing/generation in the same router.

MongoDB:

- No direct policy route usage found.

## AI Integration

Implemented:

- Main proxy: `POST /api/v1/ai/policy/analyze/{policy_id}`.
- AI service: `backend/ai_service/routers/policy.py`.
- Agent: `PolicyAgent`.

Partially Implemented:

- AI policy analysis route exists, but core policy approval lifecycle is stored only as status fields and direct updates in `generated_policies`.

## Missing Features and Improvements

- Explicit approve/reject endpoints should use `APPROVE_POLICIES`.
- Policy version history is limited to `version_number`; no separate version history table found.
- No notification workflow for submitted/approved/rejected policies found.

