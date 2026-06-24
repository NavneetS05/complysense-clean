# ComplySense UI Specification
# Document 6 of 7 — Vendor Reviewer, Policy Approver, Read-Only Assessor

---

## VENDOR REVIEWER PAGES

Role: Vendor Reviewer | Route prefix: /vendor
Manages third-party risk. Primary regulatory concern is DPDP Act 2023 data processor obligations.
Daily work: onboard new vendors, review contracts, monitor expiries.

---

### PAGE: Vendor Risk Register
Route: /vendor/dashboard

**Purpose:** Central command for all vendors. Risk posture at a glance. Expiry alerts prominent.

**Layout:**
```
PageShell title="Vendor Risk Register"
  actions=[+ Onboard Vendor]
[Expiry Alert Banner — conditional]
[4 KPI Cards]
[Filter bar]
[Vendor Table]
```

**Expiry Alert Banner:**
```
Shown when any vendor has contract_expiry_date within 30 days:
Amber banner:
  ⚠ {N} vendor contracts expiring within 30 days. Review and renew before expiry.
  [View Expiring →] → /vendor/expiry
Dismissable per session.
```

**KPI Cards (4):**
```
Total Vendors         N  — all active vendors
Critical Risk         N  — red if any
High Risk             N  — orange
DPA Missing           N  — vendors with dpa_available=false — link opens table filtered
```

**Filter Bar:**
```
[Search — by vendor name or product name]
[Risk Level: All | Critical | High | Medium | Low | Not Assessed]
[Category: All | Cloud | EdTech | ERP | Security | Communication | Other]
[DPA: All | Available | Not Available]
[Data Location: All | India | US | EU | Other]
```

**Vendor Table:**
```
Columns:
  Vendor Name | Product | Category | Risk Level | DPA | Data Location | Contract Expiry | Actions

Vendor Name: bold, row click → /vendor/vendors/:vendor_id
Risk Level: colored badge. "Not Assessed" = gray
DPA: ✓ green / ✗ red
Data Location: badge — India=green, US/EU=amber, Other=red (DPDP concern)
Contract Expiry:
  >60 days: date in gray
  30-60 days: date in amber
  <30 days: date in red with warning icon ⚠
  Expired: "EXPIRED" red badge

Actions per row:
  [Assess] → /vendor/vendors/:vendor_id (scrolls to assessment section)
  [Edit] → opens Edit Vendor modal
  [Delete] → ConfirmModal (only if no risk assessments linked)

Bulk: select multiple → [Export selected to CSV]
Pagination: 20 per page
Empty: Store icon + "No vendors registered yet." [+ Onboard Vendor]
```

---

### PAGE: Onboard Vendor
Route: /vendor/vendors/new

**Purpose:** Register a new third-party vendor and capture DPDP-relevant information.

**Layout:**
```
PageShell
  title="Onboard New Vendor"
  breadcrumbs=[Vendor Register → New Vendor]
[2-column form card]
```

**Form Card:**
```
Section 1: Vendor Information
  Vendor Name*          text input
  Product / Service*    text input (what the university uses them for)
  Category*             Select: Cloud | EdTech | ERP | Security | Communication | Other
  Contact Email         email input

Section 2: Data & Privacy (DPDP relevance)
  Data Processing Location*
    Select: India | United States | European Union | Multiple Locations | Other
    Helper text: "Where will this vendor process or store data about individuals?"
  
  Data Processing Agreement (DPA) Available?
    Toggle Switch (ON/OFF)
    When OFF: amber note "A DPA is required under DPDP Act 2023 for data processors"
  
  Model Training Allowed?
    Toggle Switch
    Helper text: "Does the vendor's terms allow them to train AI models on your data?"
    When ON: amber note "Verify this is acceptable under your data protection policy"

Section 3: Contract
  Contract Expiry Date   date picker
  
  Upload Contract / SOC2 (optional — can do later in assessment workspace):
    FileUpload: PDF only, max 25MB
    "Upload now to run AI analysis, or upload later from the vendor detail page"

Form footer:
  [Cancel] [Save — Onboard Vendor]
  
  POST /api/vendors { all fields }
  On success:
    If contract uploaded: redirect to /vendor/vendors/:new_id (analysis runs automatically)
    If no contract: redirect to /vendor/dashboard, toast "Vendor onboarded. Add contract for AI analysis."
```

