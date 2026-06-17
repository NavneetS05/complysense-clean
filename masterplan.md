# ComplySense — Master Architecture & Build Plan
**Version:** 1.0  
**Timeline:** 15 Days  
**Stack:** React + Vite · FastAPI · PostgreSQL (Neon) · MongoDB Atlas · LangChain + OpenAI · Supabase Storage  
**Architect:** Garv Jain  

---

## SESSION SUMMARY (Update after every session)

```
Last updated : Session 1 — Initial Architecture
Completed    : Planning document created
In progress  : Nothing yet — setup starts next
Next session : Project scaffolding + schema migration + auth
Blockers     : 6 framework document names (knowledge base) — pending from Garv
```

---

## 1. SCHEMA ASSESSMENT

### Verdict: Keep as-is. One addition.

The v2 schema is clean, well-isolated, and covers every role's operational need. No redesign required.

**One table to add — `ai_conversations`**

The Read-Only Assessor Q&A chatbot and the Compliance Officer triage chat need persistent conversation history so the AI has context across turns. Nothing in the current schema handles this.

```sql
CREATE TABLE ai_conversations (
    conversation_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id    UUID REFERENCES institutions(institution_id),
    user_id           UUID REFERENCES users(user_id),
    agent_type        VARCHAR(100) NOT NULL,
    -- assessor_qa / compliance_triage / cert_in_draft / vendor_analysis / policy_conflict
    messages          JSONB NOT NULL DEFAULT '[]',
    -- [{role: "user"/"assistant", content: "...", timestamp: "..."}]
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_conversations_user ON ai_conversations(user_id);
CREATE INDEX idx_ai_conversations_type ON ai_conversations(agent_type);
```

**Minor flags (not blockers):**

- `evidence_documents.file_path` — stores Supabase object path (e.g. `evidence-documents/institution_id/file.pdf`). This is correct as designed.
- `generated_policies.policy_content TEXT` — fine for MVP. Large policies might hit PostgreSQL row limits at extreme scale, not a concern here.
- `control_assignments UNIQUE(institution_id, control_id)` — correct. One status row per control per institution.
- `compliance_calendar.related_entity_id UUID` — this is a polymorphic FK (no FK constraint by design). Acceptable for MVP.

---

## 2. PAGES BY ROLE

Routes follow the pattern `/<role-prefix>/<page>`. Each role gets a layout wrapper with a role-aware sidebar. Shared auth pages live at `/auth/*`.

---

### AUTH (All Roles)
| Route | Page | Notes |
|---|---|---|
| `/login` | Login | Email + password, returns JWT + role |
| `/forgot-password` | Forgot Password | Sends reset link |
| `/reset-password/:token` | Reset Password | Token from `password_reset_tokens` |

---

### SUPER ADMIN `/super-admin/*`
Daily frequency: Low. Triggered by AI anomaly alerts.

| Route | Page | Use Case |
|---|---|---|
| `/super-admin/dashboard` | Global Health Map | All institutions, status Green/Amber/Red, active users, error rates |
| `/super-admin/tenants` | Tenant Manager | List institutions, create new, activate/deactivate |
| `/super-admin/tenants/:id` | Institution Detail | View users, departments, audit logs for one institution |
| `/super-admin/audit-trail` | Audit Trail Explorer | Filter `audit_logs` by user, action, date, institution |
| `/super-admin/roles` | Role & Permission Viewer | Read-only view of RBAC matrix. Seeded, not editable by UI |

**AI feature on this role:** Anomaly detection alert banner on dashboard (flags mass role changes, unusual access times). Runs passively — no dedicated AI page.

---

### INSTITUTION ADMIN `/admin/*`
Daily frequency: Medium. Weekly reviews + onboarding.

