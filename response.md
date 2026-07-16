**Frontend Role Coverage Audit — Summary (2026-07-16)**

- **Scope:** quick pass comparing implemented frontend routes/pages to UI specs in `docs/`.
- **Method:** inspected role routes and primary pages, searched for AI panel and kanban patterns.

**Findings (per role)**

- **Super Admin:** Fully present — pages and routes exist. Key files: [frontend/src/routes/SuperAdminRoutes.tsx](frontend/src/routes/SuperAdminRoutes.tsx), [frontend/src/pages/super-admin/Dashboard.tsx](frontend/src/pages/super-admin/Dashboard.tsx). Some advanced widgets (AI anomaly banner, platform activity chart) are scaffolded or rely on backend data.

...

- **Institution Admin:** Pages present (`Dashboard`, `Users`, `Departments`, `Reports`, `Calendar`) and routed via `AdminRoutes`. Mostly implemented; reporting widgets may depend on backend endpoints.

...

- **Compliance Officer:** Core pages present: [frontend/src/pages/compliance/Dashboard.tsx](frontend/src/pages/compliance/Dashboard.tsx), [frontend/src/pages/compliance/Controls.tsx](frontend/src/pages/compliance/Controls.tsx), [frontend/src/pages/compliance/EvidenceQueue.tsx](frontend/src/pages/compliance/EvidenceQueue.tsx), [frontend/src/components/shared/AIPanel.tsx](frontend/src/components/shared/AIPanel.tsx). AI surface exists (AIPanel used in regulatory drawer and incident flows). The Kanban board is rendered (columns/cards) but drag-and-drop is not implemented — partial feature (see `Controls.tsx`).

...

- **IT Security Officer:** Pages exist (`/security/*`) and AIPanel is used in incident detail. CERT-In reporting UI elements and triggers are present in places, but full draft/export workflow appears partial and may require backend support.

...

- **Auditor:** Workspace, observations, report builder and report view pages are present and include AI integrations (AIPanel imported in `Workspace.tsx`). Functionality appears largely implemented for basic reporting flows.

...

- **Department Reviewer:** Dashboard, Tasks, Evidence and Self-Assessment pages exist. Basic review flows implemented; finer UX (bulk actions, department-level settings) may be incomplete.

...

- **Vendor Reviewer:** Vendor register, expiry tracker, and vendor detail pages exist. Core CRUD flows present (partial completeness depends on backend endpoints).

...

- **Policy Approver:** Inbox and policy review pages exist (`policy/Inbox.tsx`, `policy/PolicyReview.tsx`). Policy AI/editor integrations are scaffolded in the UI but require backend generation endpoints.

...

- **Read-Only Assessor:** Full-page RAG chat implemented at [frontend/src/pages/assessor/Chat.tsx](frontend/src/pages/assessor/Chat.tsx) and calls `/api/v1/ai/assessor/chat`. This matches the spec for a persistent, multi-turn read-only assessor UI.

...

**Common Gaps / Recommendations**

- **Kanban drag & drop (Compliance Controls):** UI shows the Kanban columns but lacks DnD and optimistic update logic. Implement `@dnd-kit/core` or similar and add PATCH `/api/v1/controls/:id/status` wiring in the card drop handler.

...

- **Sidebar badge counts:** `Sidebar.tsx` has placeholders for `pending` counts; implement API endpoints to supply per-role counters and wire them into `useNotificationStore` or a dedicated badges store.

...

- **AI flows depend on backend:** AIPanel components and the assessor chat are present; verify backend AI endpoints and streaming behavior. Prioritize end-to-end tests for `/api/v1/ai/*` routes.

...

- **CERT-In drafting:** UI surfaces exist but export/copy/official formatting and checklist compliance need end-to-end QA. Add a small e2e test or manual checklist to validate output format.

...

- **Missing polish items:** Empty states, confirmation modals, and error states are partially scaffolded. Add acceptance tests for critical flows (assign control, upload evidence, approve/reject evidence).

...

**Next actions (suggested order)**

- Implement Kanban DnD + optimistic status updates (high impact for daily users).
- Wire badge counts and pending-notification APIs for the Sidebar.
- Verify and test AI backend endpoints with frontend AIPanel/Chat components.
- Add smoke tests for critical flows: assign control, evidence upload, CERT-In export, assessor chat.

...

**References**

- Sidebar nav & badges: [frontend/src/components/shared/Sidebar.tsx](frontend/src/components/shared/Sidebar.tsx)
- Kanban (render-only): [frontend/src/pages/compliance/Controls.tsx](frontend/src/pages/compliance/Controls.tsx)
- Shared AI panel: [frontend/src/components/shared/AIPanel.tsx](frontend/src/components/shared/AIPanel.tsx)
- Assessor chat (RAG): [frontend/src/pages/assessor/Chat.tsx](frontend/src/pages/assessor/Chat.tsx)

...

Audit completed quickly; if you want, I can now open PR-ready patches for Kanban DnD and Sidebar badge wiring, or run the app locally and exercise the flows.

---

**Backend Gaps & Documentation Requirements (detailed, per-role)**

Notes: below I list concrete backend pieces that are missing or only partially implemented (based on the frontend usage), the exact API contract/docs that should be added or updated, and which implementations already exist and therefore do NOT need doc changes before testing.