---

### PAGE: Assessment Workspace
Route: /vendor/vendors/:vendor_id

**Purpose:** Full vendor profile. Run and view risk assessments. AI contract analysis.

**Layout:**
```
PageShell
  title={vendor_name}
  subtitle={product_name} | {category badge}
  breadcrumbs=[Vendor Register → {name}]
  actions=[Edit Vendor | Delete Vendor]

[Vendor Info Card + Risk Summary — top section]
[Tabs: Risk Assessments | Contract Analysis | History]
```

**Vendor Info Card:**
```
2-column grid of info chips:
  Data Location:       [badge — color coded]
  DPA Available:       [✓ Yes / ✗ No]
  Model Training:      [Allowed / Not Allowed]
  Contract Expiry:     [date + days remaining, color coded]
  Contact:             email link
  Onboarded by:        name + date
  Category:            badge
```

**Risk Summary Bar:**
```
Current Risk Level:
  [Large badge: CRITICAL / HIGH / MEDIUM / LOW / NOT ASSESSED]
  If assessed: "Last assessed: {relative date} by {name}"
  If not assessed: "No formal assessment completed yet"

[+ Run New Assessment] button — opens assessment form below (or scrolls to tab)
```

---

**TAB: Risk Assessments**
```
New Assessment Form Card (always visible at top of tab):
  Card title: "Conduct Risk Assessment"
  Fields:
    Risk Level*       Select: Critical | High | Medium | Low
    Assessment Summary*  textarea 5 rows
      placeholder "Summarize the vendor's compliance posture, key risks identified, and basis for risk rating"
    Recommendations      textarea 3 rows
    DPDP Compliant?   Toggle (Yes/No)
  
  [Save Assessment] — primary button
  POST /api/vendors/:vendor_id/risk-assessments { risk_level, assessment_summary, recommendations, dpdp_compliant }
  On success: new entry in history list below, risk summary bar updates
  If new risk is Critical or High → notification sent to Compliance Officer

Assessment History list:
  Each assessment card (collapsible, newest first):
    Risk Level badge | Assessed by | Date
    Summary: (truncated 3 lines) [Read more]
    DPDP Compliant: Yes/No
    Recommendations: text
    [Expand/Collapse ▾]
```

**TAB: Contract Analysis**
```
Upload Section:
  Card title: "Contract / SOC2 Analysis"
  FileUpload: PDF only, max 25MB
  "Upload vendor contract, SOC 2 report, or DPA for AI analysis"
  
  Uploaded files list (if any):
    [📄 filename.pdf] — {date uploaded} — [Replace] [Download]
  
  [Analyze with AI] button (active when file uploaded):
    → POST /ai/vendor/analyze-contract { extracted text from PDF }
    → Loading: "Extracting document content... Analyzing DPDP compliance... Checking ISO 27001 supplier controls..."
    → Shows progress steps (each ~3-5 seconds)
    
  AI Analysis Result (shown after analysis completes, persisted):
    Card with "AI Analysis" badge (sparkle icon)
    "Analyzed: {filename} on {date}"
    
    DPDP Act 2023 Compliance Gaps:
      [List with red left border]
      e.g. "Missing: Breach notification timeline clause (Section 8 requires 72-hour notification)"
    
    ISO 27001:2022 Supplier Control Gaps:
      [List with amber left border]
      e.g. "Annex A.5.19 — No right-to-audit clause found in contract"
    
    Overall Risk: [badge: HIGH]
    
    Top 3 Recommendations:
      1. Request DPA addendum including breach notification obligations
      2. Add data localization clause restricting processing to India
      3. Obtain written confirmation that model training is prohibited
    
    [Regenerate Analysis] ghost button (re-runs with same file)
    [Export as PDF] — downloads analysis as PDF document
```

