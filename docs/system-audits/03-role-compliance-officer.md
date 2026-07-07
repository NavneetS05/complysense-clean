# Role Audit - Compliance Officer

## Overview

Purpose: manage controls, gaps, assessments, evidence review, policies, tasks, notifications, and compliance AI workflows.

Frontend route file: `frontend/src/routes/ComplianceRoutes.tsx`.

Sidebar entries: Dashboard, Controls, Gaps, Evidence Queue, Assessments, Policies, Tasks, Notifications.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/compliance/dashboard` | `pages/compliance/Dashboard.tsx` | Partially connected; includes AI triage/regulatory change paths |
| Controls | `/compliance/controls` | `Controls.tsx` | Connected to `GET/POST /controls` |
| Control Detail | `/compliance/controls/:id` | `ControlDetail.tsx` | Connected to `GET/PATCH /controls/{assignment_id}` |
| Gaps | `/compliance/gaps` | `Gaps.tsx` | Connected to `GET /gaps` and detail route |
| Evidence Queue | `/compliance/evidence-queue` | `EvidenceQueue.tsx` | Connected to evidence list/detail APIs |
| Assessments | `/compliance/assessments` | `Assessments.tsx` | Connected to assessment APIs |
| Assessment Runner | `/compliance/assessments/:id` | `AssessmentRunner.tsx` | Connected to save/submit APIs |
| Policies | `/compliance/policies` | `Policies.tsx` | Connected to policies APIs |
| Tasks | `/compliance/tasks` | `Tasks.tsx` | Connected to mitigation task APIs |
| Notifications | `/compliance/notifications` | `Notifications.tsx` | Backend notifications router is empty |

## Permissions and Guards

Backend permissions involved:

- `VIEW_CONTROLS`
- `MANAGE_CONTROLS`
- `VIEW_ASSESSMENTS`
- `MANAGE_ASSESSMENTS`
- `VIEW_GAPS`
- `VIEW_EVIDENCE`
- `REVIEW_EVIDENCE`
- `VIEW_POLICIES`
- `DRAFT_POLICIES`
- `VIEW_TASKS`
- `MANAGE_TASKS`
- `VIEW_NOTIFICATIONS`

Frontend guard:

- `RoleRoute allowedRoles={["Compliance Officer"]}`.

## Database Usage

PostgreSQL:

- Reads/writes `control_assignments`.
- Reads/writes `assessments`.
- Reads/writes `assessment_responses`.
- Writes `compliance_results` on assessment submit.
- Writes `compliance_gaps` on assessment submit.
- Reads/writes `mitigation_tasks`.
- Reads/writes `generated_policies`.
- Reads `evidence_documents`.
- Reads/writes `audit_reports` for report APIs under policies.

MongoDB:

- No direct Compliance Officer page usage found in inspected routes.

## AI Integration

Implemented:

- Main API proxy routes:
  - `POST /api/v1/ai/compliance/triage`
  - `POST /api/v1/ai/compliance/regulatory-change`
- Direct AI service routes:
  - `POST /compliance/triage`
  - `POST /compliance/regulatory-change`
  - `POST /compliance/chat`
- Agent: `backend/ai_service/agents/compliance_agent.py`.
- RAG pipeline through `BaseAgent`.

Partially Implemented:

- Main API proxy allows `VIEW_CONTROLS`; AI service triage/regulatory-change require `MANAGE_INSTITUTIONS`, which can block the Compliance Officer role.
- Conversation history is supported through `ConversationManager` when `conversation_id` is supplied.

## Missing Features and Improvements

- Notifications backend is not implemented.
- AI permissions should be aligned between proxy and service.
- Assessment gap generation is simplistic: yes/no response mapping only; no framework-specific scoring rules found.
- Evidence queue needs stronger review/update endpoints if approvals are expected.

