# ComplySense UI Specification
# Document 7 of 7 — AI Panel Specifications Across All Roles

This document defines exactly how the AI features behave across every role.
It covers the shared AIPanel drawer component, role-specific behavior differences,
input formats, output rendering, loading states, error handling,
and how AI output connects to page actions.

---

## 1. TWO TYPES OF AI UI

Before speccing each role, define the two modes AI appears in:

**Type A — AIPanel Drawer (right-side Sheet, 420px)**
Used for: task-specific, single-shot AI requests triggered by a button.
Examples: CERT-In draft, contract analysis, compliance triage, observation draft.
The user triggers it, AI runs, result shown, user acts on it.
Not persistent — closes when navigated away.

**Type B — Full-Page AI Chat**
Used only for: Read-Only Assessor (/assessor/chat)
Multi-turn conversation, persistent history, citations shown.
Specced in full in Doc 6.

**Type C — Inline AI Panel (embedded in page, not a drawer)**
Used for: Policy Editor AI Copilot (right column, always visible on the page)
Also: Dashboard AI triage panels (embedded cards, not drawers)
Not a Sheet — part of the page layout itself.

---

## 2. SHARED AIPANEL DRAWER COMPONENT SPEC

```
Component: Sheet (shadcn/ui, side="right")
Width: 420px
Cannot be resized
Does not block the main content (overlay, not modal)
Clicking outside does NOT close it (user must explicitly close)
Close: X button in header

Structure:
  ┌────────────────────────────────────────┐
  │ [Sparkle icon] {Panel Title}    [X]   │ ← Header (56px, border-bottom)
  ├────────────────────────────────────────┤
  │                                        │
  │        CONTENT AREA                    │ ← Scrollable, flex-col
  │        (role-specific, see below)      │
  │                                        │
  ├────────────────────────────────────────┤
  │        FOOTER (optional)               │ ← Action buttons if applicable
  └────────────────────────────────────────┘

Header color: always white background, primary sparkle icon
Z-index: 50 (above main content, below modals)
```

### Panel States

**Empty / Not Yet Run:**
```
Center of content area:
  Sparkle icon (large, primary color, 48px)
  Title: {action-specific message}
  Description: what the AI will do
  [Primary Action button]
```

**Loading:**
```
3 content skeleton blocks:
  Block 1: full-width bar (60% width)
  Block 2: 3 shorter lines (full, 80%, 60%)
  Block 3: full-width bar (40% width)
Animated shimmer (CSS animation)
Status text below skeletons (updates every ~3 seconds):
  "Reviewing input..."
  "Checking regulatory frameworks..."
  "Preparing response..."
(messages rotate via setInterval — makes the wait feel purposeful)
```

**Success:**
```
Content rendered per role spec below.
[Regenerate] ghost button always shown in footer after first run.
Last run timestamp: small, secondary text, footer left.
```

**Error:**
```
Center:
  AlertCircle icon (red, 36px)
  "Failed to generate response"
  Secondary text: specific error message (sanitized — never raw API errors)
  [Retry] button — primary
  [Report Issue] link — opens mailto or feedback form
```

---

## 3. AI FEATURES PER ROLE

---

### COMPLIANCE OFFICER — AI Features

**A. Smart Triage Panel (Type C — Inline Dashboard Card)**

Location: /compliance/dashboard, left column major card
Trigger: [Run AI Triage] button inside the card

Input sent to AI service:
```
POST /ai/compliance/triage
Payload assembled by backend (never sent directly from frontend):
  {
    calling_role: "compliance_officer",
    institution_id: "...",
    // Backend assembles these from DB before calling AI:
    alerts: [
      { alert_id, type, control_id, control_title, framework, status, due_date, evidence_count },
      ...
    ]
  }
```

Output rendering in card:
```
Numbered list 1-10:
[1] [CRITICAL badge] Control {ID}: {title}
    {1-line explanation}
    {recommended action}
    [Action button] — primary action for this item:
      e.g. [Assign Task] / [View Control] / [Upload Evidence]
    
[2] [HIGH badge] ...

Priority badges:
  CRITICAL → red bg
  HIGH     → orange bg
  MEDIUM   → amber bg
  LOW      → green bg

At bottom of list:
  "Note: 3 alerts flagged as likely false positives — archived automatically"
  [View false positives ▾] — collapsible list of archived items
```

