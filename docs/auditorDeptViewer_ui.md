# ComplySense UI Specification
# Document 5 of 7 — Auditor & Department Reviewer

---

## AUDITOR PAGES

Role: Auditor | Route prefix: /auditor
Read-only access to all institutional data. Can add observations. Cannot edit controls, evidence, or policies.
Auditor is seasonal — heavy use during audit cycles, light otherwise.

---

### PAGE: Audit Workspace
Route: /auditor/workspace

**Purpose:** The core working page during an audit cycle. Review controls and evidence, write observations, use AI smart sampling. Everything is read-only except observations.

**Layout:**
```
Custom full-height layout (not standard PageShell padding):
  [Assessment Selector Bar — full width, sticky top]
  [3-panel layout — fills remaining viewport height]:
    Left Panel   25%: Control List
    Center Panel 45%: Evidence Viewer
    Right Panel  30%: Observation Input
```

**Assessment Selector Bar:**
```
"Audit Workspace —"
Assessment dropdown: [Select Assessment ▾] lists all assessments for the institution:
  "{Assessment Name} — {Framework} — {Status} — {Date}"
  Filter shown assessments: completed and in_progress only (draft assessments not auditable)

When assessment selected:
  Shows: "{N} Controls | {N} Evidence Items | {N} Observations"
  [AI: Smart Sample] button — right side of bar
```

**AI Smart Sample:**
```
Trigger: [AI: Smart Sample] button in assessment selector bar
→ POST /ai/audit/smart-sample { evidence_list metadata for current assessment }
→ Loading: button shows spinner, "Analyzing risk..."
→ Result: Highlights risk-priority evidence items in the center panel:

Result popover/tooltip:
  "AI recommends reviewing these {N} items first:"
  Numbered list of evidence IDs with risk reason
  e.g. "evidence-abc123 — High risk: Control non-compliant, no supporting evidence"

Effect on center panel:
  High-priority evidence items get a [★ Priority] gold badge
  Panel scrolls to show first priority item

[Clear Sampling] — resets highlights
```

---

**LEFT PANEL — Control List:**
```
Panel header: "Controls ({N})"
[Search controls — by ID or title]
[Framework filter chips — horizontal scroll]

Control list (virtualized for large sets):
  Each item:
    [Framework color dot] [Control ID monospace]
    Title (truncated 1 line)
    Status badge (compact)
    Evidence count: [📎 3] or [⚠ 0 files] amber if zero
    Observation indicator: [💬 2] if any observations exist

  Active/selected control: primary left border + primary-light bg
  Click → loads control's evidence in center panel

Group by section:
  Collapsible section headers (e.g. "A.5 Organizational Controls (8)")
  Default: all expanded

Scroll position remembered when switching back from center panel
```

**CENTER PANEL — Evidence Viewer:**
```
Panel header:
  [Control ID] — [Control Title]
  Framework badge | Status badge

When no control selected:
  Centered: "Select a control from the list to review evidence"
  Compass icon illustration

When control selected:

  Control Description section (collapsible, default closed):
    Full regulatory description from MongoDB
    Evidence requirements list
    [▼ Show control details] toggle

  Evidence Files section:
    Sub-header: "Evidence ({N} files)"
    
    Each evidence item:
      ┌────────────────────────────────────────────────┐
      │ [★ Priority] [📄 filename.pdf]                 │
      │ Uploaded by: Priya Sharma (Dept Reviewer)      │
      │ Submitted: Aug 10, 2025 at 3:15 PM             │
      │ Status: Approved ✓   Size: 2.4 MB              │
      │ Description: "Access log showing MFA..."       │
      │                                                │
      │ [Preview ▾] [Download] [Add Observation →]    │
      └────────────────────────────────────────────────┘

    [Preview ▾] expands inline:
      PDF: embedded iframe (height 400px, scrollable)
      Image: img with max-height 400px
      Other: "Preview not available — [Download to view]"

    [Add Observation →] button scrolls right panel to observation form
    and pre-fills control_id and evidence_id

  No evidence case:
    Amber banner: "No evidence uploaded for this control"
    If control is non_compliant: red banner instead
```

