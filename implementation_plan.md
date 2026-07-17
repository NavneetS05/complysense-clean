# ComplySense — Full Frontend Implementation Plan

This plan replaces the earlier role-specific draft with a repository-wide implementation roadmap for the frontend. It is intentionally strict about using real backend data and real API contracts only. No hardcoded values, mock data, or placeholder UI states are allowed unless they are clearly derived from the current backend responses and are treated as fallback/error states rather than design content.

## Guiding principles
- Use the existing backend routers, SQLAlchemy queries, and response shapes already present in the repository.
- Prefer real API-driven data flow for every page. If a backend endpoint is missing, implement the backend endpoint first rather than inventing frontend-only mock data.
- Keep the UI aligned with the existing design patterns in the repo: PageShell, shared cards, existing form styles, and role-based routing.
- Treat any missing backend capability as an implementation task, not as a reason to hardcode sample content.
- Do not introduce new tables, new mock endpoints, or fabricated demo records. If the current schema cannot support a feature, document the gap and implement the smallest faithful backend extension.

## Scope
This plan covers the remaining frontend work across the main role experiences, including:
1. Role-based dashboards and route flows
2. Assessment and control workflows
3. Evidence and vendor workflows
4. Security, auditor, compliance, department, and vendor UX completion
5. Shared UI consistency and navigation cleanup

## Core implementation approach
The implementation will proceed in three layers:
1. Backend contract completion where the frontend depends on data that is not yet exposed consistently.
2. Page-by-page frontend wiring to those contracts.
3. Shared component and state cleanup so the app behaves consistently across roles.

This order is required because the frontend should never depend on placeholder data to appear complete.

## Phase 1 — Backend contract completion first

### 1.1 Assessment and control data exposure
Files to inspect/update:
- backend/app/routers/assessments.py
- backend/app/routers/controls.py
- backend/app/routers/evidence.py

Goal:
- Ensure the frontend receives consistent arrays or documented object shapes for assessments, controls, evidence, and related status fields.

Required work:
- Standardize response payloads so the frontend can use them without custom parsing hacks.
- Return institution-scoped records only.
- Include the fields needed by the UI: ids, title/name, status, due dates, framework, severity, description, related evidence, and ownership where available.

Justification:
The current frontend already contains several pages that assume a specific payload shape. If the backend response shape is inconsistent, the UI is forced into brittle fallback parsing. Fixing the contract at the source is cleaner and more maintainable.

### 1.2 Incident and security workflow data exposure
Files to inspect/update:
- backend/app/routers/incidents.py
- backend/app/routers/security.py if present

Goal:
- Make the security-related pages fully functional with real incidents, timeline data, and dashboard summaries.

Required work:
- Expose incident list/detail endpoints with institution-scoped filtering.
- Expose incident creation and timeline update endpoints.
- Expose dashboard stats that the security dashboard can consume directly.

Justification:
The security pages are currently more UI-oriented than data-driven. They should be connected to real incident resources rather than local placeholder state.

### 1.3 Vendor and audit workflow exposure
Files to inspect/update:
- backend/app/routers/vendor.py
- backend/app/routers/audit.py
- backend/app/routers/assessor.py

Goal:
- Ensure the vendor, audit, and assessor workflows consume backend data structures directly.

Required work:
- Confirm vendor detail, contract analysis, observation, and assessment endpoints return the fields the frontend expects.
- Add missing or inconsistent fields where necessary.

Justification:
Several frontend pages already contain the UI surface but depend on data contracts that are not fully aligned with the backend. This should be fixed at the API boundary.

## Phase 2 — Shared frontend foundations