Connecting to page actions:
```
[Assign Task] button → opens Create Mitigation Task modal, pre-filled with control_id
[View Control] → navigate to /compliance/controls/:assignment_id
[Upload Evidence] → navigate to /compliance/controls/:assignment_id (scrolls to evidence section)
```

---

**B. Regulatory Change Gap Analysis (Type A — AIPanel Drawer)**

Location: /compliance/dashboard, triggered by [Analyze Regulation] button in a secondary card OR /compliance/gaps page
Trigger: user pastes regulation text

Panel Title: "Regulatory Change Analysis"

Panel Content (not-yet-run state):
```
Label: "Paste regulation text or amendment"
Textarea:
  placeholder "Paste the text of a new regulation, amendment, or government circular..."
  min-height 150px, max 3000 chars, char counter
  
[Analyze Gap Impact] button — primary
  Disabled until at least 200 chars entered
```

Loading:
```
"Identifying new requirements..."
"Comparing against current controls..."
"Generating gap report..."
```

Output:
```
Section: New Requirements Identified
  Bullet list of new regulatory requirements found

Section: Controls Needing Updates (with framework badges)
  Each item: [Control ID] + [what needs to change]
  Each has: [Update Control →] button → navigate to that control

Section: New Controls to Create
  List of net-new controls implied by the regulation
  [Create Assignment →] button per item → Create Control Assignment modal

Section: Timeline Risk
  If hard deadline found: amber/red banner with deadline date
  "No hard deadline identified" if not found
```

---

**C. Policy Generation AI Copilot (Type C — Inline in Policy Editor)**

Fully specced in Doc 3 (Policy Editor page).
Key behaviors:
- Wizard structured questions (no free-text except last optional field)
- Pre-flight compliance check before generation
- Streaming output section by section into Tiptap editor
- AI-generated sections marked with blue left border (fades on user edit)
- Validate tab analyzes existing policy documents against frameworks

---

### IT SECURITY OFFICER — AI Features

**CERT-In Report Drafter (Type A — AIPanel Drawer, right panel of Incident Command Center)**

Location: /security/incidents/:id
Trigger: [AI: Draft CERT-In Report] button inside CERT-In Checklist card

Panel Title: "CERT-In Report Draft"

Loading messages (these are high-stress moments — language must feel helpful and fast):
```
"Reading incident details..."
"Reviewing CERT-In 2022 mandatory fields..."
"Checking DPDP notification requirements..."
"Writing report draft..."
```

Output:
```
Monospace font — this is a formal document
Black text on off-white (#FAFAF7) background

CERT-In INCIDENT REPORT
━━━━━━━━━━━━━━━━━━━━━━━
Organization:      {institution_name}
Contact Person:    {assigned_to full_name}
Designation:       {assigned_to designation}
Contact Email:     {assigned_to email}
Date of Report:    {today}

1. INCIDENT NATURE
   Type:        {incident_type readable}
   Severity:    {severity}

2. TIMELINE
   Occurred:    {occurred_at formatted}
   Detected:    {detected_at formatted}
   Reported:    {today} at {time}

3. AFFECTED SYSTEMS
   {affected_systems or "[FILL IN: List affected systems, IPs, hostnames]"}

4. AFFECTED DATA
   {affected_data_categories or "[FILL IN: Describe categories of data affected]"}

5. ESTIMATED IMPACT
   {AI-generated 2-3 sentence impact assessment based on incident type and data}

6. IMMEDIATE ACTIONS TAKEN
   {Timeline entries pulled in + AI-formatted as formal actions taken}

7. CURRENT STATUS
   {status readable}

8. FOLLOW-UP CONTACT
   {assigned_to full_name, designation, email, phone}
━━━━━━━━━━━━━━━━━━━━━━━

[FILL IN:] fields are shown in amber highlight — user must fill before submitting

Unresolved [FILL IN:] count: "2 fields need manual completion" — amber banner at top of draft
```

Footer actions:
```
[Copy to Clipboard]
[Download as .txt]
[Mark CERT-In as Reported] — primary green
  ConfirmModal: "Have you submitted this report to the CERT-In portal?"
  On confirm: PATCH incidents/:id { cert_in_reported: true, cert_in_reported_at: now }
              Timer bar updates. Toast "CERT-In reported."
[Regenerate] — ghost
```

---

### AUDITOR — AI Features

**A. Smart Sampling (Type A — AIPanel Drawer)**

Location: /auditor/workspace
Trigger: [AI: Smart Sample] button in Assessment Selector Bar