**RIGHT PANEL — Observation Input:**
```
Panel header: "Observations"

Existing Observations list (top of panel):
  Each observation:
    [Severity chip: finding/observation/recommendation]
    Observation text (full)
    Status badge: open / acknowledged / resolved
    Added: relative time (hover for full datetime)
    ──────────────────────────────────
  
  Linked context per observation:
    If linked to evidence: [📎 filename] link
    If linked to control:  [Control ID] link

  Empty: "No observations yet for this control"

────── Divider ──────

Add Observation section (sticky bottom of panel):
  Card with light-blue header: "Add Observation"
  
  Pre-filled context (read-only chips, dismissable):
    Control: [ISO-A.5.1]  Evidence: [filename.pdf]
    (pre-filled when coming from Add Observation → button, otherwise empty)
  
  Type*:
    Radio buttons — horizontal:
    ○ Finding  ○ Observation  ○ Recommendation
    
  Observation Text*:
    textarea — 5 rows, auto-expand
    placeholder "Describe your finding. Reference the evidence and regulatory requirement."
    Character counter: min 50 chars
    
  [AI: Draft Observation] button (below textarea, ghost style):
    → POST /ai/audit/draft-observation { control details, observation text so far }
    → Streams draft into textarea
    → "AI drafted — review and edit before saving"
    Auditor must edit before submitting (not submit AI text raw)
    
  [Add Observation] — primary button
    POST /api/audit/observations { assessment_id, control_id, evidence_id?, observation_text, severity }
    On success: new observation appears in list above, form resets, toast
    Audit log entry written
```

---

### PAGE: Finding Tracker
Route: /auditor/observations

**Purpose:** All observations the auditor has written across all assessments. Track their resolution.

**Layout:**
```
PageShell title="Observations & Findings"
[Summary counts row]
[Filter bar]
[Observations Table]
```

**Summary Counts (4 inline stat chips):**
```
[Findings: N  red] [Observations: N  blue] [Recommendations: N  amber] [Resolved: N  green]
Clicking a chip filters the table
```

**Filter Bar:**
```
[Search — by observation text or control ID]
[Assessment: All | {assessment list}]
[Severity: All | Finding | Observation | Recommendation]
[Status: All | Open | Acknowledged | Resolved]
[Framework: All | ...]
[Date range]
```

**Observations Table:**
```
Columns:
  Severity badge | Observation (truncated 2 lines) | Control | Assessment | Status | Added | Actions

Severity: color-coded chip
Control: "[ID] Title" truncated
Assessment: name + framework badge
Status: open=red | acknowledged=amber | resolved=green

Row click → opens Observation Detail Drawer

Actions per row:
  [Edit] — opens edit modal (own observations only, not acknowledged/resolved ones)
  [Delete] — ConfirmModal, own observations only while open
```

**Observation Detail Drawer (Sheet right, 480px):**
```
Header: Severity chip + [Edit] [Close]
Body:
  Full observation text
  Type: finding/observation/recommendation
  Control: link → control in workspace
  Evidence: filename link (if linked)
  Assessment: name + framework
  Status: badge
  Added: full datetime
  
  Status History (if status changed):
    Acknowledged by: {name} on {date}
    Resolved by: {name} on {date}
```

---

### PAGE: Report Builder
Route: /auditor/reports

**Purpose:** Compose and generate formal audit reports from completed assessments.

**Layout:**
```
PageShell title="Audit Reports"
  actions=[+ Generate New Report]
[Past Reports Table]
```

**Past Reports Table:**
```
Columns:
  Report Name | Assessment | Framework | Type | Generated | Actions

Actions:
  [View] → /auditor/reports/:report_id
  [Download] — PDF download
  [Delete] — ConfirmModal
```

