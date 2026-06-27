# ComplySense — Design Review & Architectural Decision Log

This file is the authoritative record of every architectural, security, API, database, and UI decision made during the ComplySense implementation. It is updated after every meaningful change.

---

## Iteration 1 — 2026-06-24

### Source
- `docs/design_systems.md`
- `docs/admins_ui`
- `docs/compliance_ui`
- `backend/app/services/auth_service.py`
- `backend/app/routers/auth.py`
- `backend/app/repositories/users.py`
- `backend/app/schemas/auth.py`
- `schema.sql`

### Observation
Full codebase discovery and cross-referencing of the three provided UI specification documents against the existing FastAPI backend and PostgreSQL schema.

### Decision
Accepted the existing FastAPI + SQLAlchemy async architecture as the backend foundation. No framework changes required.

### Reasoning
The backend already models all 28 required tables, supports JWT with refresh-token rotation, and uses repository-pattern layering. Changing frameworks would introduce risk without benefit.

### Alternatives Considered
- Django REST Framework — rejected due to async limitations and heavier migration cost.

### Impact
- No direct impact on pages or APIs.
- All future code will follow the existing repository → service → router pattern.

### Status
Approved

### Evidence
- `schema.sql` — 28 tables confirmed.
- `backend/app/routers/` — 9 existing router files.

---

## Iteration 2 — 2026-06-24

### Source
- `docs/design_systems.md` (Auth Pages section)
- `backend/app/services/auth_service.py`

### Observation
**Conflict detected:** The login UI specification shows an error banner reading *"Account locked due to 5 failed attempts"*, implying a 5-attempt threshold. The existing backend used `_MAX_ATTEMPTS = 5` and `_BLOCK_MINUTES = 30`. The user explicitly requested 3 attempts and 5-second blocks.

### Decision
- `_MAX_ATTEMPTS` set to **3**.
- `_BLOCK_SECONDS` set to **5** (replaces `_BLOCK_MINUTES`).
- Lock duration formula changed from `timedelta(minutes=_BLOCK_MINUTES)` → `timedelta(seconds=_BLOCK_SECONDS)`.

### Reasoning
User explicitly mandated the 3-attempt / 5-second rule for development convenience. The 5-minute default was changed for testability. The `_BLOCK_MINUTES` variable was removed entirely to avoid stale-variable runtime errors.

### Alternatives Considered
- Keep 5-attempt / 30-minute production default — rejected per user instruction.
- Use configurable env-var — deferred until production hardening phase.

### Impact
- **Security:** Shorter lockout window reduces brute-force protection in production; must be revisited before go-live.
- **Pages:** Login screen countdown timer now counts down from 5 seconds, not 5 minutes.
- **API:** `POST /auth/login` — `blocked_until` field in error response reflects 5-second offset.

### Status
Approved

### Evidence
- `backend/app/services/auth_service.py` lines 38–39: `_MAX_ATTEMPTS = 3`, `_BLOCK_SECONDS = 5`.

---

## Iteration 3 — 2026-06-24

### Source
- `docs/design_systems.md` (Reset Password screen section)
- `backend/app/routers/auth.py`
- `backend/app/services/auth_service.py`
- `backend/app/repositories/users.py`

### Observation
The Reset Password screen requires the frontend to validate whether a reset token is valid **on page mount**, before rendering the form. No such endpoint existed in the backend — only `POST /auth/reset-password` (which **consumes** the token) was present.

### Decision
Added `GET /auth/validate-reset-token?token=:token` endpoint.
- **Non-destructive:** The token is not marked `used`; only a SELECT query runs.
- **Response:** `{ "valid": true, "email": "..." }` or `{ "valid": false }`.
- **Security:** No information leaked — invalid/expired/used tokens all return `valid: false` with no distinction.

### Reasoning
The frontend must conditionally show either the password form or an "invalid link" error state. Consuming the token on load would break the reset flow if the user refreshes the page.

### Alternatives Considered
- Return HTTP 400 instead of `valid: false` — rejected to keep the endpoint friendly for frontend conditional rendering without requiring try-catch.
- Embed token validity in the `POST /reset-password` response — rejected because the UI renders two completely different screens.

### Impact
- **Pages:** `/reset-password/:token` — mounts and calls this endpoint; shows form only when `valid: true`.
- **API:** New `GET /auth/validate-reset-token` endpoint added.
- **Database:** Read-only query on `password_reset_tokens` joined with `users`.
- **Security:** No token consumption; replay-safe.

### Status
Approved

### Evidence
- `backend/app/routers/auth.py` — `validate_reset_token` route handler.
- `backend/app/services/auth_service.py` — `validate_reset_token` method.
- `backend/app/repositories/users.py` — `validate_reset_token` method (added in previous session).

---

## Iteration 4 — 2026-06-24

### Source
- `docs/design_systems.md` (Role Assumption / Topbar section)
- `backend/app/repositories/sessions.py`
- `backend/app/routers/auth.py`
- `backend/app/services/auth_service.py`

