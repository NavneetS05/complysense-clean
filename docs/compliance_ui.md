# ComplySense UI Specification
# Document 3 of 7 — Compliance Officer (10 Pages)

Role: Compliance Officer | Route prefix: /compliance
This is the most complex role. Primary daily user. Opens the app every morning.

---

### PAGE: Compliance Dashboard
Route: /compliance/dashboard

**Purpose:** Morning command center. Shows what needs attention today. AI Triage panel is a first-class feature here.

**Layout:**
```
PageShell title="Good morning, {first_name}" subtitle="{today's date}"
[5 KPI Cards]
[2-column: AI Triage Panel | Today's Actions list]
[3-column bottom: Gap Summary | Evidence Queue | Overdue Controls]
```

**KPI Cards (5):**
```
Controls Compliant    XX / YY (fraction + %)   — donut mini-chart
Active Gaps           N  — split: Critical:N High:N Medium:N Low:N
Evidence Pending      N  — link → /compliance/evidence-queue
Tasks Overdue         N  — red if >0, link → /compliance/tasks?status=overdue
Assessments Active    N  — link → /compliance/assessments
```

**AI Triage Panel (left column, major):**
```
Card with header: "AI Priority Triage" [sparkle icon] [Refresh button]
Sub-header: "Top items requiring your attention today"

State: Empty (first load / no triage run)
  [Run AI Triage] button — primary, centered
  "AI will analyze {N} controls, {N} gaps, and {N} tasks to prioritize your day"
  → POST /ai/compliance/triage (sends control statuses, gap list, overdue tasks)
  → Loading: 3 skeleton rows

State: Results loaded
  Numbered list 1–10:
  [1] [Severity badge: CRITICAL] Control ISO-A.5.1 — 3 days overdue, no evidence uploaded
      [Assign Task] [View Control] — inline action buttons
  [2] [HIGH] Gap: Access control policy missing — DPDP Section 8
      [Create Task] [View Gap]
  ...

Last refreshed: "2 minutes ago" timestamp
[Refresh] re-runs triage
```

Data source for triage input: GET /api/compliance/triage-context (assembled by main app, sanitized before sending to AI)

**Today's Actions list (right column):**
```
Card title: "Your Actions Today"
Simple checklist style:
  □ Review 3 pending evidence submissions
  □ Complete ISO 27001 assessment (47% done)
  □ Assign tasks for 2 new gaps
  □ Follow up on 5 overdue controls

Each item is a clickable link → relevant page
Checked items move to bottom with strikethrough
Items generated from actual DB data, not AI
```

**Gap Summary (bottom left):**
```
Compact bar chart (recharts BarChart horizontal):
X-axis: severity (Critical, High, Medium, Low)
Y-axis: count
Colors match severity palette
Click bar → /compliance/gaps?severity=critical
```

**Evidence Queue (bottom center):**
```
Compact list of 5 most recent pending evidence submissions:
  [Dept] | [Control] | Submitted by | Time ago | [Review →]
[View all pending ({N})] → /compliance/evidence-queue
```

**Overdue Controls (bottom right):**
```
Compact list: 5 most overdue controls (sorted by due_date ASC)
  [Control ID] | [Framework badge] | [Days overdue in red]
[View all overdue] → /compliance/controls?status=overdue
```

---

### PAGE: Control Task Manager (Kanban)
Route: /compliance/controls

**Purpose:** Primary operational workspace. Every control assignment shown as a card in a Kanban board.

**Layout:**
```
PageShell title="Controls" 
  actions=[+ Assign Control | Export]
[Filter bar]
[Kanban board — 5 columns, horizontally scrollable]
```

**Filter Bar:**
```
[Search — placeholder "Search control ID or title"]
[Framework — dropdown: All | DPDP Act 2023 | ISO 27001:2022 | NIST CSF 2.0 | CERT-In 2022 | UGC Guidelines | NAAC Criteria 4 & 6]
[Department — dropdown: All | {institution depts}]
[Assigned To — dropdown: All | {institution users}]
[Due — dropdown: All | Overdue | Due This Week | Due This Month]
[Clear Filters — ghost button, visible only when any filter active]
```

