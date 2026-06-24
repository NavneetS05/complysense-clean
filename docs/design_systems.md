# ComplySense UI Specification
# Document 1 of 7 — Design System, Global Components, Auth Pages

---

## 1. BRAND & COLOR SYSTEM

### Primary Color
```
Primary:       #2563EB  (blue-600) — buttons, active nav, links, focus rings, chart series 1
Primary Hover: #1D4ED8  (blue-700)
Primary Light: #EFF6FF  (blue-50)  — pill backgrounds, selected row tint
Primary Ring:  #BFDBFE  (blue-200) — focus outlines
```

Why this blue: Used by Linear, Vercel, Jira, Notion dashboards. Signals trust, authority, compliance. Readable at all sizes. Works in both light and dark mode without appearing washed out.

### Semantic Colors
```
Success:  #16A34A  (green-600)   — approved, compliant, resolved
Warning:  #D97706  (amber-600)   — in_progress, partial, expiring soon
Critical: #DC2626  (red-600)     — overdue, non_compliant, critical severity
High:     #EA580C  (orange-600)  — high severity
Medium:   #CA8A04  (yellow-600)  — medium severity
Low:      #65A30D  (lime-600)    — low severity
Info:     #0891B2  (cyan-600)    — informational banners, neutral badges
```

### Status → Color Mapping (used everywhere consistently)
```
not_started      → gray-400 bg, gray-700 text
in_progress      → blue-100 bg, blue-700 text
submitted        → purple-100 bg, purple-700 text
compliant        → green-100 bg, green-700 text
non_compliant    → red-100 bg, red-700 text
na               → gray-100 bg, gray-500 text
open             → red-100 bg, red-700 text
investigating    → amber-100 bg, amber-700 text
contained        → blue-100 bg, blue-700 text
resolved         → green-100 bg, green-700 text
closed           → gray-100 bg, gray-500 text
pending          → amber-100 bg, amber-700 text
approved         → green-100 bg, green-700 text
rejected         → red-100 bg, red-700 text
draft            → gray-100 bg, gray-500 text
pending_approval → amber-100 bg, amber-700 text
superseded       → gray-200 bg, gray-500 text
```

### Light Mode (default)
```
--background:        #F8FAFC   (slate-50)  — page background
--surface:           #FFFFFF               — cards, panels, sidebars
--surface-secondary: #F1F5F9   (slate-100) — table rows alt, input backgrounds
--border:            #E2E8F0   (slate-200)
--text-primary:      #0F172A   (slate-900)
--text-secondary:    #64748B   (slate-500)
--text-disabled:     #CBD5E1   (slate-300)
```

### Dark Mode
```
--background:        #0F172A   (slate-950)
--surface:           #1E293B   (slate-800)
--surface-secondary: #334155   (slate-700)
--border:            #475569   (slate-600)
--text-primary:      #F1F5F9   (slate-100)
--text-secondary:    #94A3B8   (slate-400)
--text-disabled:     #475569   (slate-600)
```

Dark mode class toggle on `<html>` element. Preference saved to `localStorage`. Detected on first load from `prefers-color-scheme`.

---

## 2. TYPOGRAPHY

```
Font Family:   Inter (from Google Fonts, variable font)
Mono Font:     JetBrains Mono (for control IDs, UUIDs, code, CERT-In report text)

Scale:
  xs:   12px / 16px line-height — table meta, timestamps, helper text
  sm:   13px / 20px — secondary labels, form hints
  base: 14px / 20px — body, table cells, inputs (UI default)
  md:   15px / 22px — card titles
  lg:   18px / 28px — page section headers
  xl:   20px / 28px — modal titles
  2xl:  24px / 32px — page titles (h1)
  3xl:  30px / 36px — stat numbers on dashboards

Weights: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
```

---

## 3. LAYOUT GRID

```
Sidebar width:    240px (collapsed: 64px icon-only on mobile)
Topbar height:    56px
Content padding:  24px (desktop), 16px (mobile)
Card radius:      8px (rounded-lg)
Input radius:     6px (rounded-md)
Button radius:    6px (rounded-md)
Max content width: none — full width minus sidebar
```