### Observation
The design system specifies that privileged users (Super Admin, Institution Admin) can temporarily assume the view of another role. The existing `SessionRepository.update_role()` method already supported updating `active_role_id` on a session. However, no HTTP endpoint existed to **enter** or **exit** a role assumption.

### Decision
Implemented `POST /auth/exit-role-assumption` as the first role-assumption endpoint.

**Exit flow:**
1. Read `user.role_id` (primary) and `user.active_role_id` (currently active).
2. If they differ, call `sessions.update_role()` to reset `active_role_id → role_id`.
3. Reload permissions for the primary role via `RbacRepository`.
4. Write `exit_role_assumption` audit log entry.
5. Return a fresh `ExitRoleAssumptionResponse` containing the restored `UserContext` so the frontend can immediately re-hydrate without a second `/auth/me` call.

**Enter flow (`POST /auth/assume-role`):** Deferred to Phase 2 once the role-assumption UI drawer is specified in docs 4–7.

### Reasoning
- `exit-role-assumption` is the minimum required for the "Exit Assumed Role" banner button in the Topbar design.
- Reusing `SessionRepository.update_role()` avoids duplicating session mutation logic.
- Returning a full `UserContext` in the response eliminates a round-trip to `/auth/me`.

### Alternatives Considered
- Invalidate the session and issue a new JWT — rejected; unnecessarily complex and forces a full re-login UX.
- Store assumed role in JWT claims instead of the session — rejected; sessions are already the source of truth for `active_role_id` per `deps.py`.

### Impact
- **API:** New `POST /auth/exit-role-assumption` endpoint.
- **Schemas:** Added `ExitRoleAssumptionResponse`, `AssumeRoleRequest`, `ValidateResetTokenResponse` to `schemas/auth.py`.
- **Pages:** Topbar `RoleAssumptionBar` component will call this on "Exit" click.
- **Security:** Endpoint is protected by `get_current_user`; audit log is written on every call.
- **Database:** Updates `user_sessions.active_role_id`; reads `roles.role_name` for the restored context.

### Status
Approved

### Evidence
- `backend/app/routers/auth.py` — `exit_role_assumption` route handler.
- `backend/app/services/auth_service.py` — `exit_role_assumption` method.
- `backend/app/repositories/sessions.py` line 87 — `update_role` method (pre-existing).

---

## Iteration 5 — 2026-06-24

### Source
- `frontend/src/routes/AdminRoutes.tsx`
- `frontend/src/routes/SuperAdminRoutes.tsx`
- `frontend/src/routes/ComplianceRoutes.tsx`
- `frontend/src/routes/SecurityRoutes.tsx`
- `frontend/src/routes/AuditorRoutes.tsx`
- `frontend/src/routes/DeptRoutes.tsx`
- `frontend/src/routes/VendorRoutes.tsx`
- `frontend/src/routes/PolicyRoutes.tsx`
- `frontend/src/routes/AssessorRoutes.tsx`
- `frontend/src/layouts/DashboardLayout.tsx`
- `frontend/src/components/shared/Sidebar.tsx`

