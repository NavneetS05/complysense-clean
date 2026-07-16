# Role Audit - Auditor

## Overview

Purpose: inspect assessments/evidence, create audit observations, generate reports, and use audit sampling.

Frontend route file: `frontend/src/routes/AuditorRoutes.tsx`.

Sidebar entries: Workspace, Observations, Reports.

Current status: Partially Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Workspace | `/auditor/workspace` | `Workspace.tsx` | Uses audit/evidence/assessment data |
| Observations | `/auditor/observations` | `Observations.tsx` | Connected to observation APIs |
| Reports | `/auditor/reports` | `ReportBuilder.tsx` | Connected to report list/generate APIs |
| Report View | `/auditor/reports/:id` | `ReportView.tsx` | Connected to report detail/download APIs |

## Permissions

Backend permissions:

- `VIEW_AUDIT_REPORTS`
- `ADD_AUDIT_OBSERVATIONS`
- `GENERATE_AUDIT_REPORTS`
- `VIEW_ASSESSMENTS`
- `VIEW_EVIDENCE`

Additional backend role checks:

- Some endpoints explicitly require `active_role_name == RoleName.AUDITOR`.

## Database Usage

PostgreSQL:

- Reads `audit_logs` for audit trail endpoints.
- Reads/writes/deletes `audit_observations`.
- Reads `assessments`.
- Reads `evidence_documents`.
- Reads `compliance_gaps`.
- Reads/writes `audit_reports`.

MongoDB:

- No direct auditor route usage found.

## AI Integration

Implemented:

- Main proxy routes:
  - `POST /api/v1/ai/audit/smart-sample`
  - `POST /api/v1/ai/audit/draft-observation`
- Direct AI service routes in `backend/ai_service/routers/audit.py`.
- Agent: `AuditAgent`.

Implemented:

- `/api/v1/ai/audit/smart-sample` is canonical for smart sampling.
- `/api/v1/ai/audit/draft-observation` is canonical for observation drafting.
- Legacy local audit endpoints redirect to the canonical AI proxy routes with HTTP 307.

## Missing Features and Improvements

- Generated reports are stored as database records and returned as simple HTML; no robust document/PDF generation pipeline found.
- Audit observations now write audit logs with the created observation ID; update/delete observation actions are also audited.
- CSV export exists for audit logs.