### 2.1 Replace page-level ad hoc data handling with shared request helpers
Files to update:
- frontend/src/lib/api.ts
- frontend/src/components/shared/*

Goal:
- Centralize request handling, auth headers, and error handling so pages can focus on UI and data rendering.

Required work:
- Keep using the current axios client and auth store.
- Add shared helpers only where they reduce repeated boilerplate and keep the same security model.
- Avoid introducing custom abstractions that hide backend errors.

Justification:
A shared request layer will make the pages consistent and reduce duplicate error handling logic.

### 2.2 Implement shared loading/error/empty states
Files to update:
- frontend/src/components/shared/*
- relevant role page components

Goal:
- Provide consistent UX for data fetch states without defaulting to fake content.

Required work:
- Loading skeletons or spinner states while requests are in flight.
- Error states that surface the actual backend error meaningfully.
- Empty states that explain there is no data rather than showing fabricated placeholders.

Justification:
These states are important for a real application and prevent the UI from pretending data exists when it does not.

## Phase 3 — Role page completion by priority

### 3.1 Compliance workflow completion
Files:
- frontend/src/pages/compliance/Assessments.tsx
- frontend/src/pages/compliance/AssessmentRunner.tsx
- frontend/src/pages/compliance/Controls.tsx
- frontend/src/pages/compliance/Gaps.tsx
- frontend/src/pages/compliance/EvidenceQueue.tsx

Required work:
- Load actual assessment and control data from backend endpoints.
- Render real question/response state using API-backed responses.
- Connect gap and evidence views to real records instead of relying on static lists or assumptions.
- Ensure action buttons trigger real API calls and update the page after success.

Justification:
These are the core compliance flows and should be fully data-driven.

### 3.2 Auditor workflow completion
Files:
- frontend/src/pages/auditor/Workspace.tsx
- frontend/src/pages/auditor/Observations.tsx
- frontend/src/pages/auditor/ReportBuilder.tsx
- frontend/src/pages/auditor/ReportView.tsx

Required work:
- Replace placeholder parsing with direct use of the backend response payloads.
- Implement real observation creation and report generation flows through the existing endpoints.
- Keep filters and selection state derived from actual backend data.

Justification:
The auditor workspace already has substantial UI but still depends on brittle assumptions about payload structure.

### 3.3 Vendor workflow completion
Files:
- frontend/src/pages/vendor/Dashboard.tsx
- frontend/src/pages/vendor/VendorDetail.tsx
- frontend/src/pages/vendor/ExpiryTracker.tsx

Required work:
- Connect vendor list/detail screens to actual vendor endpoints.
- Keep contract analysis and risk results tied to the backend AI contract endpoint.
- Ensure the latest analysis result is displayed from backend data, not local synthetic state.

Justification:
Vendor review is one of the most important role flows and should not depend on local-only assumptions.

### 3.4 Security workflow completion
Files:
- frontend/src/pages/security/Dashboard.tsx
- frontend/src/pages/security/Incidents.tsx
- frontend/src/pages/security/NewIncident.tsx
- frontend/src/pages/security/IncidentDetail.tsx
- frontend/src/pages/security/Controls.tsx
- frontend/src/pages/security/Evidence.tsx

Required work:
- Connect each page to actual incidents, controls, evidence, and timeline endpoints.
- Implement real submit/update flows using the backend API.
- Ensure countdown, checklist, and timeline updates are derived from live incident data.

Justification:
The security experience is a core operational workflow and should be fully functional, not partially assembled.

### 3.5 Department reviewer workflow completion
Files:
- frontend/src/pages/dept/Dashboard.tsx
- frontend/src/pages/dept/Tasks.tsx
- frontend/src/pages/dept/TaskWizard.tsx
- frontend/src/pages/dept/Evidence.tsx
- frontend/src/pages/dept/SelfAssessment.tsx

Required work:
- Connect each page to department-scoped task, evidence, and self-assessment data from the backend.
- Keep forms and approvals aligned with the actual service contracts.

Justification:
Department workflows are still likely to be structurally incomplete without direct backend coupling.

## Phase 4 — Navigation and role consistency

### 4.1 Sidebar and route consistency
Files:
- frontend/src/components/shared/Sidebar.tsx
- frontend/src/routes/*.tsx

Required work:
- Ensure every implemented role page is reachable and grouped correctly.
- Keep the active role and navigation labels aligned with the actual authenticated user role.

Justification:
Navigation is part of the user experience and should reflect the implemented routes rather than a partial subset.

### 4.2 Shared component reuse
Files:
- frontend/src/components/shared/*

Required work:
- Reuse the shared page shell, cards, form layout, and chat patterns where possible.
- Avoid one-off styling that makes each page inconsistent.

Justification:
Consistency reduces maintenance cost and speeds implementation.

## Phase 5 — Verification and acceptance criteria

### 5.1 Frontend verification
Run:
- cd frontend
- npm run build

Expected result:
- The app builds successfully with no TypeScript errors introduced by the implementation.

### 5.2 Backend verification
Run:
- py -m compileall backend\app

Expected result:
- The backend modules compile successfully after any API contract changes.

### 5.3 Functional acceptance criteria
Each major role page must satisfy the following:
- It loads real data from the backend when available.
- It presents loading, error, and empty states correctly.
- It uses the current auth context and institution scope.
- It does not show fabricated content or hardcoded demo values.
- It supports the core user action for that workflow (create, update, review, analyze, or submit).

## Explicit non-goals
The following are explicitly out of scope for this implementation plan:
- Creating mock datasets for UI development
- Hardcoding sample records into pages
- Building placeholder dashboards that look complete but are disconnected from the backend
- Rewriting the entire architecture for the sake of consistency if the current routes and services are sufficient

## Implementation order
1. Backend contract alignment for assessments, controls, evidence, incidents, and vendor/audit data
2. Shared frontend data/error/empty-state components
3. Compliance workflow pages
4. Auditor workflow pages
5. Vendor workflow pages
6. Security workflow pages
7. Department reviewer workflow pages
8. Navigation cleanup and final verification