**+ Generate New Report → Opens full-page modal (Dialog large):**
```
Title: "Generate Audit Report"
Step 1: Select Assessment
  [Assessment dropdown — completed assessments only]
  On selection: preview shows:
    "This assessment has {N} controls, {N} observations, {N} gaps"
    Framework badge, completion date

Step 2: Report Configuration
  Report Name*      text input (default: "{Framework} Audit Report — {Month Year}")
  Report Type*      Select: NAAC | ISO Readiness | DPDP Assessment | Custom
  
  Include sections (checkboxes — all checked by default):
    ☑ Executive Summary (AI-generated)
    ☑ Compliance Score Overview
    ☑ Findings Summary (from observations)
    ☑ Control-by-Control Detail
    ☑ Evidence Index
    ☑ Gap Analysis
    ☑ Recommendations
    ☑ Appendix: Assessment Responses

Step 3: Review & Generate
  [Generate Report] button
    → POST /api/audit/reports/generate { assessment_id, report_name, report_type, sections }
    → AI generates executive summary section
    → System compiles remaining sections from DB
    → Loading overlay with progress:
      "Compiling assessment data..."
      "Generating executive summary..."
      "Building evidence index..."
      "Finalizing report..."
    → On complete: dialog closes, new row in table, toast "Report ready"
    → Auto-open: /auditor/reports/:new_id in new tab
```

---

### PAGE: Report View
Route: /auditor/reports/:report_id

**Purpose:** Read the generated audit report. Download it.

**Layout:**
```
PageShell
  title={report_name}
  breadcrumbs=[Reports → {name}]
  actions=[Download PDF | Share (copy link)]

[Report content — rendered HTML/PDF iframe]
```

**Report Content:**
```
Rendered inside a white card with 64px horizontal padding
Report has its own internal navigation:
  Sticky left mini-nav (like a document outline):
    1. Executive Summary
    2. Compliance Score
    3. Findings
    4. Control Detail
    5. Evidence Index
    6. Gaps
    7. Recommendations
    8. Appendix

Each section styled formally:
  Section headings: serif-like weight, border-bottom divider
  Tables: full-width, alternating row colors
  Severity indicators: colored labels

Download PDF:
  GET /api/audit/reports/:id/download → binary PDF response → browser download
```

---

## DEPARTMENT REVIEWER PAGES

Role: Department Reviewer | Route prefix: /dept
Scoped to ONE department. This user is NOT a compliance expert.
The UI must be simple, task-driven, and jargon-free. Everything is plain language.

---

### PAGE: My Department Dashboard
Route: /dept/dashboard

**Purpose:** "What do I need to do today?" — simple overview of tasks and evidence status.

**Layout:**
```
PageShell title="Welcome, {first_name}"
  subtitle="{department_name} Department"
[3 KPI Cards]
[2-column: My Pending Tasks | Recent Evidence Status]
[Bottom: Self-Assessment Reminder (conditional)]
```

**KPI Cards (3):**
```
Pending Tasks      N  — link → /dept/tasks
Department Score   NN% — color coded, large
  Green >75% | Amber 50-75% | Red <50%
Evidence Pending   N  — "awaiting review" — link → /dept/evidence
```

**My Pending Tasks (left, major):**
```
Card title: "Your Tasks"
Simple list (not a table):
  Each task:
    [Priority dot] {Task Title}
    Due: {relative date} — red if overdue
    [Start →] → /dept/tasks/:task_id

Sorted: overdue first, then by due_date ASC
Max 5 shown
[View all tasks ({N}) →] → /dept/tasks

Empty: Checkmark icon + "All caught up! No pending tasks."
```

**Recent Evidence Status (right):**
```
Card title: "Evidence Updates"
List of last 5 evidence submissions with status:
  [📄 filename] — [Status badge]
  Approved: green with check
  Rejected: red with reason excerpt "Missing date on..."
  Pending: amber "Awaiting review"

Rejected items have [Re-upload] link → /dept/evidence (pre-filters to that control)
[View all evidence →] → /dept/evidence
```

**Self-Assessment Reminder (conditional):**
```
Shown only when a self-assessment has been assigned and not completed:
Amber banner full width:
  📋 You have a pending self-assessment: "{title}" — Due: {date}
  [Complete Self-Assessment →] → /dept/self-assessment
```

---

### PAGE: My Task List
Route: /dept/tasks

**Layout:**
```
PageShell title="My Tasks"
[Status tabs: All | Pending | In Progress | Completed]
[Filter: Priority | Due Date]
[Task Cards grid — 2 columns]
```