**TAB: History**
```
Audit log for this vendor:
  Timeline view of all actions:
    Vendor created | Assessed | Contract uploaded | Risk level changed | Edited
  [Actor] [Action] [Date]
```

---

### PAGE: Expiry Tracker
Route: /vendor/expiry

**Purpose:** Proactive view of expiring contracts and certifications. Prevents accidental lapse.

**Layout:**
```
PageShell title="Expiry Tracker"
[View toggle: Calendar | List]
[Filter: All | Expiring This Month | Expiring in 60 Days | Expired]
```

**Calendar View:**
```
Month calendar grid
Event dots on dates with expirations
Color: red if expired, amber if expiring soon, green if >60 days
Click date → popover showing:
  [Vendor name] — [Product] — [Expiry type: Contract/Cert]
  [View Vendor →] link
```

**List View:**
```
Grouped by time bucket:
  ─── Expired ───────────────────────────────
  [Vendor] [Product] [Expired: {N} days ago]  [EXPIRED badge]  [View]

  ─── Expiring This Week ─────────────────────
  [Vendor] [Product] [Expires: {date}]  [3 DAYS badge red]  [View]

  ─── Expiring This Month ────────────────────
  [Vendor] [Product] [Expires: {date}]  [18 DAYS badge amber]  [View]

  ─── Expiring in 60 Days ────────────────────
  [Vendor] [Product] [Expires: {date}]  [45 DAYS badge]  [View]

[View] → /vendor/vendors/:vendor_id

Empty state per group: "None in this period"
```

---

## POLICY APPROVER PAGES

Role: Policy Approver | Route prefix: /policy
Event-driven role. Logs in when a notification arrives. Must review policies quickly.
The Diff Viewer is the most critical UI element here.

---

### PAGE: Policy Inbox
Route: /policy/inbox

**Purpose:** Policies awaiting sign-off. Notification badge drives login. Designed to process quickly.

**Layout:**
```
PageShell title="Policy Inbox"
  subtitle="{N} policies pending your approval"
[Pending Policies List]
```

**Pending Policies List:**
```
Not a table — card list for readability:

Each policy card:
  ┌──────────────────────────────────────────────────────────┐
  │ [NEW badge if <24h]    Data Protection Policy    v2      │
  │ Framework: DPDP Act 2023                                  │
  │ Submitted by: Priya Sharma (Compliance Officer)           │
  │ Submitted: Aug 12, 2025 at 2:30 PM (3 hours ago)         │
  │ Note from submitter: "Updated to include new consent..."  │
  │                                                          │
  │ [Review & Decide →]   [Quick View ▾]                     │
  └──────────────────────────────────────────────────────────┘

[NEW] badge: shown if submitted_at within 24 hours
[Review & Decide →] → /policy/:policy_id/review
[Quick View ▾] → expands policy text inline (first 300 chars + "Read more")

Empty state:
  Inbox zero illustration (green check envelope)
  "No policies pending approval"
  "You'll receive a notification when a policy needs your review."
```

---

### PAGE: Policy Review
Route: /policy/:policy_id/review

**Purpose:** Read the policy, compare to previous version, see AI conflict summary, approve or reject. Must be achievable in under 5 minutes.

**Layout:**
```
Custom layout — full-width editor view:
  [Review Header Bar — sticky top]
  [2-column: Left 50% Previous Version | Right 50% Current Version]
  [AI Analysis Card — below diff, collapsible]
  [Decision Panel — sticky bottom]
```

**Review Header Bar:**
```
Left: Policy name | [v{N} badge] | [Framework badge] | [pending_approval badge]
Center: Submitted by {name} on {date}
Right: [Approve ✓] [Reject ✗] — both visible always (not just at bottom)
```

