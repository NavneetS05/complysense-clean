# ComplySense UI Specification
# Document 4 of 7 — IT Security Officer (6 Pages)

Role: IT Security Officer | Route prefix: /security
This role is high-frequency, real-time during incidents. UI must be fast, clear, and stress-resistant.
The Incident Command Center is the most operationally critical page in the entire application.

---

### PAGE: Technical Control Health Dashboard
Route: /security/dashboard

**Purpose:** Morning status check. IT-specific controls, recent incidents, CERT-In compliance posture.

**Layout:**
```
PageShell title="Security Dashboard"
[Critical Alert Banner — conditional]
[5 KPI Cards]
[2-column: IT Control Status | Active Incidents]
[Bottom: CERT-In Compliance Timeline]
```

**Critical Alert Banner:**
```
Shown only when there is an open incident with severity=critical or cert_in_reported=false and deadline approaching (<2 hours remaining).
Red full-width banner (dismissable per session, not permanently):
  🚨 Active Critical Incident: {incident_title} — CERT-In deadline in 1h 23m
  [Manage Incident →] → /security/incidents/:incident_id
```

**KPI Cards (5):**
```
IT Controls Assigned    N total — X compliant, Y failing
  Link → /security/controls

Open Incidents          N
  Color: red if any open, green if zero
  Link → /security/incidents

CERT-In Pending         N incidents not yet reported
  Color: red if any, green if zero

Critical Severity       N open critical incidents
  Always red if >0

Last Incident Closed    relative date ("3 days ago") or "No incidents this month" (green)
```

Data source: GET /api/security/dashboard-stats

**IT Control Status (left column):**
```
Card title: "Assigned Controls"
Horizontal progress breakdown:
  Compliant     ████████░░  8  (green)
  In Progress   ███░░░░░░░  3  (blue)
  Non-Compliant ██░░░░░░░░  2  (red)
  Not Started   █░░░░░░░░░  1  (gray)

Below: list of 5 most critical non-compliant controls:
  [Control ID] [Title truncated] [Due date] [Red badge: Non-Compliant]
  Each row: [Review →] link → /security/controls

[View All Controls →] link
```

**Active Incidents (right column):**
```
Card title: "Active Incidents"
List of all open/investigating/contained incidents sorted by severity DESC, created DESC:

Each row:
  [Severity dot — red/orange/amber/green] {Title}
  {incident_type badge} | Detected: {relative time}
  CERT-In: [Filed ✓ green] or [DUE IN 2h 15m — amber/red countdown]
  [View →] → /security/incidents/:id

Empty state: Shield check icon + "No active incidents" (green)
[+ Log New Incident] button at bottom of card
```

**CERT-In Compliance Timeline (bottom full width):**
```
Card title: "Incident History — Last 90 Days"
Timeline chart (recharts BarChart):
  X-axis: dates (weekly buckets)
  Y-axis: incident count
  Bars stacked: reported on time (green) | reported late (amber) | not reported (red)
  Tooltip: "Week of Aug 12: 2 incidents, 1 on time, 1 late"

Below chart: compliance rate stat:
  "CERT-In Reporting: 85% on time in last 90 days"
```

---

### PAGE: Incident Register
Route: /security/incidents

**Purpose:** Full list of all incidents. The entry point to managing any incident.

**Layout:**
```
PageShell title="Incidents"
  actions=[+ Log New Incident]
[Summary status tabs]
[Filter bar]
[Incidents Table]
```

**Summary Status Tabs:**
```
[All ({N})] [Open ({N})] [Investigating ({N})] [Contained ({N})] [Resolved ({N})] [Closed ({N})]
Tabs show counts. Active tab filters table.
```

**Filter Bar:**
```
[Search — by title or description]
[Severity: All | Critical | High | Medium | Low]
[Type: All | Data Breach | Unauthorized Access | Ransomware | Phishing | System Failure | Other]
[CERT-In: All | Reported | Not Reported | Overdue]
[Date range picker]
```

**Incidents Table:**
```
Columns:
  Severity | Title | Type | Status | Detected At | CERT-In Deadline | Reported | Assigned To | Actions

Severity: colored dot + text badge
Title: bold, truncated 1 line, row click → /security/incidents/:id
Type: badge
Status: StatusBadge
Detected At: "Aug 12, 2:34 PM" + relative "(3 hours ago)"
CERT-In Deadline:
  If reported: "Filed ✓" green
  If deadline passed and not reported: "OVERDUE" red badge (blinking animation subtle)
  If deadline upcoming: countdown "1h 45m left" — amber if <2h, red if <30min
  If not applicable: "—"
Reported: Yes (green check) / No (red X)
Assigned To: name

Actions per row:
  [View] → /security/incidents/:id
  [Close] — available if resolved. ConfirmModal: "Mark as closed?"
  [Delete] — ConfirmModal — only if status=open and no timeline entries

Empty state: Shield icon + "No incidents logged" [+ Log New Incident]
```

