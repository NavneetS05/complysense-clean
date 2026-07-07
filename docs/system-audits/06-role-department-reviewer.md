# Role Audit - Department Reviewer

## Overview

Purpose: review assigned tasks, upload evidence, and complete self-assessment work.

Frontend route file: `frontend/src/routes/DeptRoutes.tsx`.

Sidebar entries: Dashboard, My Tasks, Evidence Vault, Self Assessment.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/dept/dashboard` | `Dashboard.tsx` | Uses tasks/evidence summaries |
| My Tasks | `/dept/tasks` | `Tasks.tsx` | Connected to `GET /tasks` |
| Task Wizard | `/dept/tasks/:id` | `TaskWizard.tsx` | Connected to task detail/submit and AI translation/preflight |
| Evidence Vault | `/dept/evidence` | `Evidence.tsx` | Connected to evidence APIs |
| Self Assessment | `/dept/self-assessment` | `SelfAssessment.tsx` | Assessment-related UI exists |

## Permissions

Backend permissions:

- `VIEW_TASKS`
- `UPLOAD_EVIDENCE`
- `VIEW_EVIDENCE`
- likely assessment/control view permissions depending on seeded RBAC.

Special behavior:

- `backend/app/routers/tasks.py::list_tasks` scopes Department Reviewer tasks by reviewer department or assigned user.

## Database Usage

PostgreSQL:

- Reads `mitigation_tasks`.
- Updates `mitigation_tasks` on submit.
- Updates linked `control_assignments` to `submitted` on task submit.
- Reads `departments` to identify reviewer department.
- Reads/writes `evidence_documents`.

MongoDB:

- No direct Department Reviewer route usage found.

## AI Integration

Implemented:

- Main proxy routes:
  - `GET /api/v1/ai/dept/translate/{control_id}`
  - `POST /api/v1/ai/dept/preflight-check`
- AI service routes in `backend/ai_service/routers/dept.py`.
- Agent: department-oriented route logic uses RAG through AI service.

Partially Implemented:

- Evidence preflight can analyze submitted text/file context, but uploaded file extraction/indexing path is not fully connected in the inspected main evidence route.

## Missing Features and Improvements

- Department reviewer evidence approval workflow is not complete.
- Task submit does not validate supporting evidence before marking assignment submitted.
- File upload lacks size/type/security validation.