**2-Column Diff Viewer:**
```
When version_number > 1 (has a parent_policy_id):
  Left column:
    Header: "Previous Version (v{N-1})" in gray
    Background: slightly warm off-white (#FFFBF0)
    Content: policy_content from parent_policy_id row in PostgreSQL / MongoDB
    
  Right column:
    Header: "Current Version (v{N})" in blue
    Background: white
    Content: current policy_content

  Diff highlighting (computed client-side using diff library):
    Added lines in right: light green background (#F0FDF4), green left border
    Removed lines in left: light red background (#FEF2F2), red left border, strikethrough
    Changed lines: yellow highlight
    Unchanged: normal

  Both columns scroll in sync (synchronized scroll)

When version_number = 1 (first version, no parent):
  Left column shows:
    Gray card: "This is the first version of this policy"
    "There is no previous version to compare."
  Right column shows full policy text

Policy text rendering:
  Rendered from Tiptap JSON (fetched from MongoDB)
  Full rich text formatting preserved
  Read-only (no editing for Policy Approver)
  Comfortable reading typography (15px, 1.7 line height)
```

**AI Analysis Card (collapsible, between diff and decision panel):**
```
Header: "AI Conflict Analysis" [sparkle icon]  [Run Analysis / Regenerate] button  [▼ collapse]

Default state: not run yet
  Gray card with [Run AI Analysis] button
  "Check this policy against existing policies and regulations"
  
Running state (first click):
  → POST /ai/policy/conflict-detect { new_policy_text, existing_policies_summary }
  → Skeleton loading, "Analyzing for conflicts..."

Result state:
  Executive Summary section:
    1-paragraph summary of what changed and why it matters
    (from POST /ai/policy/executive-summary)
  
  Conflicts section (if any):
    Red header: "⚠ {N} Conflicts Found"
    Each: [Type badge] Description + Framework reference + Suggested fix
    
  Clear section:
    Green header: "✓ No Conflicts" (if none)
  
  [Collapse] to hide if not needed
```

**Decision Panel (sticky bottom, always visible):**
```
Background: white, top border, shadow-up, height 72px
Content:
  Left: "Your Decision" label + current status badge (pending_approval)
  Right: 
    [Reject] — destructive outlined button, red border
    [Approve] — primary solid green button

[Approve] → ConfirmModal:
  Title: "Approve Policy?"
  "This will mark the policy as approved and notify the Compliance Officer."
  Note (optional textarea): "Add a comment for the submitter (optional)"
  [Cancel] [Approve Policy]
  PATCH /api/policies/:id { policy_status: "approved", approved_by: user_id, approved_at: now }
  + note stored if provided
  On success: toast "Policy approved", notification to CO, redirect to /policy/inbox

[Reject] → Reject Modal:
  Title: "Reject Policy"
  Fields:
    Rejection Reason*  textarea, min 30 chars, required
    placeholder "Be specific about what needs to be changed before resubmission"
  [Cancel] [Reject Policy]
  PATCH /api/policies/:id { policy_status: "rejected", rejection_reason: text }
  On success: toast "Policy rejected. CO has been notified.", notification to CO, redirect to /policy/inbox
```

---

### PAGE: Approval History
Route: /policy/history

**Purpose:** Record of all policies the approver has signed off on or rejected. Compliance evidence.

**Layout:**
```
PageShell title="Approval History"
[Filter bar]
[Policies Table]
```

**Filter Bar:**
```
[Search — by policy name]
[Decision: All | Approved | Rejected]
[Framework: All | ...]
[Date range]
```

**Policies Table:**
```
Columns:
  Policy Name | Version | Framework | Decision | Decided At | Submitted By | Rejection Reason | Actions

Decision: Approved (green ✓) | Rejected (red ✗)
Rejection Reason: truncated to 1 line, tooltip for full text, "—" for approved
Actions per row:
  [View] → /policy/:id/review in read-only mode (no action buttons, just view)

Pagination: 20 per page
Empty: "No approval history yet."
```

