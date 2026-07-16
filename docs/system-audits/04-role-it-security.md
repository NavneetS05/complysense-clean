# Role Audit - IT Security Officer

## Overview

Purpose: manage security incidents, CERT-In timelines, related controls, and evidence.

Frontend route file: `frontend/src/routes/SecurityRoutes.tsx`.

Sidebar entries: Dashboard, Incidents, Controls, Evidence.

Current status: Implemented for incident CRUD/timeline, dashboard stats, AI permission alignment, and evidence upload hardening.

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
- `REVIEW_EVIDENCE` for evidence approval/rejection where granted by role seeding.

Frontend guard:

- `RoleRoute allowedRoles={["IT Security Officer"]}`.

## Database Usage

PostgreSQL:

- `incidents`: read, insert, update.
- `incident_timeline`: written on incident create/update and read in detail view.
- `control_assignments`: read for controls.
- `evidence_documents`: read/insert for evidence and status transition review.

MongoDB:

- No direct route usage found for incident pages.

## AI Integration

Implemented:

- Main API proxy: `POST /api/v1/ai/security/cert-in-draft/{incident_id}`.
- AI service: `backend/ai_service/routers/security.py`.
- Agent: `SecurityAgent`.
- RAG pipeline via `BaseAgent`.

Remaining gap:

- CERT-In drafting exists as AI feature, but actual official filing workflow is not implemented.

## Missing Features and Improvements

- Official CERT-In filing workflow is not implemented.
- Notifications/reminders are not implemented because notifications backend is out of scope.
