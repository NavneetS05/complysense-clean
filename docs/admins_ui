# ComplySense UI Specification
# Document 2 of 7 — Super Admin & Institution Admin

---

## SUPER ADMIN PAGES

Role: Super Admin | Route prefix: /super-admin
Access: Only users with role_name = "Super Admin"
Note: Super Admin sees all institutions. No institution_id filter on their queries — they query the entire platform.

---

### PAGE: Global Health Dashboard
Route: /super-admin/dashboard

**Purpose:** Platform-wide status at a glance. Super Admin opens this only when the AI anomaly agent has flagged something or for periodic checks.

**Layout:**
```
PageShell title="Platform Overview"
  [AI Anomaly Alert Banner — conditional]
  [4 Stat Cards row]
  [Institution Health Table]
  [2-column bottom: Recent Audit Events | Platform Activity Chart]
```

**AI Anomaly Alert Banner:**
```
Appears only when AI service flags anomalies (polled from GET /api/super-admin/anomaly-alerts)
Amber dismissable banner above stat cards:
⚠ AI Alert: Unusual admin activity detected at Jaipur National University — 14 role changes in the last hour.
[Investigate →] links to /super-admin/audit-trail?institution_id=&type=role_change
[Dismiss] removes banner until next anomaly
```

**Stat Cards (4):**
```
Total Institutions   — integer, link → /super-admin/tenants
Active Users         — integer (is_active=true across all institutions)
Incidents This Week  — integer, red if >5
Avg Compliance Score — percentage across all institutions
```

Data source: GET /api/super-admin/stats

**Institution Health Table:**
```
Columns:
  Institution Name | Type | City | Users | Compliance % | Status | Last Active | Actions

Status badge:
  Healthy  (compliance >80%, no critical incidents) → green
  Warning  (compliance 50–80% or open incidents)    → amber
  Critical (compliance <50% or critical incident)   → red

Compliance % shown as:
  [Progress bar 0–100% in badge color] 72%

Actions column per row:
  [View] → /super-admin/tenants/:institution_id
  [Audit] → /super-admin/audit-trail?institution_id=

Table features: search by name, filter by status, filter by type, sortable columns
Pagination: 20 per page

Empty state: "No institutions registered yet. Create your first tenant."
  [+ Add Institution] button
```

Data source: GET /api/super-admin/institutions?search=&status=&type=

**Recent Audit Events (left column, bottom):**
```
List of last 10 audit_logs entries across all institutions
Each row: [Action icon] Institution Name | User Name | Action description | Timestamp
Action description maps action_type to readable text:
  user_created     → "Created user {entity_id}"
  role_changed     → "Changed role"
  login_failed     → "Failed login attempt"
  evidence_approved → "Approved evidence"
etc.
[View full audit trail →] → /super-admin/audit-trail
```

Data source: GET /api/super-admin/recent-audit?limit=10

**Platform Activity Chart (right column, bottom):**
```
Line chart (recharts LineChart)
X-axis: last 14 days
Y-axis: count
Two lines: "Logins" (blue) | "Actions" (green)
No tooltip interaction required — just visual
```

---

### PAGE: Tenant Manager
Route: /super-admin/tenants

**Purpose:** View all institutions, create new tenants, activate/deactivate.

**Layout:**
```
PageShell
  title="Institutions"
  actions=[+ Add Institution button (opens modal)]
  [Search + Filter row]
  [Institutions Table]
```

**Search + Filter row:**
```
[Search input — placeholder "Search by name or city"]
[Type filter dropdown: All | University | College | Institute]
[Status filter: All | Active | Inactive]
[State filter: All | [Indian states list]]
```

**Institutions Table:**
```
Columns:
  Name | Type | City, State | Staff Count | Status | Created At | Actions

Name: bold, clickable → /super-admin/tenants/:institution_id
Status: Active (green badge) / Inactive (gray badge)
Actions:
  [View] → /super-admin/tenants/:institution_id
  [Deactivate / Activate] → ConfirmModal before action
    Deactivate: "Deactivating will prevent all users at this institution from logging in. Continue?"
    PUT /api/super-admin/institutions/:id/status { is_active: false }
    
Empty state: "No institutions found."
Bulk select: none for this table (operations are per-row)
```