| Route | Page | Use Case |
|---|---|---|
| `/admin/dashboard` | Institution Risk Scorecard | Compliance % by framework, top 3 emerging risks, dept heatmap |
| `/admin/departments` | Department Manager | List depts, create, assign Department Reviewer user |
| `/admin/users` | User Lifecycle Manager | List all institution users, create, assign roles, activate/deactivate |
| `/admin/calendar` | Compliance Calendar | All upcoming control deadlines, assessment schedules, vendor expiries |
| `/admin/reports` | Executive Briefing | Select timeframe → AI generates a PDF/HTML risk summary |

**AI feature:** Predictive Risk Heatmap on dashboard. Morning digest email (described in AI service section).

---

### COMPLIANCE OFFICER `/compliance/*`
Daily frequency: High. Primary operator — opens this every morning.

| Route | Page | Use Case |
|---|---|---|
| `/compliance/dashboard` | Compliance Overview | Control completion %, active gaps, evidence queue count, tasks overdue |
| `/compliance/controls` | Control Task Manager | Kanban board: Not Started → In Progress → Submitted → Verified. Filterable by framework |
| `/compliance/controls/:id` | Control Detail | Control info from MongoDB, assignment status, linked evidence, notes |
| `/compliance/gaps` | Gap Assessment Matrix | Grid: frameworks × severity. Drill into gap detail, assign mitigation task |
| `/compliance/evidence-queue` | Evidence Verification Queue | Approve/reject uploaded evidence with comments. Bulk actions |
| `/compliance/assessments` | Assessment List | All assessments, status, framework, start new |
| `/compliance/assessments/:id` | Assessment Runner | Question-by-question response form against a framework's controls |
| `/compliance/policies` | Policy Manager | List drafted policies, create new, send to Policy Approver |
| `/compliance/tasks` | Mitigation Task Manager | All tasks across all depts, filter by status/priority/dept |
| `/compliance/notifications` | Notification Center | All system alerts for this user |

**AI features:** Smart Triage panel on dashboard (top 10 critical items). Regulatory Change Agent (paste new regulation text → get gap analysis). Both are in-page panels, not separate routes.

---

### IT SECURITY OFFICER `/security/*`
Daily frequency: High. Real-time during incidents.

| Route | Page | Use Case |
|---|---|---|
| `/security/dashboard` | Technical Control Health | Pass/fail status of IT controls (NIST Annex A focus), incidents summary |
| `/security/incidents` | Incident Register | List all incidents, filter by status/severity |
| `/security/incidents/new` | Log Incident | Form: type, description, occurred_at, detected_at. Starts CERT-In clock on submit |
| `/security/incidents/:id` | Incident Command Center | Live 6-hour countdown timer. CERT-In checklist. DPDP breach toggle. Timeline log. AI draft button |
| `/security/controls` | IT Control Assignments | Controls assigned to this role, upload evidence against them |
| `/security/evidence` | Technical Evidence Upload | Upload logs, scan reports, config screenshots. Pre-flight AI check |

**AI features:** CERT-In Draft button on `/security/incidents/:id` — sends incident data to AI service, returns a formatted CERT-In report draft. Officer reviews and sends.

---

### AUDITOR `/auditor/*`
Daily frequency: Medium. Seasonal peaks during audit cycles.

| Route | Page | Use Case |
|---|---|---|
| `/auditor/workspace` | Audit Workspace | Read-only control list + evidence view. Right side panel for adding observations. Linked to one assessment |
| `/auditor/observations` | Finding Tracker | All observations: open / acknowledged / resolved. Filter by severity |
| `/auditor/reports` | Report Builder | Select assessment → drag sections → generate PDF audit report |
| `/auditor/reports/:id` | Report View | View a generated audit report |

**AI features:** Smart Sampling — on workspace, AI highlights which evidence items are statistically high-risk and should be reviewed first. Drafting Assistant — pre-fills observation text based on prior similar findings.

---

### DEPARTMENT REVIEWER `/dept/*`
Daily frequency: Medium. Task-driven — they come when assigned.