---

## 4. COMPONENT LIBRARY

**shadcn/ui** — Tailwind-based, accessible, zero lock-in.

Install components used:
```
Button, Input, Label, Textarea, Select, Checkbox, Switch,
Dialog, Sheet (for AI drawer), Dropdown Menu, Popover,
Table, Badge, Card, Separator, Avatar, Skeleton, Toast,
Tabs, Progress, ScrollArea, Tooltip, Alert, AlertDialog,
Form (with react-hook-form + zod validation)
```

Additional libraries:
```
@dnd-kit/core          — Kanban drag-and-drop (Controls page)
recharts               — Charts on all dashboards
@tiptap/react          — Rich text editor (Policy editor)
date-fns               — Date formatting everywhere
react-hook-form        — All forms
zod                    — Validation schemas
lucide-react           — All icons (consistent icon set)
```

---

## 5. SIDEBAR COMPONENT

### Behavior
- Always visible on desktop (240px), collapsible on mobile (slides out as Sheet)
- Active item: left border 2px solid primary, primary-light background, primary text
- Hover: slate-100 background (light) / slate-700 (dark)
- Icon: 18px, same color as text, placed left of label
- Badge (count): right-aligned, red-500 background, white text, min-width 18px rounded-full
- Logo at top: shield icon + "ComplySense" in semibold + institution name beneath in secondary text (for non-super-admin)
- Bottom of sidebar: user avatar, full name, role badge, with a kebab menu (Profile, Logout)

### Nav Items Per Role

**Super Admin**
```
Dashboard          /super-admin/dashboard     LayoutDashboard
Tenants            /super-admin/tenants       Building2
Audit Trail        /super-admin/audit-trail   ScrollText
Roles & Permissions /super-admin/roles        ShieldCheck
```

**Institution Admin**
```
Dashboard          /admin/dashboard           LayoutDashboard
Departments        /admin/departments         FolderTree
Users              /admin/users               Users
Calendar           /admin/calendar            CalendarDays
Reports            /admin/reports             FileBarChart
```

**Compliance Officer**
```
Dashboard          /compliance/dashboard      LayoutDashboard
Controls           /compliance/controls       Kanban
Gaps               /compliance/gaps           AlertTriangle
Evidence Queue     /compliance/evidence-queue Inbox        [pending count badge]
Assessments        /compliance/assessments    ClipboardList
Policies           /compliance/policies       FileText
Tasks              /compliance/tasks          CheckSquare
Notifications      /compliance/notifications  Bell         [unread count badge]
```

**IT Security Officer**
```
Dashboard          /security/dashboard        ShieldAlert
Incidents          /security/incidents        Siren        [open count badge]
Controls           /security/controls         Settings2
Evidence           /security/evidence         Upload
```

**Auditor**
```
Workspace          /auditor/workspace         Microscope
Observations       /auditor/observations      MessageSquare
Reports            /auditor/reports           FileText
```

**Department Reviewer**
```
Dashboard          /dept/dashboard            LayoutDashboard
My Tasks           /dept/tasks                CheckSquare  [pending count badge]
Evidence Vault     /dept/evidence             Archive
Self Assessment    /dept/self-assessment      ClipboardCheck
```

**Vendor Reviewer**
```
Vendor Register    /vendor/dashboard          Store
Expiry Tracker     /vendor/expiry             CalendarX
```

**Policy Approver**
```
Inbox              /policy/inbox              Inbox        [pending count badge]
Policy History     /policy/history            History
```

**Read-Only Assessor**
```
Dashboard          /assessor/dashboard        BarChart3
Reports            /assessor/reports          Library
Ask AI             /assessor/chat             Bot
```

### Role Assumption State
When a user is operating under an assumed role, the sidebar switches to show the **assumed role's nav items**. The original role sidebar is replaced entirely. The topbar assumption bar (see below) is the indicator.

---

## 6. TOPBAR COMPONENT

### Structure (left to right)
```
[Hamburger - mobile only] [Logo + ComplySense + | + Institution Name]
                                    CENTER: Role Assumption Banner (when active)
                           [Dark Mode Toggle] [Notification Bell] [Avatar Menu]
```