### Observation
The previous layout pattern defined a constant navigation array (`nav`) and page `title` directly in every single route config file (e.g. `AdminRoutes.tsx`), passing them as props to `<DashboardLayout title={title} nav={nav} />`. This created tight coupling between navigation layout presentation, user auth state (since the layout must match the user's active role context), and the router configuration. Furthermore, static route files could not easily react to dynamic state changes (such as showing dynamic unread notification/task count badges) and introduced massive code duplication (9 separate layout configurations for 9 roles).

### Decision
Centralized all navigation and role-aware menu presentation rules directly within the `Sidebar` and `Topbar` components, removing the `nav` and `title` props from `DashboardLayout` and stripping the redundant navigation lists from all 9 route configuration files. 

### Reasoning
1. **Single Source of Truth (DRY):** Nav links, icons, and structures are now defined in a single dictionary mapping (`NAV_MAP`) inside `Sidebar.tsx` instead of being duplicated and synchronized across 9 distinct routing files.
2. **Dynamic Badging & Real-Time Count States:** Routing files are static modules and cannot naturally react to reactive state stores (like `useNotificationStore` or future tasks queue stores). Moving navigation definition inside a React component (`Sidebar.tsx`) allows navigation badges (such as unread notification counts, pending evidence count) to update dynamically in real time.
3. **Impersonation/Role Assumption Support:** The "Role Assumption" feature allows admins to swap contexts without logging out. If navigation layout definitions were tied statically to route layouts, the sidebar would display incorrect options when role assumption is active. Centralizing navigation rules inside `Sidebar` lets it read the active session's `active_role_name` dynamically and render the correct sidebar navigation for the assumed role automatically.
4. **Decoupled Architecture:** Route files are now purely responsible for URL path mapping, component loading, and role guards (`RoleRoute`), rather than UI navigation presentation.

### Alternatives Considered
- **Keep router-based nav config and pass state context to layout** — rejected because it required boilerplate to propagate reactive counts and role assumptions up into the static router array.
- **Pass navigation list down as a JSON metadata object in routes** — rejected because React Icons (Lucide icons) cannot easily be serialized, and static configs still wouldn't have clean access to reactive context.

### Impact
- **Pages:** Layout renders the correct navbar automatically.
- **APIs:** None.
- **Database:** None.
- **Permissions:** None.
- **Security:** Standard role guards (`RoleRoute`) still secure each sub-route layout statically, maintaining authorization integrity.
- **UI:** Sidebar UI automatically synchronizes with active role transitions and updates badges on unread items.

### Status
Approved

### Evidence
- [`Sidebar.tsx`](file:///c:/Users/hp/Desktop/complysense-clean/frontend/src/components/shared/Sidebar.tsx#L30-L84) — Contains the centralized `NAV_MAP` for all 9 roles.
- [`AdminRoutes.tsx`](file:///c:/Users/hp/Desktop/complysense-clean/frontend/src/routes/AdminRoutes.tsx#L12-L18) — Uses prop-free `<DashboardLayout />`.
- [`DashboardLayout.tsx`](file:///c:/Users/hp/Desktop/complysense-clean/frontend/src/layouts/DashboardLayout.tsx) — Cleared of prop-types.

---

## Iteration 6 — 2026-06-26

### Source
- `docs/itsecurity_ui.md`
- `frontend/src/pages/security/`
- `frontend/src/pages/auditor/Workspace.tsx`
- `frontend/src/pages/dept/Evidence.tsx`

### Observation
The implementation work for new UI documents must not rely on fallback or mock data behavior in the frontend when the backend contract is still being developed. A few earlier UI implementations used local parsing fallbacks (for example, accepting either an array or a wrapped `{ data: ... }` object) and generic placeholder behavior, which makes the UI less explicit and can silently hide contract mismatches.

### Decision
- Frontend pages will only consume the API contract shape that the backend is expected to return.
- If a response shape is not yet finalized, the UI will leave the field unpopulated or show a neutral empty state rather than silently coercing the payload.
- Any pending integration point must be documented as a placeholder contract in the design review document and in the relevant implementation notes, using the expected backend endpoint name and payload shape.
- The implementation will not introduce fallback data generation inside the UI for real workflow pages.

### Reasoning
- Fallback parsing can be mistaken for working integration and makes later backend contract changes harder to track.
- Explicit placeholder contracts make it clear which team owns the endpoint and what response shape is expected.
- This keeps the frontend implementation honest, testable, and aligned with the product spec.

### Impact
- Frontend pages will be more explicit about missing backend integrations.
- The backend and AI service teams can align on the exact endpoint names and payloads without UI-side guessing.
- The docs will now record what is already implemented and what remains as a contract placeholder.

### Status
Approved

### Evidence
- `frontend/src/pages/auditor/Workspace.tsx` — response parsing is now documented as a placeholder contract rather than a silent fallback.
- `frontend/src/pages/security/` — the security workflow pages will follow the same pattern.

### Source
- `frontend/src/pages/super-admin/`
- `frontend/src/pages/institution-admin/`
- `frontend/src/routes/SuperAdminRoutes.tsx`
- `frontend/src/components/shared/Toast.tsx`
- `frontend/src/components/shared/ConfirmModal.tsx`

### Observation
Completed implementation of all Phase 4 (Super Admin Portal) and Phase 5 (Institution Admin Portal) pages. Identified several TypeScript compilation errors during integration:
1. `useToast()` hook returns context handlers (`success`, `error`, `warning`) instead of a generic `showToast(msg, type)` function.
2. `ConfirmModal` component expects explicit `open` control prop, and a `confirmVariant` prop (values: `"default" | "destructive"`) rather than `variant`.
3. The Super Admin routing list defined the path for the institution detail page as `tenants/:id` but the `TenantDetail.tsx` component expected the route param name `institution_id` (via `useParams<{ institution_id: string }>()`).

### Decision
1. Implemented the executive reports page `/admin/reports` with a PDF briefings generator and log table.
2. Adjusted route paths in `SuperAdminRoutes.tsx` to match the exact `:institution_id` parameter expected by `TenantDetail.tsx`.
3. Updated the frontend toast notifications across all Phase 4 & 5 pages to call `toast.success(msg)` and `toast.error(msg)` directly.
4. Rewrote `ConfirmModal` tags to pass `open={!!target}` and `confirmVariant` correctly, satisfying TS rules.

### Reasoning
- Aligning prop names directly with component contracts guarantees correct type checking and prevents UI crashes during user confirmation.
- Aligning URL router parameter keys to component parameters ensures that institution data displays correctly when navigating.

### Alternatives Considered
- Modify the `useToast` hook or `ConfirmModal` props directly — rejected because those are shared core components created in earlier iterations. Modifying page calls is less intrusive and cleaner.

### Impact
- **Pages:** Super Admin and Institution Admin pages load correctly.
- **Routing:** Deep linking to `/super-admin/tenants/:institution_id` parses the ID properly.
- **TypeScript:** The project compiles cleanly.

### Status
Approved

### Evidence
- `frontend/src/pages/super-admin/TenantDetail.tsx` — uses `institution_id` successfully.
- `frontend/src/pages/institution-admin/Reports.tsx` — generates mock executive PDF briefing logs.
- `npm run typecheck` — successfully compiles with zero errors.