| Route | Page | Use Case |
|---|---|---|
| `/dept/dashboard` | My Department Dashboard | My dept's compliance score, pending tasks count, recent evidence status |
| `/dept/tasks` | Task List | All tasks assigned to me. Simple list with priority + due date |
| `/dept/tasks/:id` | Task Wizard | Step-by-step guided interface for completing a control. Plain English AI translation of the requirement |
| `/dept/evidence` | Evidence Vault | History of all uploaded files, approval status, rejection reasons |
| `/dept/self-assessment` | Self Assessment | Periodic questionnaire about local risks, submitted to Compliance Officer |

**AI features:** Plain-English Translator on Task Wizard (converts NIST/ISO jargon to simple language). Pre-Flight Check on evidence upload (AI validates file before submission).

---

### VENDOR REVIEWER `/vendor/*`
Daily frequency: Medium.

| Route | Page | Use Case |
|---|---|---|
| `/vendor/dashboard` | Vendor Risk Register | All vendors with risk level badges. Expiry alerts prominent |
| `/vendor/vendors/new` | Onboard Vendor | Form: name, category, DPA status, model training flag, contract expiry, contact |
| `/vendor/vendors/:id` | Assessment Workspace | Vendor detail, risk assessment form, upload contract/SOC2, AI analysis results |
| `/vendor/expiry` | Expiry Tracker | Calendar view + list of expiring vendor certifications and contracts |

**AI features:** Contract Analyzer on Assessment Workspace — upload a SOC2 / contract PDF → AI returns: missing DPDP clauses, high-risk findings, overall summary.

---

### POLICY APPROVER `/policy/*`
Daily frequency: Low. Event-driven (notification triggers login).

| Route | Page | Use Case |
|---|---|---|
| `/policy/inbox` | Policy Inbox | Policies pending my approval. Count badge drives notification email |
| `/policy/:id/review` | Policy Review | Full policy text. Diff viewer against previous version. AI conflict summary. Approve / Reject with comment |
| `/policy/history` | Approval History | All policies I've approved or rejected, with timestamps |

**AI features:** Conflict Detector (highlights contradictions with existing policies). Executive Summary (one-para brief on why this policy changed and who it affects).

---

### READ-ONLY ASSESSOR `/assessor/*`
Daily frequency: Low. Periodic oversight.

| Route | Page | Use Case |
|---|---|---|
| `/assessor/dashboard` | Executive View | High-level charts: compliance trend, top risks, framework readiness scores. No edit actions |
| `/assessor/reports` | Report Library | All finalized audit reports. Download PDF |
| `/assessor/chat` | Q&A Interface | Conversational RAG chatbot. Ask questions about compliance data, frameworks, incidents |

**AI features:** The entire Q&A page is the AI feature. LangChain RAG over framework knowledge base + summarized institutional data (no raw rows exposed).

---

## 3. FOLDER STRUCTURE