---

### PAGE: Log New Incident
Route: /security/incidents/new

**Purpose:** Fast intake form. Submitting this starts the CERT-In clock. Speed is critical.

**Layout:**
```
PageShell
  title="Log New Incident"
  breadcrumbs=[Incidents → New Incident]
[Urgency Banner]
[2-column form]
```

**Urgency Banner (always shown):**
```
Amber info banner:
ℹ Logging an incident will start the CERT-In 6-hour reporting clock.
The deadline is calculated from the Detection Date & Time you enter below.
```

**Form (2-column, left-right split):**
```
LEFT COLUMN:
  Incident Title*
    text input
    placeholder "Brief, clear description (e.g. 'Ransomware on Lab Network Server')"
    max 255 chars, char counter shown

  Incident Type*
    Select:
      Data Breach
      Unauthorized Access
      Ransomware
      Phishing Attack
      System Failure
      DDoS Attack
      Other

  Severity*
    Large radio card buttons (2x2 grid):
      ┌──────────────┐  ┌──────────────┐
      │ 🔴 Critical  │  │ 🟠 High      │
      │ Immediate    │  │ Urgent       │
      │ action req.  │  │ response     │
      └──────────────┘  └──────────────┘
      ┌──────────────┐  ┌──────────────┐
      │ 🟡 Medium    │  │ 🟢 Low       │
      │ Monitor      │  │ Routine      │
      │ closely      │  │ handling     │
      └──────────────┘  └──────────────┘

  Description*
    textarea 5 rows
    placeholder "Describe what happened, what was observed, and initial findings"

RIGHT COLUMN:
  Date & Time Occurred*
    datetime-local input
    "When did the incident occur?"

  Date & Time Detected*
    datetime-local input
    "When was the incident first detected?"
    Live helper text below: "⏰ CERT-In deadline: {detected_at + 6h formatted}"
    Updates as user types detected time

  Affected Systems
    textarea 3 rows
    placeholder "IP addresses, hostnames, system names (comma separated)"

  Affected Data Categories
    Multi-select checkboxes:
      □ Student Personal Data
      □ Staff Personal Data
      □ Financial Records
      □ Research Data
      □ Authentication Credentials
      □ System Configuration
      □ Other

  DPDP Notification Required
    Toggle Switch with label
    Helper text: "Enable if personal data of individuals was compromised"
    When toggled ON: amber info box:
      "DPDP Act 2023 Section 8(6) may require notification to Data Protection Board and affected individuals."

  Assign To
    Searchable user select (IT Security Officers)
    Default: current user
```

**Form Footer:**
```
[Cancel — ghost button] [Save as Draft — outline button] [Log Incident — primary button]

Log Incident:
  POST /api/incidents {all fields}
  Backend calculates cert_in_deadline = detected_at + 6 hours
  On success: redirect to /security/incidents/:new_id immediately
  Toast: "Incident logged. CERT-In deadline: {datetime}"
```

---

### PAGE: Incident Command Center ← MOST CRITICAL PAGE
Route: /security/incidents/:incident_id

**Purpose:** Live incident management room. The CERT-In 6-hour clock ticks here. AI drafts the report. Every action is logged.

**Layout:**
```
Custom header replaces PageShell title area:
  [Incident title — large] [Severity badge] [Status badge] [Edit] [⋯ More actions]
  [Incident type badge] | Detected: {datetime} | Assigned to: {name}

[CERT-In Timer Bar — full width, always visible]

[3-column layout]:
  Left 30%:   CERT-In Checklist + DPDP Panel
  Center 40%: Incident Details + Affected Systems + Resolution
  Right 30%:  Timeline + AI Draft Panel
```

---

**CERT-In Timer Bar (full width, sticky below topbar):**
```
When cert_in_reported = false AND deadline not passed:
┌─────────────────────────────────────────────────────────────────────────────┐
│ ⏱ CERT-In Deadline                                                          │
│ [BIG COUNTDOWN: 04 : 23 : 17]  hours  minutes  seconds                     │
│ Deadline: Aug 12, 2025 at 8:47 PM  |  Detected: Aug 12 at 2:47 PM         │
│                              [Mark as Reported →] button (primary)          │
└─────────────────────────────────────────────────────────────────────────────┘

Color states:
  >2 hours remaining:   blue bar background
  1-2 hours remaining:  amber bar background, amber text
  <1 hour remaining:    red bar background, red text, pulsing animation
  Passed (not reported): red bar, "DEADLINE PASSED — OVERDUE", no countdown

When cert_in_reported = true:
┌────────────────────────────────────────────────────────┐
│ ✓ CERT-In Reported  |  Filed: Aug 12 at 6:21 PM       │
└────────────────────────────────────────────────────────┘
Green bar background.

Countdown implementation:
  useEffect with setInterval(1000)
  Calculate remaining = cert_in_deadline - Date.now()
  Format to HH:MM:SS
  Cleanup on unmount
```