- **Global / Notifications (applies to all roles)**
	- Missing backend implementation: `GET /api/v1/notifications` and `PATCH /api/v1/notifications/read-all` — the router exists at `backend/app/routers/notifications.py` but has no handlers. There also appears to be no `notifications` table or repository in the schema/migrations.
	- Why it's needed: the frontend `Topbar` and `Sidebar` rely on `GET /api/v1/notifications` to populate `notifications` and `unread_count` and to mark read via `PATCH /api/v1/notifications/read-all`.
	- Exact doc requirements to add/update:
		- API spec: `GET /api/v1/notifications` parameters (`limit:int`, `unread:bool`), response shape:
			{
				"notifications": [ { "notification_id": string, "type": string, "message": string, "created_at": ISO8601, "meta": {...}, "entity_link": string|null, "is_read": bool } ],
				"unread_count": number
			}
		- API spec: `PATCH /api/v1/notifications/read-all` request (none) and response `{ "message": "ok" }` or the updated `unread_count`.
		- Database migration: `notifications` table schema (notification_id, institution_id, user_id, type, message, meta JSONB, entity_id, is_read boolean, created_at)
		- Events mapping doc: enumerate backend events that must create notifications (control assignment, evidence submitted/approved/rejected, incident logged, policy pending/assigned, vendor risk flagged, role assumption start/exit, task assigned/overdue). For each event include `type`, `message template`, `recipient rule` (assigned user / role group), and `entity_link` format.
	- Implementation possible now without doc changes: I can add a minimal, mock-backed implementation of the `GET` and `PATCH` endpoints that return/switch an in-memory list (useful for frontend testing), but production-ready implementation requires the DB migration and wiring in event-producing places. Recommend adding the DB migration + a `NotificationRepository` and then emitting notifications from existing places that create audit_logs.

- **Compliance Officer**
	- Missing backend pieces: none critical — most control/evidence endpoints exist (`/controls`, `/evidence`, `/gaps`). The Kanban DnD is a frontend omission only (backend `PATCH /controls/{id}/status` exists).
	- Doc requirements:
		- Add API contract for the compliance AI triage endpoint: `POST /api/v1/ai/compliance/triage` response fields (exact shape for `response`, `citations`, `query_type`, `conversation_id`) so frontend can reliably render severity badges and action buttons.
		- Document the expected fields/examples returned by `/api/v1/ai/compliance/regulatory-change` (how recommendations are returned and any structured flags like `cert_in_trigger`).
	- Implementations available now (no doc change required to test): `GET /api/v1/controls`, `PATCH /api/v1/controls/{id}/status`, `POST /api/v1/ai/compliance/triage` and `/regulatory-change` proxies are implemented in backend — you can run end-to-end tests if the AI service is available or mocked.

- **IT Security Officer**
	- Missing backend pieces: none obvious — `POST /api/v1/ai/security/cert-in-draft/{id}` proxy exists and `incidents` dashboard stats routes exist.
	- Doc requirements:
		- Document the CERT-In draft API response contract (exact required fields and formatting expectations: `incident_details`, `report_text`, optional placeholders) so the front-end can render and present export/print reliably.
	- Implementations available now: AI proxy exists at `backend/app/routers/ai/security.py`.

- **Auditor**
	- Missing backend pieces: none critical — audit report and observation generation endpoints exist (see `backend/app/routers/audit.py`).
	- Doc requirements:
		- AI endpoints used by auditor (`/api/v1/ai/audit/smart-sample`, `/api/v1/ai/audit/draft-observation`) should have documented response shapes (e.g., `draft_text`, `evidence_refs`, `confidence`) to avoid fragile parsing in the frontend.
	- Implementations available now: audit generation endpoints exist; no DB migration required for basic usage.

- **Institution Admin / Super Admin**
	- Missing backend pieces: none critical — `GET /api/v1/institutions/anomaly-alerts` and `/institutions/stats` exist (mock/support present).
	- Doc requirements:
		- Document `GET /api/v1/institutions/anomaly-alerts` contract and the possible `severity` values and `link` formats used by the front-end.
	- Implementations available now: `backend/app/routers/institutions.py` includes `anomaly-alerts` and `stats` endpoints (mocked but usable).

- **Department Reviewer / Vendor Reviewer / Policy Approver**
	- Missing backend pieces: no unique missing endpoints found in quick scan — vendor risk AI proxy exists and vendor CRUD exists.
	- Doc requirements:
		- For vendor AI: document the `POST /api/v1/ai/vendor/analyze-contract` response fields (`assessment_summary`, `recommendations`, `vendor_risk_id`, `dpdp_compliant`) and what frontend should show.
		- For policy approval: document `POST /api/v1/ai/policy/analyze/{policy_id}` response schema so the Policy Review UI knows how to show suggested edits and citations.
	- Implementations available now: vendor AI and policy AI proxies exist; tests may be done with a stubbed AI service.

**Cross-cutting implementation notes (what I can implement now)**

- I can add a minimal, pragmatic implementation to `backend/app/routers/notifications.py` that returns mock notifications and supports `PATCH /read-all` for frontend testing without altering DB schema. This is useful for UI acceptance testing and does NOT require docs updates.
- For production behavior we must add a DB migration to create a `notifications` table and implement a `NotificationRepository` plus instrument key backend write points (control assignment creation, evidence approval/rejection, incident creation, vendor risk creation, task assignment) to emit notifications. This requires documentation (events mapping) and QA.
- I can also draft the required API docs (OpenAPI-style request/response examples) for the AI endpoints and the notification endpoints — these docs will be sufficient for frontend devs to implement robust rendering and for backend to implement matching contracts.

If you want, I can now either:
- (A) Implement a mock `GET /api/v1/notifications` and `PATCH /api/v1/notifications/read-all` for frontend testing (quick PR), or
- (B) Create the DB migration + repository + event emitters (larger change), or
- (C) Generate OpenAPI-style doc snippets for the AI and notification endpoints so you can review and paste them into `docs/`.

Tell me which option you prefer and I will proceed (I can start with (A) + (C) to unblock frontend testing and the docs).
