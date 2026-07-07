# Role Audit - Read-Only Assessor

## Overview

Purpose: view reports and ask AI questions without modifying system state.

Frontend route file: `frontend/src/routes/AssessorRoutes.tsx`.

Sidebar entries: Dashboard, Reports, Ask AI.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/assessor/dashboard` | `Dashboard.tsx` | Uses summary/report data |
| Reports | `/assessor/reports` | `ReportLibrary.tsx` | Uses report APIs |
| Chat | `/assessor/chat` | `Chat.tsx` | Uses assessor AI route |

## Permissions

Backend permissions:

- `USE_ASSESSOR_CHAT`
- `VIEW_AUDIT_REPORTS`
- `VIEW_CONTROLS` appears in AI service route requirements.

## Database Usage

PostgreSQL:

- Reads `audit_reports`.
- Reads assessment/control/gap/report summary tables depending on page.
- AI conversations may read/write `ai_conversations`.

MongoDB:

- No direct assessor route usage found.

## AI Integration

Implemented:

- AI service route: `backend/ai_service/routers/assessor.py`.
- Agent: `AssessorAgent`.
- RAG pipeline in `BaseAgent`.

Partially Implemented:

- Permission used by direct AI route should be reviewed against the intended `USE_ASSESSOR_CHAT` enum.

## Missing Features and Improvements

- Ensure assessor pages are read-only at both frontend and backend.
- Align AI permission requirement with `USE_ASSESSOR_CHAT`.

