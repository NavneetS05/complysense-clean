# Frontend Implementation Audit

Frontend root: `frontend/src`.

## Application Entry

Implemented:

- `frontend/src/main.tsx` mounts React and applies persisted dark mode before render.
- `frontend/src/App.tsx` wraps the router in `ToastProvider`.
- `frontend/src/routes/AppRouter.tsx` creates the active route tree, hydrates the user profile, and silently refreshes the in-memory access token through the refresh cookie.
- Stale duplicate router file `frontend/src/routes/index.tsx` was confirmed unused and removed.

## State Management

Implemented:

- `useAuthStore` in `frontend/src/store/authStore.ts`.
- `useNotificationStore` in the same file.
- `useThemeStore` in the same file.

Partially Implemented:

- Notification state exists, but backend notification endpoints are not implemented.
- Access tokens are stored in Zustand memory state only.
- Refresh tokens are stored in backend-managed HttpOnly cookies.
- `localStorage` stores only the user profile and UI theme preference.

## API Clients & Security Interceptor

Implemented:

- Main API client: `frontend/src/lib/api.ts`.
- Auth helpers: `frontend/src/lib/auth.ts`.
- **Axios 401 Interceptor Security Guard**: Excluded `/login`, `/register`, and `/refresh` from 401 token refresh loops in `frontend/src/lib/api.ts`. Prevents bad credentials from triggering automatic token rotation loops.
- **Client-Side MAC Address Fingerprinting**: `getClientMacAddress()` in `frontend/src/lib/auth.ts` collects browser hardware device fingerprint metrics to pass `mac_address` in payload and `X-Client-MAC` HTTP header on login.

## Implemented UI Modals & Enhancements

- **Security & Password Card ([`Profile.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/Profile.tsx))**: User self password change section added across all 9 RBAC roles.
- **User Reset Password & Invite Modals ([`Users.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/institution-admin/Users.tsx) & [`TenantDetail.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/super-admin/TenantDetail.tsx))**: Action buttons and modals to reset user passwords and invite users into institutions.
- **Delete Tenant Modal ([`Tenants.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/super-admin/Tenants.tsx))**: Permanent tenant deletion confirmation modal in Super Admin portal.
- **MAC Address Audit Columns ([`AuditTrail.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/super-admin/AuditTrail.tsx) & [`TenantDetail.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/super-admin/TenantDetail.tsx))**: Dedicated MAC Address column added to Audit Trail and Tenant Detail Audit tabs.
- **Auditor AI Smart Sampling ([`Workspace.tsx`](file:///d:/dump.worktrees/debugging-project-errors/frontend/src/pages/auditor/Workspace.tsx))**: Wired smart sampling action to return stratified sampling data.
- **Notifications System**: Unread notifications feed and topbar badge connected to `/api/v1/notifications`.

## Styling

Implemented:

- Central CSS: `frontend/src/styles.css`.
- Shared components: `PageShell`, `Sidebar`, `Topbar`, `Toast`, `StatusBadge`, `DataTable`, `FileUpload`, `AIPanel`, `CitationChip`.

## Type Status

Verified:

- Typecheck passed cleanly with `npm.cmd run typecheck`.