---

**LEFT COLUMN — CERT-In Checklist + DPDP:**

**CERT-In Checklist Card:**
```
Title: "CERT-In Response Steps"
Progress: "5 / 8 steps completed" + mini progress bar

Checklist items (from CERT-In 2022 mandatory response):
  □ 1. Contain the incident (isolate affected systems)
  □ 2. Document initial findings
  □ 3. Notify internal stakeholders
  □ 4. Preserve evidence (logs, screenshots)
  □ 5. Identify affected data categories
  □ 6. Draft CERT-In report
  □ 7. Submit report to CERT-In portal
  ☑ 8. Update incident status

Each checkbox:
  Click to check → PATCH /api/incidents/:id/checklist { step: N, checked: true }
  Checked items: strikethrough, green checkmark
  Written to incident_timeline as action_taken = "Completed checklist step N: {description}"

[AI: Draft CERT-In Report] button below checklist
  → POST /ai/security/cert-in-draft { incident data }
  → Opens AI Draft Panel in right column (see below)
```

**DPDP Notification Panel (below checklist):**
```
Title: "DPDP Notification"
Toggle: dpdp_notification_required (synced from DB)
  When ON: Amber card with:
    "Personal data breach may require notification to:"
    • Data Protection Board of India
    • Affected individuals (if feasible)
    Per DPDP Act 2023, Section 8(6)
    
    Notification Status:
      [Not notified yet — Send notification details]
      PATCH /api/incidents/:id { dpdp_notified_at: now }
      Shows timestamp when marked notified
```

---

**CENTER COLUMN — Incident Details:**

**Incident Details Card:**
```
Editable fields (inline edit — click field to edit, click away to save):
  Description: textarea, auto-save on blur
  Affected Systems: textarea
  Affected Data Categories: multi-select (same as new incident form)
  Status: Select dropdown (open → investigating → contained → resolved → closed)
    Status change → PATCH /api/incidents/:id { status }
    → timeline entry auto-created
    → notification to assigned_to user

Non-editable (set on creation):
  Incident Type: badge
  Occurred At: datetime
  Detected At: datetime
  Reported By: name + email
  Created At: datetime
```

**Resolution Section (visible when status = resolved or closed):**
```
Resolved At: datetime (auto-set or manually entered)
Resolution Notes:
  textarea — required before closing
  PATCH /api/incidents/:id { resolution_notes, resolved_at }

[Close Incident] button (visible when resolved and resolution_notes filled)
  ConfirmModal: "Close this incident? It will be archived."
  PATCH status = closed
```

---

**RIGHT COLUMN — Timeline + AI Draft:**

**Incident Timeline Card:**
```
Title: "Response Timeline"
Vertical timeline (oldest at bottom, newest at top):

Each entry:
  ● [User Avatar 24px] {action_taken} — {relative time}
  Full datetime on hover (tooltip)

Entry types display differently:
  System auto entries (status changes): gray dot, italic text
  Manual timeline entries: blue dot, regular text
  Checklist completions: green dot
  AI report drafted: purple dot

[+ Add Timeline Entry] button at top:
  Opens inline input below button:
  Textarea: "Describe action taken..."
  [Cancel] [Add Entry]
  POST /api/incidents/:incident_id/timeline { action_taken }
  New entry appears at top
```