**Add Institution Modal (Dialog):**
```
Title: "Add New Institution"
Form fields:
  Institution Name*      text input
  Type*                  Select: University | College | Institute
  Email                  email input
  Phone                  text input (Indian format hint)
  Address                textarea
  City*                  text input
  State*                 Select (all Indian states)
  Staff Count            number input

[Cancel] [Create Institution] buttons
POST /api/super-admin/institutions
body: { institution_name, institution_type, email, phone, address, city, state, staff_count }
On success: close modal, toast "Institution created", refresh table
On error: inline error below form
```

---

### PAGE: Institution Detail
Route: /super-admin/tenants/:institution_id

**Purpose:** Deep view into one institution — users, departments, recent audit.

**Layout:**
```
PageShell
  title=institution_name
  subtitle="institution_type — city, state"
  breadcrumbs=[Institutions → {name}]
  actions=[Edit | Deactivate/Activate]

[3 Stat Cards: Users | Departments | Compliance %]
[Tabs: Users | Departments | Audit Logs]
```

**Edit Action:** Opens same modal as Add Institution but prefilled.
```
PATCH /api/super-admin/institutions/:id
body: { fields changed }
```

**Tab: Users**
```
Table: Full Name | Email | Role | Status | Last Login | Created At
Role shown as badge
Filter: by role, by status
No edit actions for Super Admin — read only view of institution's users
```

Data source: GET /api/super-admin/institutions/:id/users

**Tab: Departments**
```
Table: Department Name | Code | HOD Name | Reviewer Assigned | Status
Read only
```

**Tab: Audit Logs**
```
Same as Audit Trail page but pre-filtered to this institution_id
Shows last 50 entries
[View Full Audit Trail →] → /super-admin/audit-trail?institution_id=
```

---

### PAGE: Audit Trail Explorer
Route: /super-admin/audit-trail

**Purpose:** Immutable, searchable log of every action across the platform.

**Layout:**
```
PageShell title="Audit Trail"
[Filter bar]
[Audit Logs Table]
```

**Filter Bar:**
```
[Date range picker: From — To]
[Institution dropdown: All | {institution list}]
[Action Type dropdown: All | user_created | login_failed | evidence_approved | role_changed | ...]
[User search: text input — searches by full_name or email]
[Export CSV button — right aligned]
```

**Audit Logs Table:**
```
Columns:
  Timestamp | Institution | User | Role (at time) | Action | Entity Type | Entity ID | IP Address

Timestamp: full datetime, monospace font
Entity ID: UUID in monospace, truncated to first 8 chars with tooltip showing full
IP Address: monospace
Action: human-readable mapping of action_type
No row click — this is a read-only log, no detail page

Pagination: 50 per page (audit logs are high volume)
Default sort: created_at DESC

Export CSV: downloads current filtered results
  GET /api/super-admin/audit-logs?format=csv&{current filters}
```

Data source: GET /api/super-admin/audit-logs?institution_id=&action_type=&user=&from=&to=&page=&limit=

**Empty state:** "No audit logs match your filters."

---

### PAGE: Roles & Permissions
Route: /super-admin/roles

**Purpose:** Read-only view of the RBAC matrix. Seeded data — not editable via UI.

**Layout:**
```
PageShell title="Roles & Permissions" subtitle="Fixed RBAC matrix — contact engineering to modify"

[Roles cards row — 9 cards]
[Permission Matrix Table]
```

**Role Cards (9 cards, 3 per row):**
```
Each card:
  Role name (semibold)
  Description (secondary text, 2 lines)
  Permission count badge: "14 permissions"
```

**Permission Matrix:**
```
Rows: permission_key (all permissions in system)
Columns: each role name

Cell: checkmark (green) or dash (gray) — has permission or not
Table is wide, horizontally scrollable

Group permissions by category (prefix of permission_key):
  view_* — View permissions
  manage_* — Manage permissions
  upload_* — Upload permissions
  approve_* — Approve permissions
  generate_* — Generate permissions
```

Data source: GET /api/super-admin/roles-matrix

---

## INSTITUTION ADMIN PAGES

Role: Institution Admin | Route prefix: /admin
Access: Users with role_name = "Institution Admin"
Scope: All queries filtered by institution_id from JWT

---

### PAGE: Institution Risk Scorecard
Route: /admin/dashboard

**Purpose:** Weekly review dashboard. Shows org-wide compliance health, emerging risks, dept performance.