Panel Title: "Smart Evidence Sampling"

Input (assembled by backend, not from frontend directly):
```
Evidence metadata for current assessment:
  control status, evidence count per control, control severity (from gaps)
```

Output:
```
Header:
  "Review these {N} items first — highest risk identified"
  Progress indicator: "Recommended sample: {N} of {total} evidence items"

Sampled evidence list:
  Each item:
    [★] {filename} — {control_id}
    Risk reason: "Control non-compliant, evidence uploaded 14 days after due date"
    [View →] — scrolls main panel to this evidence item

Section divider: "Lower priority — review if time allows"
  Remaining items listed without risk reasoning

At bottom:
  [Apply Highlights] button — marks priority items with ★ in center panel
  [Clear] — removes all highlights
```

---

**B. Observation Drafter (Inline in Audit Workspace right panel)**

Location: /auditor/workspace, right panel below the observation textarea
Trigger: [AI: Draft Observation] button

This is NOT a drawer — it runs inline in the right panel.

Input (user provides in right panel):
```
Control already selected in left panel
Evidence already previewed in center panel
User may have typed partial observation text in textarea
```

Loading (inline, textarea replaced with skeleton):
```
"Drafting observation..."
```

Output:
```
AI text streams into the textarea (simulated streaming via character-by-character append)
Amber banner appears above textarea:
  "AI drafted this observation. Review and edit before submitting — you are responsible for this finding."

The AI draft uses formal audit language:
  Condition: [what was found]
  Criteria: [what the control/regulation requires]
  Cause: [likely reason for the gap]
  Effect: [risk/impact]
  Recommendation: [suggested fix]

User must make at least one edit before [Add Observation] button activates
  (tracked via isDirtyFromAI flag — once user types, flag clears)
```

---

### DEPARTMENT REVIEWER — AI Features

**A. Plain English Translator (Inline in Task Wizard Step 1)**

Not a drawer. Runs automatically when the Task Wizard page loads.

Trigger: Automatic on page load (if translation not yet cached for this control)

Loading (shown in Step 1 AI Translation box):
```
Skeleton of 3 lines (simulates 2-3 second AI call)
```

Output:
```
Injected into Step 1 "AI Translation" box:
  "In plain terms: {translated requirement in clear, jargon-free English}"

Evidence checklist items below:
  Translated via same AI call — plain English bullet list of what to upload
  
These are cached: once translated for a control, stored in backend
  Redis cache key: "translate:{control_id}:{lang:en}"
  TTL: 7 days (controls don't change often)
  If cache hit: instant display, no loading state
```

---

**B. Pre-Flight Evidence Check (Inline in Task Wizard Step 2 and Evidence Upload page)**

Trigger: [AI Check: Will this work?] button appears after file is selected

Input:
```
File metadata (name, size, mime_type) + control_requirement text
+ File content preview (first 2000 chars if text-extractable, or image thumbnail description)
```

Loading state (in-place, below file preview):
```
Spinner + "Checking your file..."
Duration: ~3-5 seconds
```

Output states:

**PASS:**
```
┌────────────────────────────────────────────────────────┐
│ ✅ This looks good!                                    │
│ This evidence should meet the requirement for          │
│ "{control_title in plain English}"                     │
└────────────────────────────────────────────────────────┘
Green border, green check icon
[Continue →] button active
```

**WARN:**
```
┌────────────────────────────────────────────────────────┐
│ ⚠ This might not be enough                             │
│                                                        │
│ Issue: No date is visible in this screenshot.          │
│ The reviewer will need to verify when this was taken.  │
│                                                        │
│ Suggestion: Take a new screenshot that includes the    │
│ current date in the system clock or window title.      │
│                                                        │
│ [Upload anyway]  [Choose different file]               │
└────────────────────────────────────────────────────────┘
Amber border, warning icon
[Upload anyway] activates upload — adds WARN flag to evidence record
```

**FAIL:**
```
┌────────────────────────────────────────────────────────┐
│ ❌ This won't work                                     │
│                                                        │
│ This file is an unrelated HR form and does not         │
│ show anything about login or password requirements.    │
│                                                        │
│ What you need: A screenshot of your computer's         │
│ login screen or your IT policy about passwords.        │
│                                                        │
│ [Choose different file]                                │
└────────────────────────────────────────────────────────┘
Red border, X icon
Upload button disabled until new file chosen
```

---

### VENDOR REVIEWER — AI Features