```
complysense/
│
├── package.json                        ← root runner (concurrently)
├── .env.example
├── .gitignore
├── render.yaml                         ← Render deployment (backend + ai_service)
├── vercel.json                         ← Vercel deployment (frontend)
│
├── frontend/                           ← React + Vite + Tailwind + Zustand
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       │
│       ├── routes/
│       │   ├── index.tsx               ← root router, role-based redirect
│       │   ├── ProtectedRoute.tsx      ← JWT + role guard
│       │   ├── AuthRoutes.tsx
│       │   ├── SuperAdminRoutes.tsx
│       │   ├── AdminRoutes.tsx
│       │   ├── ComplianceRoutes.tsx
│       │   ├── SecurityRoutes.tsx
│       │   ├── AuditorRoutes.tsx
│       │   ├── DeptRoutes.tsx
│       │   ├── VendorRoutes.tsx
│       │   ├── PolicyRoutes.tsx
│       │   └── AssessorRoutes.tsx
│       │
│       ├── layouts/
│       │   ├── AuthLayout.tsx
│       │   └── DashboardLayout.tsx     ← sidebar + topbar shell (role-aware)
│       │
│       ├── components/
│       │   ├── shared/
│       │   │   ├── Sidebar.tsx         ← nav items driven by role from store
│       │   │   ├── Topbar.tsx
│       │   │   ├── NotificationBell.tsx
│       │   │   ├── RoleAssumptionBar.tsx  ← shows assumed role + exit button
│       │   │   ├── DataTable.tsx
│       │   │   ├── StatusBadge.tsx
│       │   │   ├── FileUpload.tsx
│       │   │   ├── ConfirmModal.tsx
│       │   │   └── AIPanel.tsx         ← reusable right-side AI drawer
│       │   │
│       │   ├── auth/
│       │   ├── super-admin/
│       │   ├── institution-admin/
│       │   ├── compliance/
│       │   ├── security/
│       │   │   └── IncidentTimer.tsx   ← 6hr CERT-In countdown component
│       │   ├── auditor/
│       │   ├── dept/
│       │   ├── vendor/
│       │   ├── policy/
│       │   │   └── DiffViewer.tsx      ← side-by-side policy diff
│       │   └── assessor/
│       │       └── ChatInterface.tsx   ← RAG chatbot UI
│       │
│       ├── pages/
│       │   ├── auth/
│       │   │   ├── Login.tsx
│       │   │   ├── ForgotPassword.tsx
│       │   │   └── ResetPassword.tsx
│       │   ├── super-admin/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Tenants.tsx
│       │   │   ├── TenantDetail.tsx
│       │   │   ├── AuditTrail.tsx
│       │   │   └── Roles.tsx
│       │   ├── institution-admin/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Departments.tsx
│       │   │   ├── Users.tsx
│       │   │   ├── Calendar.tsx
│       │   │   └── Reports.tsx
│       │   ├── compliance/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Controls.tsx
│       │   │   ├── ControlDetail.tsx
│       │   │   ├── Gaps.tsx
│       │   │   ├── EvidenceQueue.tsx
│       │   │   ├── Assessments.tsx
│       │   │   ├── AssessmentRunner.tsx
│       │   │   ├── Policies.tsx
│       │   │   ├── Tasks.tsx
│       │   │   └── Notifications.tsx
│       │   ├── security/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Incidents.tsx
│       │   │   ├── NewIncident.tsx
│       │   │   ├── IncidentDetail.tsx
│       │   │   ├── Controls.tsx
│       │   │   └── Evidence.tsx
│       │   ├── auditor/
│       │   │   ├── Workspace.tsx
│       │   │   ├── Observations.tsx
│       │   │   ├── ReportBuilder.tsx
│       │   │   └── ReportView.tsx
│       │   ├── dept/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── Tasks.tsx
│       │   │   ├── TaskWizard.tsx
│       │   │   ├── Evidence.tsx
│       │   │   └── SelfAssessment.tsx
│       │   ├── vendor/
│       │   │   ├── Dashboard.tsx
│       │   │   ├── NewVendor.tsx
│       │   │   ├── VendorDetail.tsx
│       │   │   └── ExpiryTracker.tsx
│       │   ├── policy/
│       │   │   ├── Inbox.tsx
│       │   │   ├── PolicyReview.tsx
│       │   │   └── History.tsx
│       │   └── assessor/
│       │       ├── Dashboard.tsx
│       │       ├── ReportLibrary.tsx
│       │       └── Chat.tsx
│       │
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useNotifications.ts
│       │   ├── usePermission.ts        ← checks permission_key client-side
│       │   └── useAI.ts               ← wrapper for AI service calls
│       │
│       ├── store/
│       │   ├── authStore.ts            ← user, role, institution, JWT
│       │   ├── notificationStore.ts
│       │   └── uiStore.ts             ← sidebar open, modal state
│       │
│       ├── lib/
│       │   ├── api.ts                 ← axios instance, base URL, interceptors
│       │   ├── aiApi.ts               ← axios instance for AI service
│       │   └── utils.ts
│       │
│       └── types/
│           ├── auth.ts
│           ├── roles.ts
│           └── api.ts
│
└── backend/
    │
    ├── requirements.txt               ← shared install
    │
    ├── app/                           ← Main FastAPI (port 8000)
    │   ├── main.py
    │   ├── config.py                  ← pydantic-settings, reads .env
    │   ├── database.py                ← SQLAlchemy async engine + session
    │   ├── mongodb.py                 ← Motor async client for Atlas
    │   │
    │   ├── models/                    ← SQLAlchemy ORM (one file per block)
    │   │   ├── __init__.py
    │   │   ├── foundation.py          ← institutions, roles, permissions
    │   │   ├── users.py
    │   │   ├── departments.py
    │   │   ├── controls.py            ← control_assignments
    │   │   ├── assessments.py
    │   │   ├── mitigation.py
    │   │   ├── evidence.py
    │   │   ├── incidents.py
    │   │   ├── vendors.py
    │   │   ├── policies.py
    │   │   ├── audit.py
    │   │   ├── calendar.py
    │   │   ├── notifications.py
    │   │   └── logs.py
    │   │
    │   ├── schemas/                   ← Pydantic v2 (request + response per domain)
    │   │   ├── auth.py
    │   │   ├── users.py
    │   │   ├── departments.py
    │   │   ├── controls.py
    │   │   ├── assessments.py
    │   │   ├── evidence.py
    │   │   ├── incidents.py
    │   │   ├── vendors.py
    │   │   ├── policies.py
    │   │   ├── audit.py
    │   │   ├── notifications.py
    │   │   └── calendar.py
    │   │
    │   ├── routers/                   ← FastAPI routers, one per domain
    │   │   ├── auth.py
    │   │   ├── users.py
    │   │   ├── institutions.py
    │   │   ├── departments.py
    │   │   ├── controls.py
    │   │   ├── assessments.py
    │   │   ├── evidence.py
    │   │   ├── incidents.py
    │   │   ├── vendors.py
    │   │   ├── policies.py
    │   │   ├── audit.py
    │   │   ├── notifications.py
    │   │   └── calendar.py
    │   │
    │   ├── services/                  ← Business logic, no DB queries here
    │   │   ├── auth_service.py        ← JWT creation, refresh, password hash
    │   │   ├── rbac_service.py        ← permission checks, role assumption
    │   │   ├── notification_service.py ← create + fan-out notifications
    │   │   ├── calendar_service.py    ← auto-create calendar events
    │   │   ├── incident_service.py    ← CERT-In deadline calculation
    │   │   └── evidence_service.py    ← orchestrates storage + DB write
    │   │
    │   ├── core/
    │   │   ├── security.py            ← bcrypt, JWT encode/decode
    │   │   ├── permissions.py         ← require_permission() dependency
    │   │   ├── deps.py                ← get_current_user, get_db, get_mongo
    │   │   ├── exceptions.py          ← custom HTTPException subclasses
    │   │   └── audit.py               ← write_audit_log() utility
    │   │
    │   ├── storage/
    │   │   ├── __init__.py            ← exports upload_file(), get_file_url()
    │   │   ├── supabase_client.py     ← Supabase Storage upload/download
    │   │   └── local_fallback.py      ← writes to backend/uploads/ if no Supabase env
    │   │
    │   └── migrations/
    │       └── schema.sql             ← v2 schema + ai_conversations table
    │
    └── ai_service/                    ← AI FastAPI (port 8001)
        ├── main.py
        ├── config.py
        │
        ├── routers/
        │   ├── compliance.py          ← triage, regulatory change agent
        │   ├── security.py            ← cert_in_draft
        │   ├── audit.py               ← smart_sample, draft_observation
        │   ├── dept.py                ← translate_control, preflight_check
        │   ├── vendor.py              ← analyze_contract
        │   ├── policy.py              ← conflict_detect, executive_summary
        │   ├── assessor.py            ← conversational Q&A
        │   ├── digest.py              ← morning digest generator
        │   └── admin.py               ← anomaly detection, risk heatmap
        │
        ├── agents/
        │   ├── base.py                ← shared LangChain chain setup
        │   ├── compliance_agent.py
        │   ├── security_agent.py
        │   ├── audit_agent.py
        │   ├── vendor_agent.py
        │   ├── policy_agent.py
        │   └── assessor_agent.py
        │
        ├── rag/
        │   ├── loader.py              ← loads .md files, chunks at ## boundaries
        │   ├── vectorstore.py         ← FAISS build + persist + load
        │   ├── retriever.py           ← similarity search wrapper
        │   └── knowledge_base/        ← 6 framework .md files go here
        │       ├── dpdp_act_2023.md
        │       ├── cert_in_2022.md
        │       ├── iso_27001_2022.md
        │       ├── nist_csf_2.md
        │       ├── ugc_guidelines.md
        │       └── naac_criteria.md
        │
        ├── prompts/                   ← LangChain PromptTemplate files
        │   ├── cert_in_draft.py
        │   ├── gap_analysis.py
        │   ├── contract_analysis.py
        │   ├── policy_conflict.py
        │   ├── plain_english.py
        │   ├── preflight_check.py
        │   ├── morning_digest.py
        │   └── assessor_qa.py
        │
        └── utils/
            ├── context_builder.py     ← pulls summarized data from main app DB (no raw rows)
            └── token_counter.py       ← guards against context window overflow
```