### Role Assumption Banner
Appears as a full-width amber bar inside the topbar when `role_assumption_sessions.is_active = true`.
```
┌─────────────────────────────────────────────────────────────────────────┐
│  ⚠ Operating as: Compliance Officer  |  Exit Assumed Role               │
└─────────────────────────────────────────────────────────────────────────┘
Background: amber-50, border-bottom: amber-400, text: amber-800
"Exit Assumed Role" is a button → POST /api/auth/exit-role-assumption → clears session → redirect to original role dashboard
```

### Notification Bell
- Icon: Bell (lucide), size 20px
- Badge: red circle with unread count (max "9+")
- Click: opens a Popover (not a new page)
- Popover shows last 10 notifications sorted by created_at DESC
- Each notification row: icon (by type), title, relative timestamp, unread dot
- "Mark all as read" button at top of popover
- "View all" link at bottom → /*/notifications (role-specific notifications page)
- Polling: GET /api/notifications?limit=10&unread=true every 30 seconds via setInterval

### Notification Type Icons
```
task_assigned         → CheckSquare (blue)
evidence_approved     → CheckCircle (green)
evidence_rejected     → XCircle (red)
incident_logged       → Siren (red)
policy_pending        → FileText (amber)
control_overdue       → Clock (red)
vendor_risk_flagged   → AlertTriangle (orange)
```

### Avatar Menu (Dropdown)
```
[Avatar initials circle — primary color]
Full Name
Email (secondary text)
Role badge

────────────────
Profile Settings  → /profile (future page, placeholder for now)
────────────────
Logout  → POST /api/auth/logout → clear localStorage → /login
```

---

## 7. DASHBOARD LAYOUT (DashboardLayout.tsx)

```
<html class="light | dark">
  <body class="bg-background text-text-primary">
    <div class="flex h-screen overflow-hidden">
      <Sidebar />                          // 240px, fixed
      <div class="flex flex-col flex-1 overflow-hidden">
        <Topbar />                         // 56px, fixed
        [RoleAssumptionBar if active]      // 40px when shown
        <main class="flex-1 overflow-y-auto bg-background p-6">
          <PageShell>
            {children}
          </PageShell>
        </main>
      </div>
    </div>
  </body>
</html>
```

---

## 8. SHARED COMPONENT SPECS

### PageShell.tsx
```
Props: title, subtitle?, breadcrumbs?, actions? (ReactNode — buttons for top-right)
Renders:
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        [Breadcrumb if provided]
        <h1 class="text-2xl font-bold text-text-primary">{title}</h1>
        <p class="text-sm text-text-secondary mt-1">{subtitle}</p>
      </div>
      <div class="flex gap-2">{actions}</div>
    </div>
    {children}
  </div>
```

### DataTable.tsx
```
Props: columns[], data[], loading, onRowClick?, pagination, filters?
Features:
  - Column headers: sortable (click to toggle asc/desc)
  - Row hover: slate-50 background
  - Row click: calls onRowClick(row) — navigate to detail
  - Pagination: "Showing 1–20 of 143 results" | Prev | Page numbers | Next
  - Page size selector: 10 / 20 / 50
  - Loading: skeleton rows (5 rows of shimmer)
  - Empty: centered icon + message + optional CTA button
  - Checkbox column (leftmost) when bulk actions exist
  - Bulk action bar appears above table when rows selected

Column definition:
  { key, label, sortable?, render?(value, row) => ReactNode, width? }
```

### StatusBadge.tsx
```
Props: status (string)
Renders a pill badge using the Status → Color mapping from section 1.
Always capitalized, space-replaced-with-hyphen for display.
E.g. "not_started" → "Not Started" in gray badge
```

### FileUpload.tsx
```
Props: accept, maxSizeMB, onFile(file), label, hint?
Renders:
  Dashed border dropzone (24px border-dashed, border-slate-300, rounded-lg)
  Center: Upload cloud icon + label + "or click to browse" + hint
  On hover: border-primary, bg-primary-light
  On file selected: shows filename, size, type icon, X to remove
  Validation: client-side size check before upload, mime type check
  Disabled state: grayed out with "Upload in progress..."
  Error state: red border + error message below
```

### ConfirmModal.tsx
```
Props: open, title, description, confirmLabel, confirmVariant (default|destructive), onConfirm, onCancel
Uses shadcn AlertDialog
Destructive actions: confirmVariant="destructive" → red button
Always shows Cancel + Confirm buttons
Never auto-closes — wait for onConfirm callback to resolve
```

### AIPanel.tsx (Right Drawer)
```
Props: open, onClose, title, children
Renders as shadcn Sheet (side="right", width=420px)
Header: title + X close button
Body: scrollable content area
Footer: optional action buttons slot

States:
  loading  → full panel skeleton (3 content blocks)
  error    → red alert with retry button
  empty    → centered message "Ask something to get started"
  result   → formatted output (see Doc 7 for per-role specs)

The AIPanel is a controlled component — parent owns open state.
Triggered by a button on the page. Never auto-opens.
```

---

## 9. TOAST SYSTEM

```
Position: bottom-right
Duration: success=3s, error=5s, loading=persistent until resolved
Library: shadcn/ui Toast (Radix Toast primitive)

Usage pattern:
  toast.success("Evidence approved successfully")
  toast.error("Failed to upload. File size exceeds 10MB.")
  toast.loading("Generating AI report...") → toast.dismiss() when done

Never show raw error messages from API. Map to user-friendly text.
```

---

## 10. AUTH LAYOUT (AuthLayout.tsx)

```
Full screen, no sidebar or topbar.
Split layout on desktop:
  Left 45%: Brand panel
    - Dark blue background (#1E3A5F)
    - ComplySense logo (shield icon + text) centered top
    - Tagline: "Intelligent GRC for Indian Universities" 
    - Bottom: 3 feature bullets with check icons
      ✓ DPDP Act 2023 Ready
      ✓ CERT-In Incident Management
      ✓ AI-Powered Compliance
  Right 55%: Form panel
    - White background
    - Vertically centered form
    - Max-width 400px centered

Mobile: full width, no left panel, logo at top of form
```

---

## 11. AUTH PAGES

### LOGIN — /login

**Purpose:** Entry point for all roles. JWT returned on success.

**Form fields:**
```
Email address
  type="email", required, placeholder="you@institution.ac.in"
  Validation: must be valid email format

Password
  type="password" with show/hide toggle (Eye icon)
  required

Remember me — checkbox (extends session to 7 days via refresh token)

[Sign In button] — full width, primary color, loading spinner on submit
[Forgot password?] — link below button → /forgot-password
```

**Submit behavior:**
```
POST /api/auth/login
body: { email, password }

Success (200):
  Store access_token in memory (Zustand authStore)
  Store refresh_token in httpOnly cookie (handled by backend)
  Decode JWT → extract { user_id, role, institution_id, full_name }
  Store in authStore
  Redirect to role-specific dashboard:
    Super Admin         → /super-admin/dashboard
    Institution Admin   → /admin/dashboard
    Compliance Officer  → /compliance/dashboard
    IT Security Officer → /security/dashboard
    Auditor             → /auditor/workspace
    Department Reviewer → /dept/dashboard
    Vendor Reviewer     → /vendor/dashboard
    Policy Approver     → /policy/inbox
    Read-Only Assessor  → /assessor/dashboard

Error (401 - invalid credentials):
  Inline error below password field: "Invalid email or password"
  Do not clear password field

Error (423 - account locked):
  Show locked state:
  Red banner: "Account locked due to 5 failed attempts."
  Countdown timer: "Try again in 14:32" (uses blocked_until from backend)
  Sign In button disabled until countdown reaches 0
  Countdown re-checks every second client-side
  
Error (403 - account inactive):
  "Your account has been deactivated. Contact your administrator."
```

**Route guard:** If already logged in → redirect to role dashboard immediately.

---

### FORGOT PASSWORD — /forgot-password

**Form:**
```
Email address — type="email", required
[Send Reset Link] — full width primary button
[Back to login] — ghost button below
```

**Submit:**
```
POST /api/auth/forgot-password
body: { email }

Always show success state after submission (do not confirm if email exists — security):
Success state:
  Green check icon (large, centered)
  "Check your email"
  "If an account exists for {email}, we sent a password reset link."
  "The link expires in 15 minutes."
  [Resend email] — ghost button, disabled for 60s after send (countdown shown)
  [Back to login] — link
```

---

### RESET PASSWORD — /reset-password/:token

**On load:**
```
GET /api/auth/validate-reset-token?token=:token
  Invalid/expired → show error state:
    Red X icon + "This link has expired or is invalid."
    [Request new link] → /forgot-password
  Valid → show form
```

**Form:**
```
New password
  type="password" with show/hide toggle
  Validation rules shown inline as checkmarks:
    ✓ At least 8 characters
    ✓ At least one uppercase letter
    ✓ At least one number
    Rules turn green as user types

Confirm new password
  type="password"
  Validation: must match new password

[Set New Password] — primary button, disabled until both fields valid
```

**Submit:**
```
POST /api/auth/reset-password
body: { token, new_password }

Success:
  "Password updated successfully"
  Auto-redirect to /login after 2 seconds
  
Error (token expired during form fill):
  "This link has expired. Request a new one."
  [Request new link] → /forgot-password
```

---

## 12. ROUTE GUARDS

### ProtectedRoute.tsx
```
Checks authStore for valid access_token
If no token → redirect to /login, preserve intended URL as redirect param
If token expired → attempt silent refresh via POST /api/auth/refresh
  Refresh success → continue
  Refresh fail    → clear authStore → /login
```

### RoleRoute.tsx
```
Props: allowedRoles: string[]
Checks authStore.role (or active assumed role)
If role not in allowedRoles → redirect to their correct dashboard
Never show a 403 page — always redirect silently
```

### Route structure:
```
/                    → redirect to role dashboard or /login
/login               → AuthRoutes (no auth required)
/forgot-password     → AuthRoutes (no auth required)
/reset-password/:token → AuthRoutes (no auth required)

/super-admin/*       → SuperAdminRoutes  (RoleRoute: ["Super Admin"])
/admin/*             → AdminRoutes       (RoleRoute: ["Institution Admin"])
/compliance/*        → ComplianceRoutes  (RoleRoute: ["Compliance Officer"])
/security/*          → SecurityRoutes    (RoleRoute: ["IT Security Officer"])
/auditor/*           → AuditorRoutes     (RoleRoute: ["Auditor"])
/dept/*              → DeptRoutes        (RoleRoute: ["Department Reviewer"])
/vendor/*            → VendorRoutes      (RoleRoute: ["Vendor Reviewer"])
/policy/*            → PolicyRoutes      (RoleRoute: ["Policy Approver"])
/assessor/*          → AssessorRoutes    (RoleRoute: ["Read-Only Assessor"])
```

Role assumption overrides: if user has active assumed role session, RoleRoute checks assumed role instead of primary role, and assumed role's routes are accessible.

---

## 13. NOTIFICATION SYSTEM

### Polling mechanism
```typescript
// In DashboardLayout useEffect:
const poll = setInterval(async () => {
  const res = await api.get('/notifications?limit=10&unread=true')
  notificationStore.setNotifications(res.data.notifications)
  notificationStore.setUnreadCount(res.data.unread_count)
}, 30000)
return () => clearInterval(poll)
```

### Full Notifications Page (/*/notifications)
Every role has a notifications route in their prefix.
```
PageShell: title="Notifications", actions=[Mark All Read button]

Filter tabs: All | Unread | [type filters as chips]

Table view:
  Type icon | Title | Message (truncated 1 line) | Timestamp | Read status dot
  Row click → navigate to related entity:
    task_assigned        → /dept/tasks/:task_id (or /compliance/tasks/:task_id)
    evidence_approved    → /dept/evidence
    evidence_rejected    → /dept/evidence
    incident_logged      → /security/incidents/:incident_id
    policy_pending       → /policy/inbox
    control_overdue      → /compliance/controls/:assignment_id
    vendor_risk_flagged  → /vendor/dashboard

Empty state: Bell icon + "You're all caught up"
```