**Kanban Columns (5):**
```
Not Started   (not_started)   — gray header
In Progress   (in_progress)   — blue header
Submitted     (submitted)     — purple header
Compliant     (compliant)     — green header
Non-Compliant (non_compliant) — red header

Each column header shows: Column title + card count badge
Column body: scrollable list of cards
Column max height: viewport height minus header/filters, overflow-y-auto
```

**Kanban Card:**
```
Card (white surface, 1px border, 8px radius, shadow-sm):
  Top: Framework badge (color-coded) + [⋯ kebab menu]
  Control ID: monospace, slate-500, small
  Title: 2-line truncated, semibold
  Assigned to: [Avatar 20px] + name, small
  Due date: relative ("3 days left" green / "Overdue by 2 days" red)
  Bottom row: Evidence status dot + department chip

Kebab menu on card:
  View Detail → /compliance/controls/:assignment_id
  Edit Assignment → opens Edit modal
  Add Note → opens inline note input
  Mark as NA → ConfirmModal → updates status

Framework badge colors:
  DPDP Act 2023     → violet
  ISO 27001:2022    → blue
  NIST CSF 2.0      → cyan
  CERT-In 2022      → red
  UGC Guidelines    → emerald
  NAAC Criteria 4&6 → amber
```

**Drag and Drop:**
```
Built with @dnd-kit/core
Dragging card to another column:
  1. Optimistic update: card moves immediately
  2. PATCH /api/controls/:assignment_id/status { status: new_column_key }
  3. Success: toast "Status updated to {new status}"
  4. Failure: card snaps back, toast error
  5. Audit log written on backend
  6. Notification created for assigned_to user
```

**+ Assign Control Modal:**
```
Title: "Assign Control"
Fields:
  Control*        Searchable select from MongoDB control library
                  (searches by control_id or title across all frameworks)
                  Option display: "[ISO-A.5.1] Policies for information security"
  Framework*      Auto-filled from selected control (read-only)
  Assign To*      Searchable select of institution users
  Department      Select (optional)
  Due Date*       Date picker
  Notes           textarea (optional)

[Cancel] [Assign Control]
POST /api/controls
On success: new card appears in "Not Started" column, toast, notification to assigned user
```

---

### PAGE: Control Detail
Route: /compliance/controls/:assignment_id

**Purpose:** Full view of one control — its regulatory definition, assignment state, evidence, and history.

**Layout:**
```
PageShell
  title={control_title}
  breadcrumbs=[Controls → {control_id}]
  actions=[Edit Assignment | Add Note | Mark NA]

[2-column: Left 60% — Detail + Evidence | Right 40% — Activity & Notes]
```

**Left Column:**

**Control Info Card:**
```
Control ID:   ISO-A.5.1 (monospace)
Framework:    ISO 27001:2022 (badge)
Section:      A.5 Organizational Controls
Title:        Policies for information security
Description:  Full description text from MongoDB
Evidence Required: bullet list from MongoDB control library
  • Approved policy document
  • Distribution records showing staff acknowledgment
  • Review schedule

Status:       [StatusBadge]
Assigned To:  [Avatar] Full Name
Department:   Department Name
Due Date:     Date + "X days remaining" or "Overdue by X days"
Assigned By:  Full Name
```

**Evidence for This Control:**
```
Section title: "Evidence Documents"
[Upload Evidence button] — opens FileUpload component
  Accepted: PDF, PNG, JPG, XLSX, DOCX up to 10MB
  Upload → POST /api/evidence with assignment_id, control_id
  On success: new row in evidence table below

Evidence Table:
  Columns: File Name | Uploaded By | Date | Status | Actions
  Status badge: pending / approved / rejected
  Actions:
    [Download] — GET signed URL → open in new tab
    [Remove] — only if status=pending and uploaded_by = current_user
      ConfirmModal: "Remove this evidence?"
      DELETE /api/evidence/:evidence_id
```

