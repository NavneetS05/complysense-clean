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

Partially Implemented:

- Main API also implements non-AI smart sample and draft observation directly in `backend/app/routers/audit.py`.
- This creates duplicate behavior: AI proxy exists, but main audit router has lightweight local implementations.

## Missing Features and Improvements

- Generated reports are stored as database records and returned as simple HTML; no robust document/PDF generation pipeline found.
- Audit observations write an audit log with `entity_id=None`, so the created observation ID is not captured in the log.
- CSV export exists for audit logs.