**AI Draft Panel (replaces timeline when AI draft requested):**
```
Activated by [AI: Draft CERT-In Report] button in checklist.

Header: "AI — CERT-In Report Draft" [← Back to Timeline]

Loading state (10-20 seconds):
  Skeleton content
  Status messages rotating:
    "Reviewing incident details..."
    "Checking CERT-In 2022 requirements..."
    "Drafting mandatory report fields..."
    "Finalizing report..."

Result state:
  Scrollable report draft in monospace font (this is a formal document):
  
  CERT-In INCIDENT REPORT
  ─────────────────────────────
  Organization: {institution_name}
  Contact: {assigned_to email + phone}

  1. INCIDENT DETAILS
  Nature: {incident_type readable}
  Severity: {severity}
  Date/Time Occurred: {occurred_at}
  Date/Time Detected: {detected_at}
  
  2. AFFECTED SYSTEMS
  {affected_systems}
  
  3. AFFECTED DATA
  {affected_data_categories}
  
  4. IMPACT ASSESSMENT
  [AI generated based on incident type and data categories]
  
  5. IMMEDIATE ACTIONS TAKEN
  [AI generated from timeline entries + checklist steps]
  
  6. CONTACT PERSON FOR CERT-IN FOLLOW-UP
  {assigned_to name, designation, phone, email}
  
  [FILL IN: {any field where data was not provided}]
  ─────────────────────────────

  Action buttons below draft:
  [Copy to Clipboard] [Download as .txt] [Mark CERT-In as Reported]

  "Mark CERT-In as Reported" button:
    ConfirmModal: "Confirm you have submitted this report to the CERT-In portal."
    PATCH /api/incidents/:id { cert_in_reported: true, cert_in_reported_at: now }
    Timer bar turns green, toast "CERT-In reported. Well done."
    Timeline entry auto-created.

  [Regenerate Draft] — ghost button (re-runs AI with current data)

Error state:
  "Failed to generate draft. Check your internet connection."
  [Retry] button
```

---

### PAGE: IT Control Assignments
Route: /security/controls

**Purpose:** Controls specifically assigned to IT Security Officer. Upload evidence, update status.

**Layout:**
```
PageShell title="My Controls"
  subtitle="Controls assigned to IT Security role"
[Filter bar]
[Controls Table]
```

**Filter Bar:**
```
[Framework: All | ISO 27001:2022 | NIST CSF 2.0 | CERT-In 2022]
[Status: All | Not Started | In Progress | Submitted | Compliant | Non-Compliant]
[Due: All | Overdue | Due This Week | Due This Month]
[Search — by control ID or title]
```

**Controls Table:**
```
Columns:
  Control ID | Title | Framework | Status | Evidence | Due Date | Actions

Control ID: monospace
Framework: colored badge
Status: StatusBadge
Evidence: "2 files" (count of linked evidence) or "None" in amber
Due Date: relative, red if overdue

Actions per row:
  [Upload Evidence] — opens FileUpload inline (see evidence upload spec below)
  [Update Status] — inline dropdown select, saves on change
  [View Detail] → /compliance/controls/:assignment_id (shared detail page, read their own)

Row click → expand inline (not navigate):
  Expanded row shows:
    Control description (from MongoDB)
    Evidence required list
    Linked evidence files (download links)
    Notes (read-only)
```

---

### PAGE: Technical Evidence Upload
Route: /security/evidence

**Purpose:** Dedicated upload center for IT-specific evidence — logs, scan reports, configuration screenshots.

**Layout:**
```
PageShell title="Evidence Upload"
  subtitle="Upload technical evidence for your assigned controls"
[Upload Area Card]
[My Uploaded Evidence Table]
```

**Upload Area Card:**
```
Step 1: Select Control
  Searchable select of controls assigned to this user
  Shows: "[NIST-ID.AM-1] Asset inventory" style
  
Step 2: Upload File
  FileUpload component
  Accepted: PDF, PNG, JPG, XLSX, DOCX, TXT, LOG up to 10MB
  
Step 3: Description (optional)
  textarea: "Describe what this evidence demonstrates"
  placeholder "e.g. Screenshot showing MFA enabled for all admin accounts as of Aug 2025"

[Pre-Flight AI Check] button (appears after file selected):
  → POST /ai/dept/preflight-check { control_requirement, file_metadata, content_preview }
  → Inline result below file:
    PASS:  ✅ green: "Evidence appears to meet the requirement for {control_title}"
    WARN:  ⚠️ amber: "Evidence may be incomplete: Missing date/timestamp. Consider re-uploading with visible date."
    FAIL:  ❌ red: "This file does not appear to meet the requirement. {reason}"
  User can proceed despite WARN or FAIL (with a confirmation for FAIL)

[Upload Evidence] button — primary
  POST /api/evidence { assignment_id, control_id, file, description }
  On success: toast "Evidence submitted for review", table refreshes
```

**My Uploaded Evidence Table:**
```
Columns:
  File Name | Control | Framework | Status | Submitted | Pre-Flight | Actions

Pre-Flight: PASS / WARN / FAIL badge (stored on upload)
Status: pending (amber) / approved (green) / rejected (red)
  Rejected rows: expandable rejection reason inline below row:
    "Rejected: Missing date on access log. Please re-upload."
    [Re-upload] button → opens Upload Area with control pre-filled

Actions per row:
  [Download] — signed URL
  [Delete] — only if status=pending, ConfirmModal

Filter: by status, by framework, by date range
Pagination: 20 per page
```