---

## 4. AI SERVICE ARCHITECTURE

The AI service runs as a **separate FastAPI app on port 8001**. It never touches PostgreSQL or MongoDB directly — it receives structured summaries from the main app via internal API calls. This keeps raw data out of the LLM context.

### 4.1 Endpoints

| Method | Endpoint | Role | What It Does |
|---|---|---|---|
| POST | `/ai/compliance/triage` | Compliance Officer | Takes list of alerts → returns ranked top-10 with severity and recommended action |
| POST | `/ai/compliance/regulatory-change` | Compliance Officer | Takes raw regulation text → returns gap analysis vs existing controls |
| POST | `/ai/security/cert-in-draft` | IT Security | Takes incident record → returns formatted CERT-In report draft |
| POST | `/ai/audit/smart-sample` | Auditor | Takes evidence metadata list → returns prioritized sample set |
| POST | `/ai/audit/draft-observation` | Auditor | Takes control + evidence summary → drafts observation text |
| POST | `/ai/dept/translate-control` | Dept Reviewer | Takes control_id → returns plain English task description |
| POST | `/ai/dept/preflight-check` | Dept Reviewer | Takes file metadata + control requirement → returns pass/warn/fail |
| POST | `/ai/vendor/analyze-contract` | Vendor Reviewer | Takes contract text (extracted PDF) → returns missing DPDP clauses, risk findings |
| POST | `/ai/policy/conflict-detect` | Policy Approver | Takes new policy text + existing policies list → returns conflicts |
| POST | `/ai/policy/executive-summary` | Policy Approver | Takes policy text → returns one-page brief |
| POST | `/ai/assessor/chat` | Read-Only Assessor | Conversational Q&A with RAG over framework knowledge base |
| POST | `/ai/admin/anomaly-detect` | Super Admin | Takes access log summary → flags suspicious patterns |
| POST | `/ai/admin/risk-heatmap` | Institution Admin | Takes dept compliance summaries → returns top-5 predicted risks |
| POST | `/ai/digest/generate` | All roles | Takes role + user summary → returns personalized morning digest |

