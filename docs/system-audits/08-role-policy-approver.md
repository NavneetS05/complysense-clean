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

Implemented:

- Explicit approve/reject endpoints require `APPROVE_POLICIES`.
- Generic policy update rejects direct approved/rejected status changes and directs callers to the approve/reject endpoints.
- Redrafts can carry `parent_policy_id`; backend increments `version_number` from the parent policy.

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

Implemented:

- AI policy analysis route exists, and approval/rejection are handled through dedicated status-transition endpoints.

## Missing Features and Improvements

- Policy version history uses `version_number` plus `parent_policy_id`; no separate version history table exists.
- No notification workflow for submitted/approved/rejected policies found.
