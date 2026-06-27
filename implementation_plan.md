# ComplySense — IT Security Officer UI Implementation Plan

This plan covers the IT Security Officer experience described in docs/itsecurity_ui.md. It is deliberately scoped to the existing backend schema and current frontend structure so the work stays consistent with the repository instead of inventing new data flows.

## Guiding principles
- Use the existing FastAPI router pattern and SQLAlchemy raw SQL queries already used in the project.
- Reuse the existing incident, evidence, control assignment, and audit tables from schema.sql rather than introducing speculative new tables.
- Keep the implementation incremental and testable: first backend endpoints, then frontend pages, then UI polish.
- Do not assume missing services such as AI endpoints or signed URLs; implement simple working fallbacks and clearly surface any unavailable integrations.
- Ask questions when the spec requires behavior that cannot be derived from the existing codebase.

## Scope
The implementation will cover:
1. Security dashboard
2. Incident register and incident detail workflow
3. New incident intake form
4. IT control assignment view
5. Security evidence upload workflow

## Phase 1 — Backend API readiness

### 1.1 Extend incident router
File: backend/app/routers/incidents.py

Add endpoints for:
- GET /api/v1/incidents
  - List incidents scoped to the current institution
  - Support filters: status, severity, incident_type, cert_in, search text
- POST /api/v1/incidents
  - Create a new incident
  - Compute cert_in_deadline as detected_at + 6 hours
  - Set created_by/reported_by/assigned_to from the authenticated user context
- GET /api/v1/incidents/{incident_id}
  - Return incident details plus related timeline entries
- PATCH /api/v1/incidents/{incident_id}
  - Update editable incident fields such as description, affected_systems, affected_data_categories, status, dpdp_notification_required, dpdp_notified_at, resolution_notes, resolved_at, cert_in_reported, cert_in_reported_at
- POST /api/v1/incidents/{incident_id}/timeline
  - Append a manual timeline entry
- PATCH /api/v1/incidents/{incident_id}/checklist
  - Record checklist step completion in timeline (using the existing incident_timeline table)
- GET /api/v1/incidents/dashboard-stats
  - Return count-based dashboard stats for the security dashboard

### 1.2 Add a security dashboard stats endpoint
File: backend/app/routers/incidents.py or backend/app/routers/security.py if created

Return summary data for:
- total controls assigned to the current institution/role context
- compliant vs failing controls
- open incidents count
- cert-in pending count
- critical incidents count
- last incident closed date
- recent incident history for the last 90 days

### 1.3 Make evidence upload reusable for security users
File: backend/app/routers/evidence.py

Ensure the existing evidence upload endpoint can be used by the IT Security Officer role without assumptions. The router already accepts file/form fields; we will keep the same contract and validate that the authenticated role is allowed to upload.

### 1.4 Add or reuse incident-related data shaping
File: backend/app/routers/incidents.py

Return human-readable values where useful for the UI:
- severity labels and colors
- readable incident types
- relative timestamps can be computed in the frontend

## Phase 2 — Frontend route and page implementation

### 2.1 Security dashboard page
File: frontend/src/pages/security/Dashboard.tsx

Implement the page using the existing PageShell layout and the shared UI patterns already used elsewhere.

Include:
- Conditional critical incident banner
- Five KPI cards
- Assigned controls summary and top critical controls list
- Active incidents list
- Incident history chart section

Use the backend endpoint from Phase 1. If the backend is unavailable, show a graceful empty state rather than crashing.

### 2.2 Incident register page
File: frontend/src/pages/security/Incidents.tsx

Implement:
- Summary tabs for incident states
- Filter bar for status, severity, type, CERT-In, and search
- Incidents table with action links
- Empty state when no incidents exist
- Row actions for view and close if allowed by current state

### 2.3 New incident page
File: frontend/src/pages/security/NewIncident.tsx

Implement a working form with:
- Required title, type, severity, description, occurred_at, detected_at
- Optional affected systems, affected data categories, DPDP toggle, assignment
- Countdown helper text for the CERT-In deadline
- Submit action posting to /api/v1/incidents
- Redirect to the created incident detail page on success

### 2.4 Incident detail page
File: frontend/src/pages/security/IncidentDetail.tsx

Implement the core incident command center:
- Header with title, severity status, and action buttons
- Sticky CERT-In timer bar
- Checklist cards and DPDP notification panel
- Incident details editor with inline save behavior
- Timeline list with add-entry support
- AI draft panel state (mocked or placeholder if AI service is not available)

### 2.5 Controls page
File: frontend/src/pages/security/Controls.tsx

Implement a simple but functional table of controls assigned to the IT Security Officer context, using the existing control assignment data.

### 2.6 Evidence page
File: frontend/src/pages/security/Evidence.tsx

Implement a targeted evidence upload experience:
- Select a control from assigned controls
- Upload a file
- Add an optional description
- Post to /api/v1/evidence
- Refresh the uploaded evidence list

## Phase 3 — Data handling and UX details

### 3.1 Status and badge handling
Use consistent UI states for:
- incident severity
- incident status
- evidence approval status
- control assignment status

### 3.2 Timing and countdown behavior
The countdown is a frontend-only timer derived from the incident deadline and current time. It should:
- update every second
- show overdue state after the deadline passes
- switch to a reported state once cert_in_reported is true

### 3.3 Timeline and checklist behavior
- Checklist interactions should be local-first and persist to the backend when possible.
- Timeline entries should refresh after update actions.
- If backend persistence is unavailable, the UI should still reflect the action locally and show a non-blocking warning.

### 3.4 AI draft panel
Because the repository already has AI-related services in the backend, the initial implementation will use a simple fallback path if the AI route is unavailable:
- show a local draft skeleton based on the incident data
- allow the user to regenerate it
- keep the flow functional without blocking the incident workflow

## Phase 4 — Verification steps
The user requested that commands be run by them and that output be pasted back. The implementation will therefore be verified in steps:
1. Backend compile check
2. Frontend build check
3. Manual smoke check of the route behavior

Suggested commands:
- Backend compile:
  - py -m compileall backend\app
- Frontend build:
  - cd frontend
  - npm run build

## Open questions
The following are intentionally left as questions so the implementation does not assume behavior that is not actually present in the codebase:
1. Which user role should be used as the default assignee for new incidents if no assignee is provided?
2. Should the security dashboard use the same control assignment data source as the compliance control pages, or should it be scoped to the IT Security Officer explicitly?
3. Should the AI draft panel call an existing AI endpoint, or should it be implemented as a local draft generator first?

## Implementation order
1. Backend incident endpoints
2. Security dashboard UI
3. Incident list and new incident form
4. Incident detail page
5. Controls and evidence pages
6. Polish and error handling
