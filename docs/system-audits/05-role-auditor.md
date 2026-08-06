# Role Audit - Auditor

## Overview

Purpose: inspect assessments/evidence, create audit observations, generate reports, and use audit sampling.

Frontend route file: `frontend/src/routes/AuditorRoutes.tsx`.

Sidebar entries: Workspace, Observations, Reports.

Current status: Implemented.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Workspace | `/auditor/workspace` | `Workspace.tsx` | Connected to audit/evidence/assessment data with AI Smart Sampling & Observation Modals |
| Observations | `/auditor/observations` | `Observations.tsx` | Connected to observation APIs (list, draft, update, delete) |
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

- Reads `audit_logs` for audit trail endpoints (with `mac_address` column).
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
  - `POST /api/v1/ai/audit/smart-sample` (Smart sampling with sample size calculation, stratification, and sample item generation)
  - `POST /api/v1/ai/audit/draft-observation` (Draft formal audit observations via AI)
- Direct AI service routes in `backend/ai_service/routers/audit.py`.
- Agent: `AuditAgent` with explicit user role context, assigned task, and responsibility guidance.

## Implemented Enhancements & Features

- **AI Smart Sampling Tool**: Fixed smart sampling button notification issue in Auditor Workspace (`/auditor/workspace`), returning stratified sampling data.
- **Audit Observation Management**: Adding, editing, and deleting audit observations writes detailed audit log records.
- **Audit Trail & MAC Address Visibility**: Auditor views include device MAC address and full activity details.