**Task Cards (not a table — cards are friendlier for this role):**
```
Each card:
  ┌──────────────────────────────────────────┐
  │ [Priority badge]          [Due: 3 days]  │
  │                                          │
  │ Control Access Review                    │
  │                                          │
  │ ISO 27001:2022 • A.9 — Access Control   │
  │                                          │
  │ ─────────────────────────────────────── │
  │ [View & Complete →]   Status: In Progress│
  └──────────────────────────────────────────┘

Priority badge: Critical=red, High=orange, Medium=amber, Low=green
Due date: green if >5 days, amber if 2-5 days, red if <2 days or overdue
Status: shown as small text at bottom

Card click / [View & Complete →] → /dept/tasks/:task_id

Empty state (by tab):
  Pending empty: "No pending tasks. Check back later."
  Completed empty: "You haven't completed any tasks yet."
  All empty: "No tasks assigned to you yet."
```

---

### PAGE: Task Wizard
Route: /dept/tasks/:task_id

**Purpose:** Step-by-step guided interface. The compliance jargon is hidden. Plain English throughout. This user should never need to understand what "ISO 27001:2022 Annex A.5.1" means.

**Layout:**
```
No standard PageShell — custom wizard layout:
  [Wizard Header — breadcrumb + task name + status]
  [Step Progress Bar]
  [Step Content Area — centered, max-width 680px]
  [Navigation Footer]
```

**Wizard Header:**
```
[← My Tasks]   Task: {task_title}   [Status badge]
```

**Step Progress Bar:**
```
4 steps, connected:
  ① Understand  ② Evidence  ③ Confirm  ④ Done

Current step highlighted in primary color
Completed steps: green checkmark
Future steps: gray
```

---

**STEP 1: Understand the Task**
```
Card:
  "What you need to do"
  ─────────────────────
  [Plain English description — AI translated on first load]
  
  AI Translation box (highlighted):
    "In plain terms: Your team needs to show that all computers in your department
    require a unique login (username and password) before anyone can use them.
    You should also show that shared accounts like 'admin' have been disabled."
  
  [ℹ️ Show technical details] — collapsible:
    Control ID: ISO-A.9.4.2
    Section: A.9 Access Control
    Full regulatory description from MongoDB

  What evidence do you need?
  ─────────────────────────
  Simple checklist:
    ✓ A screenshot of your login screen showing it requires a password
    ✓ A list of user accounts showing no shared accounts exist
    OR
    ✓ Your IT policy document about passwords
  
  (These are translated from MongoDB evidence_required field via AI)

[Got it, continue →] button — primary
```

**STEP 2: Upload Evidence**
```
Card:
  "Upload your proof"

  FileUpload component (large, centered):
    Accepted types labeled plainly:
      "Screenshots (PNG, JPG), Documents (PDF, Word), Spreadsheets (Excel)"
    Max 10MB

  After file selected:
    File preview (if image/PDF)
    Description field:
      Label: "Briefly describe what this shows (optional)"
      placeholder "e.g. Screenshot of our lab's login screen taken today"

    [AI Check: Will this work?] button — appears after file selected
      → POST /ai/dept/preflight-check { control_requirement, file metadata, preview }
      → Loading: "Checking your file..."
      → Result inline below file:
        PASS:  ✅ "This looks good! This evidence should meet the requirement."
        WARN:  ⚠️ "This might not be enough. {specific issue}. Consider {suggestion}."
               [Upload anyway] [Choose different file]
        FAIL:  ❌ "This won't work because {reason}. You need {what's needed instead}."
               [Choose different file]
    
    On WARN: user can proceed with acknowledgment
    On FAIL: must choose different file (upload button disabled)

Already uploaded evidence for this task:
  Small list below upload area:
    "Previously uploaded for this control:"
    [📄 filename.pdf] — [Status badge] — [Remove]
  Pending or approved count as valid evidence

[Next →] button — disabled until at least 1 file uploaded (or already has approved evidence)
  On click with no file and no evidence: gentle nudge: "Please upload at least one file to continue"
```

