# Role Audit - Read-Only Assessor

## Overview

Purpose: view reports and ask AI questions without modifying system state.

Frontend route file: `frontend/src/routes/AssessorRoutes.tsx`.

Sidebar entries: Dashboard, Reports, Ask AI.

Current status: Implemented as a read-only workspace.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/assessor/dashboard` | `Dashboard.tsx` | Uses `GET /assessor/dashboard-stats` and `GET /assessor/top-risks` |
| Reports | `/assessor/reports` | `ReportLibrary.tsx` | Uses existing audit report list/detail/download APIs |
| Chat | `/assessor/chat` | `Chat.tsx` | Uses main API proxy `POST /ai/assessor/chat` and read-only conversation history APIs |

## Permissions

Backend permissions:

- `USE_ASSESSOR_CHAT`
- `VIEW_AUDIT_REPORTS`
- Assessor AI service routes now require `USE_ASSESSOR_CHAT`.

## Database Usage

PostgreSQL:

- Reads `audit_reports`.
- Reads aggregate-only `compliance_results`, `compliance_gaps`, `incidents`, and `control_assignments`.
- Chat persistence writes `ai_conversations` with `agent_type='assessor_qa'`; assessor history endpoints are read-only.

MongoDB:

- No direct assessor route usage found.

## AI Integration

Implemented:

- AI service route: `backend/ai_service/routers/assessor.py`.
- Main API proxy: `backend/app/routers/ai/assessor.py`.
- Agent: `AssessorAgent`.
- RAG pipeline in `BaseAgent`.

Implemented:

- Direct assessor AI and main API proxy permissions align on `USE_ASSESSOR_CHAT`.
- The admin risk heatmap was not reused because it requires `MANAGE_INSTITUTIONS` and returns an admin predictive shape, not the assessor top-risk list shape.

## Missing Features and Improvements

- The requested persistent delete button for chat history conflicts with the no-mutate hard constraint; no delete endpoint was added.