**Right Column:**

**Assignment Notes:**
```
Card title: "Notes"
Existing notes: [Avatar] [Note text] [Timestamp] — most recent first
  (notes stored in control_assignments.notes as append-only text — JSON array of {author, text, timestamp})

Add note input:
  Textarea (3 rows, auto-expands)
  [Add Note] button
  PATCH /api/controls/:assignment_id/notes { note: text }
  On success: note appears at top of list
```

**Activity Timeline:**
```
Card title: "Activity"
Timeline of audit_log entries for this entity:
  Vertical line with dots
  [Icon] Action description | User name | Timestamp
  E.g.: ↑ Status changed to "In Progress" | Priya Sharma | 2 hours ago
  E.g.: 📎 Evidence uploaded | Rahul Meena | Yesterday
  E.g.: 💬 Note added | Priya Sharma | 3 days ago
```

---

### PAGE: Gap Assessment Matrix
Route: /compliance/gaps

**Purpose:** Visual overview of all compliance gaps. Drill down to assign mitigation tasks.

**Layout:**
```
PageShell title="Compliance Gaps"
  actions=[Export Gaps PDF]
[Filter bar]
[Summary cards row]
[Gap Matrix grid]
[Gap Detail Drawer — slides in from right on row click]
```

**Filter Bar:**
```
[Framework filter]  [Severity filter]  [Status filter (open/in_progress/resolved/accepted)]
[Department filter]  [Assessment filter — select which assessment]
[Search — by gap title or control_id]
```

**Summary Cards (4):**
```
Critical  — N   (red)
High      — N   (orange)
Medium    — N   (amber)
Low       — N   (green)
```

**Gap Matrix:**
```
DataTable with columns:
  Severity badge | Framework badge | Control ID | Gap Title | Status | Department | Created | Actions

Sorted default: severity DESC (critical first), then created DESC
Row click: opens Gap Detail Drawer (right side Sheet, 480px)
Actions column:
  [Create Task] — opens Create Mitigation Task modal
  [Mark Resolved] — ConfirmModal → PATCH /api/gaps/:gap_id { remediation_status: "resolved" }
  [Accept Risk] — ConfirmModal with reason text field → PATCH { remediation_status: "accepted_risk" }
```

**Gap Detail Drawer (Sheet, right side):**
```
Header: Gap title + [X close]
Body:
  Severity: badge
  Framework: badge
  Control ID: monospace link → /compliance/controls/:assignment_id
  Description: full text
  Remediation Status: badge
  Created: date
  Assessment: link to assessment

  Mitigation Tasks section:
    List of existing mitigation_tasks linked to this gap
    [+ Create Task] button → opens Create Task modal

  [Close] footer button
```

**Create Mitigation Task Modal:**
```
Title: "Create Mitigation Task"
Pre-filled from gap context (gap_id, institution_id)
Fields:
  Task Title*      text input (pre-filled: "Remediate: {gap_title}")
  Description      textarea
  Assign To*       searchable user select
  Department       select
  Priority*        Select: Critical | High | Medium | Low
  Due Date*        date picker

[Cancel] [Create Task]
POST /api/tasks { gap_id, task_title, task_description, assigned_to, department_id, priority, due_date }
On success: task appears in tasks list, notification sent to assigned user
```

---

### PAGE: Evidence Verification Queue
Route: /compliance/evidence-queue

**Purpose:** Compliance Officer's daily inbox for approving or rejecting evidence submitted by department reviewers and IT security.

**Layout:**
```
PageShell title="Evidence Queue"
  subtitle="{N} pending submissions"
[Bulk Action Bar — appears when rows selected]
[Filter bar]
[Evidence Queue Table]
```