### 4.2 LangChain Setup

Each agent follows this pattern:

```python
# agents/base.py
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
# gpt-4o-mini: cheap, fast, good enough for all tasks except contract analysis
# gpt-4o: used only for contract analysis and policy conflict detection
```

### 4.3 RAG Pipeline

```
knowledge_base/*.md
        ↓
  loader.py  ← splits at ## headings, adds YAML frontmatter as metadata
        ↓
  FAISS vectorstore  ← built once on startup, persisted to disk
        ↓
  retriever.py  ← top-k similarity search (k=5 default)
        ↓
  agent prompt  ← retrieved chunks injected into context
        ↓
  OpenAI LLM  ← returns answer
```

**Knowledge base chunking rule:** Each `##` heading becomes one chunk. YAML frontmatter (framework name, section number, applicability) is added as metadata for filtered retrieval.

### 4.4 Data Safety Rule

The AI service never receives:
- Raw student records
- Raw incident logs with PII
- Raw vendor contact data

It receives:
- Structured summaries (counts, percentages, status enums)
- Control metadata (control_id, title, framework, status)
- Document text the user explicitly submits (regulation text, policy text, contract text)

This is enforced in `utils/context_builder.py` which is the only file allowed to query the main app.

---

## 5. SUPABASE STORAGE SETUP