---

## READ-ONLY ASSESSOR PAGES

Role: Read-Only Assessor | Route prefix: /assessor
Board members, regulators, senior observers. They see aggregate data only.
No edit capabilities on any page. The AI chat is the primary value for this role.

---

### PAGE: Executive View Dashboard
Route: /assessor/dashboard

**Purpose:** Strategic compliance overview. Charts and metrics only. No operational detail.

**Layout:**
```
PageShell title="Compliance Overview"
  subtitle="{institution_name} — {current month, year}"
[Last Updated banner]
[4 KPI Tiles]
[2-column: Framework Readiness | Compliance Trend]
[2-column: Top Risk Areas | Incident Overview]
```

**Last Updated Banner:**
```
Subtle gray info bar:
  ℹ Data reflects compliance status as of {last_assessment_date}. Updated when new assessments are completed.
```

**KPI Tiles (4, large and visual):**
```
Overall Compliance Score
  Large number: 74%
  Gauge/donut chart (recharts RadialBarChart)
  Delta: ↑ 3% vs last quarter (green) / ↓ 2% (red)

Frameworks Assessed
  N of 6 frameworks
  Icon grid of 6 framework logos (colored if assessed, gray if not)

Active Gaps
  Count by severity:
  [●] Critical: 2  [●] High: 7  [●] Medium: 14  [●] Low: 9
  No links — read only

Incidents This Quarter
  Total: N
  Resolved: N (green)
  Open: N (red if any)
```

Data source: GET /api/assessor/dashboard-stats
(Returns only aggregated counts — no identifiable data per ContextBuilder.for_read_only_assessor)

**Framework Readiness (left column):**
```
Horizontal bar chart (recharts BarChart):
  Y-axis: framework names
  X-axis: 0-100%
  Bar color: <50% red | 50-75% amber | >75% green
  Labels on bars: percentage

Click on bar: no action (read only). Tooltip on hover shows exact percentage.
```

**Compliance Trend (right column):**
```
Line chart (recharts LineChart):
  X-axis: last 6 months (monthly buckets)
  Y-axis: overall compliance percentage
  Single line: primary color
  Tooltip: "March 2025: 68%"
  Reference line at 80%: dashed gray with label "Target: 80%"
```

**Top Risk Areas (bottom left):**
```
Card title: "Top Risk Areas"
Simple ranked list:
  1. [●] Data Protection — DPDP Act 2023 (Critical)
  2. [●] Access Control — ISO 27001:2022 (High)
  3. [●] Incident Response — CERT-In 2022 (High)
  4. [●] Research Data Governance — UGC Guidelines (Medium)
  5. [●] Quality Assurance — NAAC Criteria 4&6 (Medium)

Source: AI risk heatmap result (GET /api/assessor/top-risks)
Not real-time — refreshed when Institution Admin generates new heatmap
```

**Incident Overview (bottom right):**
```
Card title: "Incident Summary"
Bar chart: incidents by type (last 12 months)
  Categories: Data Breach | Unauthorized Access | Ransomware | Phishing | Other
  Counts only (no incident titles, no descriptions, no PII)
  
Below chart:
  "All incidents resolved within regulatory deadlines: {N}% compliance"
```

---

### PAGE: Report Library
Route: /assessor/reports

**Purpose:** Access finalized audit reports and executive briefings. Read and download.

**Layout:**
```
PageShell title="Report Library"
[Filter bar]
[Reports Grid — card view]
```

**Filter Bar:**
```
[Search — by report name]
[Report Type: All | NAAC | ISO Readiness | DPDP Assessment | Custom]
[Framework: All | ...]
[Date range: Generated between]
```