**Filter Bar:**
```
[Status tabs: Pending (N) | Approved | Rejected | All]
[Framework filter]  [Department filter]  [Date range]
[Search — by filename or control]
```

**Evidence Queue Table:**
```
Columns:
  □ | File Name | Control | Framework | Department | Submitted By | Submitted At | Size | Status | Actions

Row click → opens Evidence Review Drawer

Actions per row (Pending only):
  [Approve] → ConfirmModal → PATCH /api/evidence/:id { approval_status: "approved", approved_by: current_user }
  [Reject] → opens Reject Reason Modal

Bulk actions (when rows selected, pending only):
  [Approve Selected]  [Reject Selected → Bulk Reject Modal]
```

**Evidence Review Drawer (Sheet, right side, 520px):**
```
Header: filename + [Approve] [Reject] action buttons
Body:
  Control: [ID] [Title] (link → control detail)
  Framework: badge
  Department: name
  Submitted by: name + email
  Submitted at: full datetime
  File size: formatted
  Description: text from uploader (if any)

  [Preview area]:
    PDF: embedded iframe preview
    Image: img tag with max-height
    Other: download prompt

  Previous evidence for this control:
    Small list of older evidence with statuses
    "This is the Nth submission for this control"
    Previous rejections shown with their reasons — gives context
```

**Reject Reason Modal:**
```
Title: "Reject Evidence"
Filename shown at top
Fields:
  Rejection Reason*   textarea — min 20 chars, required
  "Be specific so the uploader knows what to fix and re-submit"

[Cancel] [Reject Evidence]
PATCH /api/evidence/:id { approval_status: "rejected", rejection_reason: text }
On success: notification sent to uploader, control status recalculated, toast
```

---

### PAGE: Assessment List
Route: /compliance/assessments

**Layout:**
```
PageShell title="Assessments"
  actions=[+ Start New Assessment]
[Assessments Table]
```

**Assessments Table:**
```
Columns:
  Assessment Name | Framework | Status badge | Started By | Started At | Completed At | Actions

Actions:
  [Continue] — if status=in_progress → /compliance/assessments/:id
  [View Results] — if status=completed → /compliance/assessments/:id
  [Archive] — ConfirmModal → PATCH status=archived
  Draft assessments: [Delete] ConfirmModal

Status: draft | in_progress | completed | archived
Filter: by framework, by status
Sort: started_at DESC default
```

**Start New Assessment Modal:**
```
Title: "Start New Assessment"
Fields:
  Assessment Name*   text input (default: "{Framework} Assessment — {Month Year}")
  Framework*         Select: DPDP Act 2023 | ISO 27001:2022 | NIST CSF 2.0 | CERT-In 2022 | UGC Guidelines | NAAC Criteria 4 & 6

[Cancel] [Start Assessment]
POST /api/assessments { assessment_name, framework_name }
On success: redirect to /compliance/assessments/:new_id immediately
```

---

### PAGE: Assessment Runner
Route: /compliance/assessments/:assessment_id

**Purpose:** Paginated wizard — one control question per screen. Answers write to assessment_responses. Final submit computes compliance_results and compliance_gaps.

**Layout:**
```
Full-screen modal-like experience within DashboardLayout
PageShell removed. Custom layout:
  [Progress Header — full width, fixed top]
  [Question Panel — centered, max-width 720px]
  [Navigation Footer — fixed bottom]
```

**Progress Header:**
```
Left: Assessment name + Framework badge
Center: "Question 12 of 47" + progress bar (filled segment = completed/total)
Right: [Save Draft] button + [Exit] button
  Exit → ConfirmModal: "Your progress has been saved. You can continue later."
  → /compliance/assessments (list)
```