### 5.1 Supabase Project Setup

1. Go to [supabase.com](https://supabase.com) → New Project
2. Name: `complysense-storage`, region: `ap-south-1` (Mumbai — closest to India)
3. Wait for project to provision (~2 min)

### 5.2 Create Storage Buckets

Go to **Storage** in left sidebar:

**Bucket 1: `evidence-documents`**
- Click "New bucket" → name: `evidence-documents`
- Toggle **Public**: OFF (private)
- Click Create

**Bucket 2: `audit-reports`**
- Name: `audit-reports`
- Toggle **Public**: OFF (private)
- Click Create

No RLS policies needed — the backend uses the `service_role` key which bypasses RLS entirely. Access control is handled by our own RBAC.

### 5.3 Get Credentials

Go to **Settings → API**:

```
SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...  ← use service_role key, NOT anon key
```

Add both to `.env`.

### 5.4 Storage Client (with local fallback)

```python
# backend/app/storage/__init__.py

import os
from .supabase_client import SupabaseStorage
from .local_fallback import LocalStorage

USE_SUPABASE = bool(os.getenv("SUPABASE_URL"))

storage = SupabaseStorage() if USE_SUPABASE else LocalStorage()

async def upload_file(bucket: str, path: str, file_bytes: bytes, mime_type: str) -> str:
    return await storage.upload(bucket, path, file_bytes, mime_type)

async def get_signed_url(bucket: str, path: str, expires_in: int = 3600) -> str:
    return await storage.signed_url(bucket, path, expires_in)
```

```python
# backend/app/storage/supabase_client.py

from supabase import create_client
import os

class SupabaseStorage:
    def __init__(self):
        self.client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )

    async def upload(self, bucket: str, path: str, file_bytes: bytes, mime_type: str) -> str:
        self.client.storage.from_(bucket).upload(path, file_bytes, {"content-type": mime_type})
        return path  # store this path in evidence_documents.file_path

    async def signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        res = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
        return res["signedURL"]
```

```python
# backend/app/storage/local_fallback.py

import os, aiofiles
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class LocalStorage:
    async def upload(self, bucket: str, path: str, file_bytes: bytes, mime_type: str) -> str:
        full_path = UPLOAD_DIR / bucket / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_bytes)
        return str(full_path)

    async def signed_url(self, bucket: str, path: str, expires_in: int = 3600) -> str:
        # Local: return a direct serve URL (add a static files mount in main.py)
        return f"/uploads/{bucket}/{path}"
```

**File path convention in DB:**
```
evidence-documents/{institution_id}/{control_id}/{uuid}_{original_filename}
audit-reports/{institution_id}/{assessment_id}/{uuid}_report.pdf
```

---

## 6. ROOT RUNNER SETUP

### 6.1 Root `package.json`

```json
{
  "name": "complysense",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "concurrently -n frontend,backend,ai -c cyan,green,yellow \"npm run dev:frontend\" \"npm run dev:backend\" \"npm run dev:ai\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && uvicorn app.main:app --reload --port 8000",
    "dev:ai": "cd backend && uvicorn ai_service.main:app --reload --port 8001",
    "install:all": "npm install && cd frontend && npm install",
    "install:python": "cd backend && pip install -r requirements.txt"
  },
  "devDependencies": {
    "concurrently": "^8.2.0"
  }
}
```

Run `npm install` at root once, then `npm run dev` every time.

---

## 7. DEPLOYMENT FILES

### 7.1 `render.yaml`

```yaml
services:
  - type: web
    name: complysense-api
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: MONGODB_URI
        sync: false
      - key: SECRET_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false

  - type: web
    name: complysense-ai
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn ai_service.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: MAIN_API_URL
        sync: false  # internal URL of complysense-api
```

### 7.2 `vercel.json`

```json
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }],
  "env": {
    "VITE_API_URL": "@complysense_api_url",
    "VITE_AI_URL": "@complysense_ai_url"
  }
}
```

---

## 8. ENV FILE TEMPLATE

```bash
# .env.example — copy to .env and fill in

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host/complysense

# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/complysense

# JWT
SECRET_KEY=your-256-bit-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Supabase Storage (leave blank to use local fallback)
SUPABASE_URL=
SUPABASE_SERVICE_KEY=

# OpenAI
OPENAI_API_KEY=

# Internal service URL (used by ai_service to call main app)
MAIN_API_URL=http://localhost:8000

# Frontend (Vite env vars — prefix VITE_)
VITE_API_URL=http://localhost:8000
VITE_AI_URL=http://localhost:8001
```

---

## 9. 15-DAY BUILD PLAN

Scope is realistic. AI features are second-week work. Core RBAC + evidence workflow comes first.

| Day | Focus | Deliverable |
|---|---|---|
| **1** | Setup | Repo scaffold, root runner, schema migration, Neon + MongoDB Atlas + Supabase connected, .env wired |
| **2** | Auth | JWT auth system, RBAC middleware, login/logout/refresh, ProtectedRoute on frontend |
| **3** | Institution Admin | User CRUD, Department CRUD, role assignment. Foundation for all other roles |
| **4** | Compliance Officer — Controls | Control assignments CRUD, Kanban board, framework filter |
| **5** | Evidence System | Upload (Supabase + fallback), approval queue, status flow |
| **6** | IT Security — Incidents | Incident log, 6hr CERT-In countdown component, DPDP toggle |
| **7** | Assessments + Gaps | Assessment runner, compliance_results write, gap matrix |
| **8** | AI Service Foundation | LangChain setup, FAISS RAG loader, vectorstore build from 6 framework docs |
| **9** | AI — Security + Compliance | CERT-In draft agent, compliance triage agent |
| **10** | Auditor + Dept Reviewer | Audit workspace (read-only), observation panel, Task Wizard, pre-flight check |
| **11** | Vendor Reviewer | Vendor register, risk assessment form, contract analyzer AI |
| **12** | Policy Approver | Policy inbox, diff viewer component, conflict detector AI |
| **13** | Read-Only Assessor | Executive dashboard charts, Q&A chatbot (RAG) |
| **14** | Notifications + Calendar | Fan-out notification writes, compliance calendar view |
| **15** | Polish + Deploy | render.yaml deploy, vercel.json deploy, Super Admin pages, bug fixes |

---

## 10. WHAT WE ARE NOT BUILDING (MVP SCOPE CUT)

To hit the deadline without cutting core features, these are explicitly out:

- Morning digest email (AI generates it, but email sending is not wired — shown as in-app notification only)
- Real-time WebSocket notifications (polling every 30s instead)
- Report Builder drag-and-drop (Auditor gets a generate button, not a drag interface)
- Vulnerability register (IT Security has incident management, vulnerability tracking skipped)
- Org-chart HR sync (Institution Admin creates users manually)
- Dark web breach watch for vendors (Contract Analyzer only)
- Role assumption sessions UI (schema supports it, UI deferred)

These are real features documented in the blueprint but not buildable in 15 days without cutting core flows.

---

## OPEN ITEMS

| # | Item | Status |
|---|---|---|
| 1 | 6 framework document exact names (knowledge base) | Pending from Garv |
| 2 | MongoDB control library structure (field schema for one control document) | To define before Day 8 |
| 3 | NAAC criteria — confirm it's included as a framework | Pending |

---

*Document maintained by Garv Jain. Update SESSION SUMMARY block at the top after every work session.*