**Reports Grid (card view — 3 per row):**
```
Each report card:
  ┌──────────────────────────────────────┐
  │  [Report type icon — PDF/document]   │
  │                                      │
  │  ISO 27001 Readiness Report          │
  │  Q3 2025                             │
  │                                      │
  │  ISO 27001:2022  |  Aug 12, 2025     │
  │  Generated by: Compliance Officer    │
  │                                      │
  │  [View Report]  [Download PDF]       │
  └──────────────────────────────────────┘

[View Report] → /assessor/reports/:report_id (opens report viewer, same as auditor's ReportView)
[Download PDF] → signed URL → browser download

Empty state: "No reports available yet. Reports are generated by the Compliance Officer and Auditor."
```

---

### PAGE: Q&A Interface (AI Chat)
Route: /assessor/chat

**Purpose:** Conversational interface for asking questions about the institution's compliance posture and regulatory frameworks. This is the most valuable feature for this role.

**Layout:**
```
Custom full-height chat layout (no standard PageShell):
  [Chat Header — fixed top]
  [Message Thread — scrollable, fills height]
  [Input Area — fixed bottom]
```

**Chat Header:**
```
Left: Bot icon + "Compliance AI" + "Powered by ComplySense AI" (secondary text)
Right: [New Conversation] button (clears current thread, starts fresh)
       [Conversation History] button (opens list of past conversations)
```

**Message Thread:**
```
Scrollable area, background: slate-50 (light) / slate-900 (dark)
Most recent messages at bottom (standard chat behavior)
Auto-scrolls to bottom on new message

User messages (right-aligned):
  White bubble with primary border, user avatar on right
  Text: message content
  Timestamp: below bubble, small, secondary text

AI messages (left-aligned):
  White card (more spacious than a bubble), AI avatar (sparkle icon) on left
  
  Content rendering:
    Text: markdown rendered (bold, bullets, numbered lists all work)
    Tables: rendered properly (framework tables are common in responses)
    Code/IDs: monospace styling
  
  Source Citations (below AI message):
    Small chips showing what was referenced:
    [📚 DPDP Act 2023 — Section 8] [📚 ISO 27001:2022 — A.5.1]
    These are the retrieved knowledge base chunks used to answer
    Hovering a citation chip shows the section title as tooltip
  
  Disclaimer (below each AI response, small secondary text):
    "Response based on ComplySense knowledge base and your institution's aggregated data."
  
  Action buttons below AI message (contextual):
    If response mentions a framework → [View in Report Library]
    If response about a metric → [View Dashboard]
```

**Input Area:**
```
Background: white, top border, padding 16px
Layout:
  [Textarea — auto-height, min 1 row max 5 rows]
  [Send button — right side, primary, icon only (Send icon)]

Textarea:
  placeholder "Ask about your compliance posture, regulations, or specific frameworks..."
  Shift+Enter = new line
  Enter = send

Suggested prompts (shown only when thread is empty — new conversation):
  4 prompt chips:
    "What is our current ISO 27001 compliance score?"
    "What were our top 3 compliance gaps last quarter?"
    "Explain what DPDP Act 2023 means for our institution"
    "Why did our compliance score change this month?"
  
  Click chip → populates textarea → auto-sends

Loading state (while AI responds):
  AI message bubble appears immediately with typing indicator:
  ● ● ●  (animated 3-dot indicator)
  
Error state:
  Red AI bubble: "I couldn't generate a response. Please try again."
  [Retry] button in bubble

Conversation persistence:
  Each conversation stored in ai_conversations table
  agent_type = "assessor_qa"
  messages = [{role, content, timestamp, citations}]
  
  History is loaded on page mount (GET /api/ai-conversations?agent_type=assessor_qa&limit=1)
  Continues most recent conversation by default
  [New Conversation] creates new ai_conversations row
```

**Conversation History Panel:**
```
Opened by [Conversation History] button → Sheet (right side, 320px)
List of past conversations:
  Each row:
    First user message (truncated 1 line)
    Date + message count
    Click → loads that conversation in main thread

[Delete] button per row (clears ai_conversations row)
[Close] button
```