**Contract Analyzer (Type A — AIPanel Drawer)**
(Also triggered inline from vendor detail Contract Analysis tab — same drawer, different entry point)

Location: /vendor/vendors/:id (Contract Analysis tab)
Trigger: [Analyze with AI] button after PDF uploaded

Panel Title: "Contract Analysis"

Loading messages:
```
"Extracting document content..."
"Checking DPDP Act 2023 requirements..."
"Reviewing ISO 27001 supplier controls..."
"Summarizing findings..."
```
(These are realistic — PDF extraction + AI call takes 15-25 seconds)

Output:
```
Overall Risk Badge — large, top of result:
  [HIGH RISK] / [MEDIUM RISK] / [LOW RISK] in appropriate colors

Section 1: DPDP Act 2023 Compliance Gaps
  Red header with count: "3 gaps found"
  Each gap: red left border card
    [DPDP Section N.N badge]
    Description of missing or inadequate clause
    Example: "No breach notification timeline specified. DPDP Section 8(6) requires notification within 72 hours."
    
    If gap is fixable with a clause: [Copy suggested clause text] button
      → Copies standard clause text to clipboard
      → "Suggested addition: 'In the event of a personal data breach, [Vendor] shall notify [Institution] within 72 hours of becoming aware...'"

Section 2: ISO 27001:2022 Supplier Control Gaps
  Amber header with count: "2 gaps found"
  Each gap: amber left border card
    [ISO Annex A.X.X badge]
    Description

Section 3: Top 3 Recommendations
  Numbered, plain language
  1. Request DPA addendum covering DPDP Section 7 obligations
  2. Add right-to-audit clause
  3. Confirm data localization (processing must occur in India)

Footer of output:
  Disclaimer: "This analysis is AI-generated and should be reviewed by your legal/compliance team before acting."
  [Export Analysis PDF] — downloads analysis as formatted PDF
  [Regenerate] ghost button
```

---

### POLICY APPROVER — AI Features

**Conflict Detector + Executive Summary (Type C — Inline Card in Policy Review page)**

Location: /policy/:id/review page, between diff viewer and decision panel
Trigger: [Run AI Analysis] button in the AI Analysis Card

Two AI calls made in parallel:
1. POST /ai/policy/conflict-detect
2. POST /ai/policy/executive-summary

Both results shown in the same card.

Loading (single combined loading state):
```
In the card: skeleton 4 lines
"Checking for conflicts with existing policies..."
"Generating executive summary..."
```

Output — Executive Summary section (top):
```
Gray bordered card, slightly tinted background:
  "Why this policy is changing:"
  {1-2 sentence AI summary of what changed and the regulatory driver}
  
  "Who is affected:"
  {roles and departments mentioned in policy scope}
  
  "Key change:"
  {most significant modification in plain language}
  
  "Regulatory basis:"
  [DPDP Act 2023 badge] or relevant framework badge
```

Output — Conflicts section (below summary):
```
If no conflicts:
  Green card: "✓ No conflicts found with existing policies or regulations"

If conflicts found:
  Red header: "⚠ {N} Conflicts Found — Review before approving"
  Each conflict card:
    Conflict type badge: Direct Contradiction | Overlap | Regulatory Violation
    ───────────────────────────────
    "This policy states: {quote}"
    "Conflicts with: {existing policy name, section}"
    "Because: {explanation}"
    "Suggested fix: {recommendation}"
    ───────────────────────────────
```

---

### INSTITUTION ADMIN — AI Features

**Predictive Risk Heatmap (Type C — Inline Dashboard Card)**

Location: /admin/dashboard
Trigger: [Generate Risk Prediction] button in "AI Insights" card

Input (backend assembles before calling AI):
```
Department compliance scores, framework readiness percentages,
open incident counts by category, overdue control counts by department
(All aggregate data — no individual records)
```

Loading (in card):
```
Skeleton list of 5 items
"Analyzing compliance trends..."
```

Output:
```
In the "AI Insights" card on the dashboard:

Numbered list 1-5:
  [1] [CRITICAL badge] {Framework}: {Risk description}
      Affected: {department name(s)}
      Signal: {what data pattern suggests this risk}
      
  [2] [HIGH] ...
  ...

Last generated: {relative timestamp}
[Regenerate] ghost button — re-runs analysis
```

---

### SUPER ADMIN — AI Features

**Anomaly Detection Banner (Passive, no trigger)**

Location: /super-admin/dashboard
This is NOT triggered by the user — it's a result of a background job.