**Question Panel (one at a time):**
```
Card (white, centered, padding 32px):
  Control reference:
    [Framework badge] [Control ID in monospace]
    Section: A.5 — Organizational Controls

  Question (bold, 18px):
    "Does your institution have documented information security policies
    that are approved by management?"

  Response options (Radio group — large clickable cards):
    ┌────────────────────────────────────────┐
    │ ✓ Yes — Fully implemented              │
    └────────────────────────────────────────┘
    ┌────────────────────────────────────────┐
    │ ~ Partial — In progress or incomplete  │
    └────────────────────────────────────────┘
    ┌────────────────────────────────────────┐
    │ ✗ No — Not implemented                 │
    └────────────────────────────────────────┘
    ┌────────────────────────────────────────┐
    │ — Not Applicable                       │
    └────────────────────────────────────────┘

  Selected option: primary color border + background tint

  Evidence Note (optional):
    Label: "Supporting notes or evidence reference (optional)"
    Textarea — 3 rows, max 500 chars
    "Describe what evidence you have for this response"

  Previous answer indicator (if returning to already-answered question):
    Amber banner: "You previously answered: Partial"
    Current selection can be changed
```

**Navigation Footer (fixed bottom):**
```
Left: [← Previous] — ghost button, disabled on question 1
Center: "Saved automatically" + last save timestamp (auto-saves on selection)
Right: [Next →] — primary button
  On last question: button label changes to [Submit Assessment]
  Submit → ConfirmModal: "Submit this assessment? This will calculate compliance results and generate gaps. You cannot change answers after submission."
  → POST /api/assessments/:id/submit
  → Loading overlay: "Calculating compliance scores..."
  → On complete: redirect to assessment results view
```

**Auto-save behavior:**
```
On every response selection:
  PATCH /api/assessments/:assessment_id/responses
  body: { question_id, control_id, response_value, score_value }
  Silent (no toast) — just updates "Saved automatically" timestamp
```

**Assessment Results View (same route, status=completed):**
```
Layout changes to results display:
  Large score: "72% Compliant" with gauge chart
  Framework compliance breakdown bars
  Gaps identified: count by severity
  [View Gaps →] → /compliance/gaps?assessment_id=
  [Generate Report] → opens report generation
  [View Controls →] → /compliance/controls
```

---

### PAGE: Policy Manager
Route: /compliance/policies

**Purpose:** List all policies. Create new ones. Track approval status. Edit existing ones.

**Layout:**
```
PageShell title="Policies"
  actions=[+ New Policy]
[Filter bar]
[Policies Table]
```

**Filter Bar:**
```
[Search — by policy name]
[Status filter: All | Draft | Pending Approval | Approved | Rejected | Superseded]
[Framework filter]
[Sort: Newest first | Oldest first | Recently updated]
```

**Policies Table:**
```
Columns:
  Policy Name | Version | Framework | Status | Created By | Last Updated | Sent To (approver) | Actions

Version: shown as "v{version_number}" — monospace
Status badge: per status colors
Sent To: approver name if submitted, "—" if draft

Actions per row:
  [Edit] → /compliance/policies/:policy_id/edit — available for draft and rejected only
  [View] → /compliance/policies/:policy_id/view — all statuses
  [Submit for Approval] → opens Submit modal (draft status only)
  [New Version] → creates new policy with parent_policy_id = current (approved/rejected)
  [Delete] → ConfirmModal (draft only)

Row click → /compliance/policies/:policy_id/edit (if draft/rejected) or /view (if others)
```

**+ New Policy → /compliance/policies/new:**
See Policy Editor page below.

---

### PAGE: Policy Editor
Route: /compliance/policies/new | /compliance/policies/:policy_id/edit

**Purpose:** Hybrid editor — manual writing + AI copilot. Policies saved to MongoDB (content) and PostgreSQL (metadata). Like Databricks notebooks — always listed, always editable, auto-saved.

**Layout:**
```
Custom layout (not PageShell — full width editor):
  [Editor Topbar — fixed]
  [2-column: Left 58% Editor | Right 42% AI Copilot Panel]
```

