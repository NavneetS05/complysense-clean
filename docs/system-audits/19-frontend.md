# Frontend Implementation Audit

Frontend root: `frontend/src`.

## Application Entry

Implemented:

- `frontend/src/main.tsx` mounts React and applies persisted dark mode before render.
- `frontend/src/App.tsx` wraps the router in `ToastProvider`.
- `frontend/src/routes/AppRouter.tsx` creates the active route tree and hydrates auth state from `localStorage`.

Partially Implemented:

- `frontend/src/routes/index.tsx` defines another router that appears stale or unused because `App.tsx` imports `AppRouter`.

## State Management

Implemented:

- `useAuthStore` in `frontend/src/store/authStore.ts`.
- `useNotificationStore` in the same file.
- `useThemeStore` in the same file.

Partially Implemented:

- Notification state exists, but backend notification endpoints are not implemented.
- Auth tokens are stored in Zustand and `localStorage`.

## API Clients

Implemented:

- Main API client: `frontend/src/lib/api.ts`.
- Auth helpers: `frontend/src/lib/auth.ts`.

Partially Implemented:

- `frontend/src/lib/aiApi.ts` exports a direct AI service client but no usages were found by `rg "aiApi" frontend/src -n`.
- Main API proxy routes should be preferred for AI calls because they can enforce auth and tenancy.

## Routing and RBAC

Implemented:

- `ProtectedRoute` blocks unauthenticated routes.
- `RoleRoute` checks allowed role names.
- Role routes are split by workspace:
  - `AdminRoutes.tsx`
  - `ComplianceRoutes.tsx`
  - `SecurityRoutes.tsx`
  - `SuperAdminRoutes.tsx`
  - `AssessorRoutes.tsx`
  - `AuditorRoutes.tsx`
  - `DeptRoutes.tsx`
  - `VendorRoutes.tsx`
  - `PolicyRoutes.tsx`

Partially Implemented:

- Guards are role-name based, while backend authorization is permission-key based. This is acceptable but requires seeded permissions to remain aligned with frontend role assumptions.

## Navigation

Implemented:

- `frontend/src/components/shared/Sidebar.tsx` defines `NAV_MAP` for all roles.
- Sidebar uses active role, supporting assumed-role navigation display.

Partially Implemented:

- `pending` badges are noted as TODO-like behavior: unread badge uses notification store, but pending counts are not backed by API in the inspected component.

## Pages by Workspace

Implemented page shells:

- Auth: Login, Forgot Password, Reset Password.
- Super Admin: Dashboard, Tenants, Tenant Detail, Audit Trail, Roles.
- Institution Admin: Dashboard, Departments, Users, Calendar, Reports.
- Compliance: Dashboard, Controls, Control Detail, Gaps, Evidence Queue, Assessments, Assessment Runner, Policies, Tasks, Notifications.
- Security: Dashboard, Incidents, New Incident, Incident Detail, Controls, Evidence.
- Auditor: Workspace, Observations, Report Builder, Report View.
- Department: Dashboard, Tasks, Task Wizard, Evidence, Self Assessment.
- Vendor: Dashboard, New Vendor, Vendor Detail, Expiry Tracker.
- Policy: Inbox, Policy Review, History.
- Assessor: Dashboard, Report Library, Chat.

## Validation

Partially Implemented:

- Forms use a mixture of local React state and API error handling.
- Dependencies include `react-hook-form` and `zod`, but many inspected pages rely on ad hoc state and backend validation.

## Loading and Error Handling

Implemented:

- Auth hydration shows a spinner in `ProtectedRoute`.
- Axios interceptor attempts silent token refresh on 401.

Partially Implemented:

- Error response shape mismatch exists for lockout handling.
- Many pages use generic error handling and `any` in catch blocks.

## Styling

Implemented:

- Central CSS: `frontend/src/styles.css`.
- Shared components: `PageShell`, `Sidebar`, `Topbar`, `Toast`, `StatusBadge`, `DataTable`, `FileUpload`, `AIPanel`, `CitationChip`.

## Lint and Type Status

Verified:

- Typecheck passed with `npm.cmd run typecheck`.
- Lint failed with 76 errors and 10 warnings.

Major lint classes:

- Unused imports.
- `@typescript-eslint/no-explicit-any`.
- Missing React hook dependencies.
- One unnecessary escape warning.

## Missing Frontend Work

- Remove or wire `aiApi.ts`.
- Resolve duplicate router export.
- Replace `localStorage` refresh-token persistence if backend cookie auth is implemented.
- Implement notification data flow or hide nonfunctional notification/pending badges.
- Clean lint errors before production release.

