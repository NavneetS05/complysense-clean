# Role Audit - IT Security Officer

## Overview

Purpose: manage security incidents, CERT-In timelines, related controls, and evidence.

Frontend route file: `frontend/src/routes/SecurityRoutes.tsx`.

Sidebar entries: Dashboard, Incidents, Controls, Evidence.

Current status: Implemented for incident CRUD; Partially Implemented for AI and evidence hardening.

## Pages

| Page | Route | Component | Backend/API status |
|---|---|---|---|
| Dashboard | `/security/dashboard` | `pages/security/Dashboard.tsx` | Uses incident stats |
| Incidents | `/security/incidents` | `Incidents.tsx` | Connected to `GET /incidents` |
| New Incident | `/security/incidents/new` | `NewIncident.tsx` | Connected to `POST /incidents` |
| Incident Detail | `/security/incidents/:id` | `IncidentDetail.tsx` | Connected to `GET/PATCH /incidents/{incident_id}` |
| Controls | `/security/controls` | `Controls.tsx` | Uses controls APIs |
| Evidence | `/security/evidence` | `Evidence.tsx` | Uses evidence APIs |

## Permissions

Backend permissions:

- `VIEW_INCIDENTS`
- `MANAGE_INCIDENTS`
- `VIEW_CONTROLS`
- `UPLOAD_EVIDENCE`
- `VIEW_EVIDENCE`

Frontend guard:

- `RoleRoute allowedRoles={["IT Security Officer"]}`.

## Database Usage

PostgreSQL:

- `incidents`: read, insert, update.
- `incident_timeline`: read in detail view.
- `control_assignments`: read for controls.
- `evidence_documents`: read/insert for evidence.

MongoDB:

- No direct route usage found for incident pages.

## AI Integration

Implemented:

- Main API proxy: `POST /api/v1/ai/security/cert-in-draft/{incident_id}`.
- AI service: `backend/ai_service/routers/security.py`.
- Agent: `SecurityAgent`.
- RAG pipeline via `BaseAgent`.

Partially Implemented:

- Security AI service has permission inconsistencies in inspected route definitions.
- CERT-In drafting exists as AI feature, but actual official filing workflow is not implemented.

## Missing Features and Improvements

- `get_dashboard_stats` returns a generated timeline array rather than querying real incident history buckets.
- Incident timeline insertion is not visible in create/update incident flow.
- Evidence upload lacks file size, type, malware, and content validation.