**Layout:**
```
PageShell title="Risk Overview" subtitle="Last updated: {relative time}"
[4 KPI Cards]
[2-column: Framework Readiness Bars | Department Compliance Heatmap]
[AI Risk Heatmap Panel]
[Bottom row: Upcoming Calendar Events | Recent Activity]
```

**KPI Cards:**
```
Overall Compliance %    — large number, delta vs last month (↑3% green / ↓2% red)
Active Gaps             — count, split: Critical {n} | High {n} | Medium {n}
Overdue Controls        — count, link → compliance controls filtered by overdue
Open Incidents          — count, red if any critical
```

Data source: GET /api/admin/dashboard-stats

**Framework Readiness Bars:**
```
Card title: "Framework Compliance"
One row per framework:
  Framework name | [Progress bar] | Percentage | Trend arrow
  DPDP Act 2023         ████████░░  78%  ↑
  ISO 27001:2022        ██████░░░░  62%  →
  NIST CSF 2.0          ████░░░░░░  41%  ↓
  CERT-In 2022          █████████░  89%  ↑
  UGC Guidelines        ███████░░░  71%  →
  NAAC Criteria 4 & 6   ████████░░  80%  ↑

Progress bar colors: <50% red, 50–75% amber, >75% green
Trend: ↑ green ↓ red → gray
```

Data source: GET /api/admin/framework-readiness

**Department Heatmap:**
```
Card title: "Department Compliance"
Grid of department cards (3 per row):
  [Dept Name] [Score %]
  Color background by score:
    >75%: light green bg, green text
    50–75%: light amber bg, amber text
    <50%: light red bg, red text
Click on dept card → /admin/departments (future: dept detail)
```

**AI Risk Heatmap Panel:**
```
Card with "AI Insights" badge (sparkle icon)
Button: "Generate Risk Prediction" 
  → POST /ai/admin/risk-heatmap with dept_summaries context
  → Loading state in card (skeleton)
  → Result: numbered list of top 5 predicted risks
    1. [Framework] Risk description — Severity badge — Affected dept
Result is displayed in the card (not a separate drawer for this one)
Last generated timestamp shown below button
[Regenerate] button after first generation
```

**Upcoming Calendar Events (bottom left):**
```
Next 7 days of compliance_calendar events
List view:
  [Color dot by event_type] Title | Due Date | Type badge
  Click → /admin/calendar

Event type colors:
  control_due             → blue
  assessment_scheduled    → purple
  evidence_expiry         → amber
  policy_review           → indigo
  vendor_contract_expiry  → orange
  audit_scheduled         → green
```

**Recent Activity (bottom right):**
```
Last 10 audit_log entries for this institution
[Action icon] User name | Action description | Timestamp
No pagination here — just last 10
```

---

### PAGE: Department Manager
Route: /admin/departments

**Layout:**
```
PageShell title="Departments" actions=[+ Add Department]
[Departments Table]
```

**Departments Table:**
```
Columns:
  Department Name | Code | HOD Name | Assigned Reviewer | Status | Actions

Assigned Reviewer: shows full_name if reviewer_user_id set, else "Unassigned" in amber text
Status: Active (green) / Inactive (gray)
Actions per row:
  [Edit] — opens Edit modal
  [Assign Reviewer] — opens Assign modal if no reviewer
  [Deactivate/Activate] — ConfirmModal

Search: by department name or code
Filter: Status (All / Active / Inactive)
Empty state: "No departments created yet." [+ Add Department]
```

**Add/Edit Department Modal:**
```
Title: "Add Department" / "Edit Department"
Fields:
  Department Name*   text input
  Department Code    text input (e.g. "CS", "ADMIN")
  HOD Name           text input
  Status             Switch (Active/Inactive) — edit only

POST /api/admin/departments (add)
PATCH /api/admin/departments/:id (edit)
On success: close modal, toast, refresh table
```

**Assign Reviewer Modal:**
```
Title: "Assign Department Reviewer"
Description: "Select a user with Department Reviewer role to assign to {dept_name}"
Select input: searchable dropdown of users with role = "Department Reviewer"
  Shows: Full Name + email in option
[Cancel] [Assign]
PATCH /api/admin/departments/:id { reviewer_user_id: selected_user_id }
On success: toast "Reviewer assigned", row updates immediately
Creates notification for assigned user: type=task_assigned
```

---

### PAGE: User Lifecycle Manager
Route: /admin/users