**STEP 3: Confirm & Submit**
```
Card:
  "Ready to submit?"

  Summary:
    Task: {task_title}
    What you're submitting: {N} file(s)
    [📄 filename.pdf] — file size

  Self-declaration checkbox:
    ☐ "I confirm that the uploaded evidence accurately represents the current state
       of our department's compliance with this requirement."
    Required to check before submit

  Note to reviewer (optional):
    textarea — "Add a message for the Compliance Officer (optional)"
    placeholder "e.g. This screenshot was taken today on Lab PC 3"

[Submit] button — primary, disabled until checkbox checked
  POST /api/tasks/:task_id/submit (updates task_status + triggers evidence upload if new file)
  PATCH /api/controls/:assignment_id/status { status: "submitted" }
  POST notification to Compliance Officer
  On success: advance to Step 4
```

**STEP 4: Done**
```
Center card:
  ✅ Large green checkmark icon
  "Submitted Successfully!"
  "Your evidence has been sent to the Compliance Officer for review."
  
  "What happens next?"
  • The Compliance Officer will review your submission
  • You'll receive a notification when it's approved or if changes are needed
  • Expected review time: 1–3 business days

  [Back to My Tasks] button → /dept/tasks
  [View Evidence History] → /dept/evidence
```

---

### PAGE: Evidence Vault
Route: /dept/evidence

**Purpose:** History of all evidence this department has submitted. See what's approved, what was rejected and why, re-upload rejected items.

**Layout:**
```
PageShell title="Evidence Vault"
  subtitle="All evidence submitted by {department_name}"
[Status filter tabs]
[Filter row]
[Evidence Table]
```

**Status Filter Tabs:**
```
[All ({N})] [Approved ({N})] [Pending Review ({N})] [Rejected ({N})]
```

**Filter Row:**
```
[Search — by filename or control name]
[Control filter — by control assignment]
[Date range]
```

**Evidence Table:**
```
Columns:
  File | Control | What It Shows | Submitted | Status | Actions

File: [file type icon] filename
Control: plain name (NOT the ISO code — translated name)
  e.g. "Password Policy" not "ISO-A.9.4.2"
  Tooltip shows: "ISO 27001:2022 — A.9.4.2"
What It Shows: description field (truncated)
Status: StatusBadge

Actions per row:
  [View/Download] — signed URL
  [Re-upload] — visible for rejected items:
    Pre-fills the control assignment
    Re-upload opens Upload section on TaskWizard for that task
    or inline file upload if task is already completed

Rejected row expansion (click to expand):
  Red highlight row
  Rejection reason in full: "{reason}" — {reviewer name}
  [Re-upload Evidence] prominent button
```

---

### PAGE: Self Assessment
Route: /dept/self-assessment

**Purpose:** Periodic questionnaire about local department risks and compliance awareness. Submitted to Compliance Officer.

**Layout:**
```
PageShell title="Self Assessment"
  subtitle="Periodic risk and compliance check for {department_name}"
[Active Assessment Card OR Completed State]
```

**Active Assessment (when assigned):**
```
Card header:
  Assessment title (e.g. "Q3 2025 Department Risk Check")
  Due: {date} | Assigned by: {CO name}
  Progress: "5 of 12 questions answered"
  [Progress bar]

Questions (paginated — 1 per page with prev/next):
  Question N of {total}:
  
  [Question text — plain English, no jargon]
  e.g. "Do all computers in your department require a password to log in?"
  
  Response options (radio cards):
    Yes
    No
    Partially (some do, some don't)
    I'm not sure
  
  Notes (optional):
    textarea — "Any additional details? (optional)"
  
  Navigation: [← Previous] [Save & Next →]
  Auto-saves on each Next

Final question → [Submit Assessment] button
  ConfirmModal: "Submit this self-assessment? You won't be able to edit after submission."
  POST /api/self-assessments/:id/submit
  On success: show Submitted state

After submission:
  Green success card:
    ✓ "Self-assessment submitted!"
    "Submitted: {datetime}"
    "The Compliance Officer will review your responses."
  
  Past submission summary (read-only):
    All questions + your answers displayed
    [Download as PDF] option
```

**No Active Assessment:**
```
Centered illustration + text:
  "No assessment assigned"
  "When the Compliance Officer assigns a self-assessment to your department, it will appear here."
  "Estimated next: {if calendar event exists, show it}"
```

**Past Assessments (below active/empty):**
```
Collapsible section: "Previous Assessments"
Table: Assessment name | Submitted | Score/Status | Actions
  [View] → read-only submitted response view
```