**Editor Topbar:**
```
Left: 
  [← Back to Policies]
  Policy Name input (inline editable, large, placeholder "Untitled Policy")
  Version badge: v1 | v2 (incremented on new version)
  Status badge

Right:
  Last saved: "Saved 30s ago" / "Saving..." / "⚠ Unsaved changes"
  [Save Draft] — PATCH /api/policies/:id (saves to MongoDB + PostgreSQL)
  [Submit for Approval] — opens Submit modal (only visible when status=draft or rejected)
```

**Left Panel — Rich Text Editor (Tiptap):**
```
Toolbar (sticky below editor topbar):
  Bold | Italic | Underline | H1 | H2 | H3 | Bullet List | Numbered List |
  Table | Horizontal Rule | [AI: Improve selection] | [AI: Continue writing]

Editor area:
  White background, comfortable padding (32px)
  Placeholder: "Start writing your policy, or use the AI Copilot →"
  Tiptap editor — supports all standard rich text
  Min-height: viewport height - topbar - toolbar
  AI-generated content: highlighted with a subtle light-blue left border
    (marks which sections were AI-generated vs manually written)
    Accepted AI content: border fades after user edits it

Auto-save: every 30 seconds silently
  PUT /api/policies/:id/content { content_json: editor.getJSON() }
  (content_json is Tiptap JSON format stored in MongoDB)
```

**Right Panel — AI Copilot:**
```
Panel header: "AI Copilot" [sparkle icon]
Tab bar: [Generate] [Validate]

─── GENERATE TAB ───

Step 1: Policy Wizard (always shown first for new policies)
  "What type of policy are you creating?"
  Option cards (click to select):
    Data Protection Policy
    Access Control Policy
    Incident Response Policy
    Data Retention Policy
    Acceptable Use Policy
    Vendor Management Policy

  After type selected, wizard questions appear:
  (Questions are structured — see policy_wizard.py)

  For Data Protection Policy example:
    Q: What data types does this policy cover?
    [Multi-select chips]: Student PII | Research Data | Financial Records | Health Records | Staff Data | Third-Party Data

    Q: Should this include consent management?
    [Option cards]: Yes - explicit | Yes - implied | No - legitimate interest

    Q: Default retention period?
    [Options]: 1 year | 3 years | 5 years | 7 years | [Custom input]

    Q: Additional clauses?
    [Multi-select]: Right to erasure | Data portability | Consent withdrawal | Breach procedure | Third-party obligations

    Q: Any other requirements? (free text)
    [Textarea with placeholder "Optional — describe any specific requirements"]
    Character limit: 500

  [Generate Policy] button — primary, full width
    → POST /ai/compliance/generate-policy { wizard_answers }
    → Loading state: Panel shows:
      "Generating your {type}..."
      Progress indicators (4 steps):
        ✓ Analyzing regulatory requirements
        ✓ Structuring policy sections
        ⟳ Writing policy content...
        ○ Final review
    
    → If compliance flags found (non-compliant wizard answers):
      ⚠ Compliance Flags panel appears BEFORE generating:
      ┌─────────────────────────────────────────────────┐
      │ ⚠ Compliance Issues Found                       │
      │                                                 │
      │ 1. Retention period of 1 year may conflict with │
      │    DPDP Act 2023 Section 8 (financial records   │
      │    require minimum 5 years per UGC guidelines). │
      │    Suggested: 5 years for financial records.    │
      │                                                 │
      │ [Review & Fix] [Proceed Anyway]                 │
      └─────────────────────────────────────────────────┘
      Review & Fix: highlights the problematic question
      Proceed Anyway: generates with a warning flag in output

    → On generation complete:
      Sections appear one by one in the editor (streaming effect):
      1. Purpose
      2. Scope
      3. Definitions
      4. Policy Statements
      5. Roles and Responsibilities
      6. Enforcement
      7. Review and Update
      
      Each section: AI adds to editor with blue left border
      Toast: "Policy generated. Review and edit as needed."

  [Regenerate] button (after generation) — replaces existing content with ConfirmModal first

─── VALIDATE TAB ───

Used to validate an existing policy (typed or uploaded) against frameworks.

Input options:
  [Validate Current Document] — uses editor content
  [Upload Policy PDF] — FileUpload component (PDF only, max 20MB)
    → POST /api/policies/extract-pdf { file } (uses pdfplumber)
    → Extracted text shown in preview area (read-only)
  
Framework selection:
  "Validate against:"
  [Checkboxes]: DPDP Act 2023 | ISO 27001:2022 | NIST CSF 2.0 | CERT-In 2022 | UGC Guidelines | NAAC Criteria 4&6
  Default: all checked

[Run Validation] button
  → POST /ai/compliance/validate-policy { policy_text, frameworks }
  → Loading: "Validating against selected frameworks..."

Result display:
  Tabs: [Gaps ({N})] [Conflicts ({N})] [Improvements ({N})] [Compliant ✓]
  
  Gaps tab:
    Each gap: [Framework badge] [Section ref] Description
    Red left border
  
  Conflicts tab:
    Each conflict: [Framework badge] What conflicts + Suggested fix
    Red left border, bold
  
  Improvements tab:
    Each item: [Framework badge] Suggestion
    Amber left border
  
  Compliant tab:
    Green summary of what the policy gets right

  Bottom: [Overall: Partially Compliant] verdict badge
```