**Layout:**
```
PageShell title="Users" actions=[+ Add User]
[Filter row]
[Users Table]
```

**Filter Row:**
```
[Search by name or email]
[Role filter dropdown: All | {9 roles}]
[Status filter: All | Active | Inactive]
```

**Users Table:**
```
Columns:
  Avatar+Name | Email | Role | Department | Status | Last Login | Actions

Avatar: initials circle in primary color
Role: badge
Department: shown for Dept Reviewers only, "—" for others
Status: Active (green) / Inactive (gray)
Last Login: relative time or "Never"

Actions per row:
  [Edit] — opens Edit User modal
  [Deactivate/Activate] — ConfirmModal:
    Deactivate: "This user will be logged out immediately and cannot log in."
    PUT /api/admin/users/:id/status { is_active: false }
  [Reset Password] — sends reset email to user
    POST /api/admin/users/:id/reset-password
    Toast: "Password reset email sent to {email}"

Bulk actions (when rows selected):
  Deactivate Selected | Export Selected
```

**Add User Modal:**
```
Title: "Add User"
Fields:
  Full Name*         text input
  Email*             email input
  Role*              Select dropdown (all 9 roles)
  Department         Select (appears only when role = "Department Reviewer")
  Phone              text input
  Designation        text input (e.g. "Data Protection Officer")

Password: auto-generated. User receives "Set your password" email.
POST /api/admin/users
body: { full_name, email, role_id, department_id?, phone, designation }
On success: toast "User created. Setup email sent.", table refreshes
```

**Edit User Modal:**
```
Same fields as Add but prefilled
Role change: if changed, ConfirmModal: "Changing this user's role will immediately affect their access."
PATCH /api/admin/users/:id
```

---

### PAGE: Compliance Calendar
Route: /admin/calendar

**Layout:**
```
PageShell title="Compliance Calendar" actions=[+ Add Event]
[View Toggle: Month | List]
[Filter: Event Type chips]
[Calendar or List]
```

**Month View:**
```
Standard calendar grid (7 columns, weeks as rows)
Each date cell: event dots (color-coded by type), shows up to 3, "+N more" if overflow
Click date → expands to show all events for that day as popover
Click event → opens Event Detail Popover:
  Title | Type badge | Related entity (link if any) | Due date | Completed toggle
```

**List View:**
```
Grouped by week: "This Week" | "Next Week" | "Month of August" etc.
Each row: [Color dot] Title | Type badge | Due date | Entity link | Completed checkbox
Completed events: strikethrough text, moved to bottom of group
```

**Filter chips:**
```
[All] [Control Due] [Assessment] [Evidence Expiry] [Policy Review] [Vendor Contract] [Audit]
Active chip: primary color bg
```

**Add Event Modal:**
```
Title: "Add Calendar Event"
Fields:
  Title*              text input
  Event Type*         Select (6 options)
  Due Date*           date picker
  Related Entity Type Select: Control | Vendor | Policy | Assessment (optional)
  Related Entity      searchable select (populates based on entity type) (optional)

POST /api/admin/calendar
On success: event appears on calendar immediately
```

---

### PAGE: Executive Reports
Route: /admin/reports

**Purpose:** Generate and view AI-produced compliance summary reports.

**Layout:**
```
PageShell title="Executive Reports" subtitle="AI-generated compliance briefings"
[Generate Report Panel]
[Past Reports Table]
```

**Generate Report Panel (Card):**
```
Card title: "Generate New Report"
Fields:
  Report Type*    Select: NAAC Readiness | ISO Readiness | DPDP Assessment | Custom Summary
  Time Period*    Select: Last 30 days | Last Quarter | Last 6 months | Custom range
  Custom Range    Date range picker (visible only when Custom selected)

[Generate Report] button — primary, full width of card
  → POST /api/admin/reports/generate { report_type, period_from, period_to }
  → Button becomes loading state: "Generating..." (spinner)
  → AI generates HTML/PDF report (can take 10–30 seconds)
  → On completion: toast "Report ready", new row appears in Past Reports table
  → Error: toast "Generation failed. Try again."
```

**Past Reports Table:**
```
Columns:
  Report Name | Type | Period | Generated By | Generated At | Actions

Actions per row:
  [View] → opens report in new tab (PDF or HTML)
  [Download] → downloads file
  [Delete] → ConfirmModal (soft delete or remove from list)

Empty state: "No reports generated yet. Create your first executive briefing."
```