The backend `jobs.py` runs an anomaly detection check periodically (every 4 hours) using audit_logs data.
The AI result is stored and surfaced on next dashboard load.

```
Passive banner if anomaly detected:
  ⚠ AI Alert: {anomaly description}
  [{N} institutions flagged] [Investigate →] [Dismiss]
  
No interactive loading state — result was pre-computed by background job
```

---

## 4. COMMON AI BEHAVIOR RULES

These apply to every AI feature across all roles:

**Never auto-run on page load:**
All AI features except the Dept Reviewer's translation (which has a dedicated page for it) require explicit user trigger. No AI call fires without user intent.

**Always show a disclaimer for regulatory content:**
Any response referencing regulation text shows below:
```
"Based on ComplySense knowledge base (DPDP Act 2023, ISO 27001:2022, etc.).
Verify critical regulatory interpretations with your legal team."
```
Small, secondary text, below every regulatory AI response. Not intrusive.

**Regenerate always available after first run:**
Every AI panel shows [Regenerate] in footer once a result has been shown. Clicking re-runs the same request with fresh results.

**Citation chips for framework references:**
When an AI response cites a specific framework section, the section name appears as a chip:
```
[📚 DPDP Act 2023 — Section 8(6)]
```
These are non-interactive labels (no click action) — they show what was used.

**Loading never blocks the entire page:**
AI drawers and inline panels load independently. The rest of the page is always usable while AI processes.

**Never expose raw AI API errors:**
If the AI service returns an error:
  503 (not ready): "AI service is starting up. Try again in a moment."
  429 (rate limit): "Too many requests. Please wait 30 seconds."
  500 (error): "Something went wrong. Please try again."
  OpenAI timeout: "Response took too long. Try with a shorter input."

**FAIL-SAFE output rule:**
If the AI response validator rejects a response (jailbreak detected or fabricated citation):
```
Show in place of normal output:
  Gray card: "Unable to generate a valid response for this request.
  Please rephrase and try again, or contact your compliance administrator."
[Try Again] button
```
Never show the rejected content.

---

## 5. API ROUTING FROM FRONTEND

All AI calls from the frontend go to the **main backend** (`/api/ai/*`), NOT directly to the AI service.

```
Frontend → POST /api/ai/compliance/triage
           ↓
Main Backend (port 8000):
  - Validates JWT
  - Checks role permission (guards.py equivalent in main app)
  - Assembles context data from DB (never lets frontend pass raw DB data)
  - Forwards sanitized payload to → AI Service (port 8001) POST /ai/compliance/triage
           ↓
AI Service → LangChain → OpenAI → Response
           ↓
Main Backend → Validates response (response_validator)
           ↓
Frontend ← Formatted result
```

This means:
- Frontend never has direct access to the AI service URL
- Frontend never constructs the AI payload (main app does from DB data)
- Role permissions checked at main app level (not just in AI service)
- AI service VITE_AI_URL is never exposed in frontend environment variables

The only exception: `VITE_AI_URL` is in `.env.example` for local dev direct testing.
Production: AI service URL not in frontend at all.

---

## 6. AI FEATURE AVAILABILITY SUMMARY

| Feature | Role | Type | Trigger | Auto-run |
|---|---|---|---|---|
| Smart Triage | Compliance Officer | Inline card | Button | No |
| Regulatory Change Analysis | Compliance Officer | Drawer | Button | No |
| Policy Generation Wizard | Compliance Officer | Inline (editor) | Button | No |
| Policy Validation | Compliance Officer | Inline (editor tab) | Button | No |
| CERT-In Report Draft | IT Security Officer | Drawer (in Incident) | Button | No |
| Smart Evidence Sampling | Auditor | Drawer | Button | No |
| Observation Drafter | Auditor | Inline (right panel) | Button | No |
| Plain English Translation | Dept Reviewer | Inline (Step 1) | Auto (cached) | Yes (cached) |
| Pre-Flight Evidence Check | Dept Reviewer | Inline (Step 2) | Button | No |
| Contract Analysis | Vendor Reviewer | Drawer | Button | No |
| Conflict Detector | Policy Approver | Inline card | Button | No |
| Executive Summary | Policy Approver | Inline card | Button | No |
| Q&A Chat | Read-Only Assessor | Full page | Message send | No |
| Risk Heatmap | Institution Admin | Inline card | Button | No |
| Anomaly Detection | Super Admin | Passive banner | Background job | Yes (background) |