**Submit for Approval Modal:**
```
Title: "Submit Policy for Approval"
Content:
  Policy name (read-only)
  "Select a Policy Approver to send this to:"
  Searchable select of users with role = Policy Approver
  Note to approver: textarea (optional)

[Cancel] [Submit for Approval]
PATCH /api/policies/:id { policy_status: "pending_approval", submitted_to: approver_id }
On success: toast "Policy submitted to {approver name}", notification sent to approver, redirect to /compliance/policies
```

---

### PAGE: Mitigation Task Manager
Route: /compliance/tasks

**Purpose:** All mitigation tasks across all departments. Filter and manage.

**Layout:**
```
PageShell title="Mitigation Tasks"
  actions=[+ Create Task]
[Summary tabs]
[Filter bar]
[Tasks Table]
```

**Summary Tabs:**
```
[All ({N})] [Open ({N})] [In Progress ({N})] [Overdue ({N})] [Completed ({N})]
Active tab filters the table
```

**Filter Bar:**
```
[Search by task title]
[Priority: All | Critical | High | Medium | Low]
[Department: All | {depts}]
[Assigned To: All | {users}]
[Due: All | Overdue | Due Today | Due This Week]
```

**Tasks Table:**
```
Columns:
  Priority badge | Task Title | Linked Gap | Department | Assigned To | Due Date | Status | Actions

Task Title: truncated to 1 line, row click → opens Task Detail Drawer
Linked Gap: gap title truncated, link to gap
Due Date: relative + absolute ("3 days · Jan 15") — red if overdue
Priority badge: Critical=red, High=orange, Medium=amber, Low=green

Actions per row:
  [Edit] → Edit Task Modal
  [Complete] → ConfirmModal → PATCH status=completed, completed_at=now
  [Cancel] → ConfirmModal with reason
```

**Task Detail Drawer (Sheet right):**
```
Header: Task title + [Edit] [Complete]
Full details:
  Priority | Status | Due Date
  Linked Gap → gap detail
  Linked Control → control detail
  Description: full text
  Assigned To: avatar + name
  Department: name
  Created By: name + date
  Completed At: date or "—"
```

**Create/Edit Task Modal:**
```
Fields: Task Title* | Description | Assign To* | Department | Priority* | Due Date* | Linked Gap (optional)
POST /api/tasks (create) | PATCH /api/tasks/:id (edit)
```

---

### PAGE: Notifications
Route: /compliance/notifications

Shared component spec — see Doc 1, Section 13.
Compliance Officer sees all 7 notification types.

---

### PAGE: Control Detail
Route: /compliance/controls/:assignment_id
Fully specced above (see Control Detail section).