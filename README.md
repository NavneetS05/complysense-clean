# ComplySense — AI-Powered GRC Platform

ComplySense is a premium, enterprise-grade Governance, Risk, and Compliance (GRC) platform designed to streamline compliance management, technical controls monitoring, audit processes, and policy orchestration. Supported by a dual-backend architecture, it combines standard CRUD features with AI-powered agents for automated triaging, document summarization, incident reporting (CERT-In), and semantic search.

---

## 🚀 Key Features

* **Fine-Grained Role-Based Access Control (RBAC):** Supports 9 distinct organizational and administrative roles with distinct dashboards, custom navigation menus, and specialized workflows:
  * *Administrative:* Super Admin, Institution Admin
  * *Compliance & Risk:* Compliance Officer, Auditor, Read-Only Assessor
  * *Operations:* IT Security Officer, Department Reviewer, Vendor Reviewer, Policy Approver
* **Role Assumption / Impersonation:** Privileged administrative accounts can temporarily swap active context to preview views and permissions of standard roles. Fully monitored and audited.
* **Brute-Force Account Protection:** Standard API-enforced and frontend-synced lockout mechanism that restricts logins after 3 consecutive failures, with an active countdown block timer.
* **RAG & Agentic AI Capabilities:** Powered by LangChain, OpenAI, and a FAISS semantic index for AI-supported regulatory changes triage, automated security incident report drafts (CERT-In template), and semantic Q&A.
* **State-of-the-Art Interface:** Designed with curated dark/light palettes, glassmorphism, responsive sidebar layout, real-time unread/pending notification counters, and modern micro-animations.

---

## 🛠️ Technology Stack

### Frontend
* **Core:** React 19 (TypeScript), Vite 6
* **Routing & Guards:** React Router 7 with role-locked declarative route wrappers
* **State Management:** Zustand 5 for lightweight reactive stores (Authentication, Notifications)
* **Styling:** Custom Vanilla CSS design system (`styles.css`) for fine-grained glassmorphic aesthetics, fluid transitions, and typography

### Main API (Backend)
* **Framework:** FastAPI
* **Relational DB:** PostgreSQL (via Neon or local) with SQLAlchemy Async IO and Asyncpg
* **Document DB:** MongoDB (via Atlas or local) with Motor for control library storage and schema-less data
* **Storage:** Supabase Storage (knowledge-base file assets bucket)

### AI Service (Backend)
* **Framework:** FastAPI
* **Orchestration:** LangChain & LangChain-OpenAI
* **Vector Store:** FAISS for local CPU-based semantic retrieval

---

## 📂 Project Directory Structure

```text
complysense-clean/
├── package.json                   # Root workspace scripts (run frontend & backend concurrently)
├── schema.sql                     # PostgreSQL DDL schema definition (28 tables)
├── docs/                          # Specifications and logs
│   ├── design-review.md           # Living Architectural Decision Log (ADL)
│   └── masterplan.md              # Global system implementation plan
├── backend/                       # Python Backends
│   ├── requirements.txt           # Python dependency specifications
│   ├── app/                       # Main FastAPI REST API
│   │   ├── main.py                # Server entry point
│   │   ├── config.py              # Environment configuration loader
│   │   ├── database.py            # PostgreSQL connection pool
│   │   ├── routers/               # API route definitions (auth, users, audits, etc.)
│   │   ├── repositories/          # Data access layer (SQLAlchemy + Motor)
│   │   └── services/              # Domain logic & transactional workflows
│   └── ai_service/                # FastAPI AI service wrapper
│       ├── main.py                # RAG & agent backend entry point
│       ├── rag/                   # FAISS indexing & retrieval logic
│       └── routers/               # AI endpoint handlers
└── frontend/                      # React SPA Workspace
    ├── package.json               # Frontend dependencies & Vite scripts
    ├── tsconfig.json              # TypeScript compilation setup
    ├── src/
    │   ├── main.tsx               # App mounting point
    │   ├── App.tsx                # Context providers & router registration
    │   ├── styles.css             # Main styling system (tokens, components, themes)
    │   ├── components/            # Shared layouts, notifications, and navigation
    │   │   └── shared/
    │   │       ├── Sidebar.tsx    # Role-aware nav menus & dynamic state badges
    │   │       ├── Topbar.tsx     # Session banner & role assumption toggle
    │   │       └── Toast.tsx      # Global notification banners
    │   ├── layouts/               # Dashboard & Auth layout shells
    │   ├── pages/                 # Routing pages group by organizational role
    │   ├── store/                 # Zustand state managers (auth, notifications)
    │   └── routes/                # Private & public route guard mappings
```

---

## ⚙️ Environment Configuration

Copy the root environment example to configure both backend and frontend targets:

```bash
cp .env.example .env
```

Ensure the following variables are filled in:
1. `DATABASE_URL`: Asynchronous PostgreSQL connection string (`postgresql+asyncpg://...`)
2. `MONGODB_URI`: MongoDB connection string
3. `SUPABASE_URL` / `SUPABASE_SERVICE_KEY`: Credentials for knowledge storage
4. `SECRET_KEY`: Secret string used to sign session cookies and JWTs
5. `OPENAI_API_KEY`: API key for GPT models utilized by LangChain

---

## 🏃 Run & Installation

### 1. Root & Frontend Installation
Install the Node.js packages for the workspace runner and the React SPA:

```bash
npm run install:all
```

### 2. Python Backend Setup
Install Python dependencies for both the Main API and the AI service:

```bash
npm run install:python
```

### 3. Database Initialization
Prepare the target PostgreSQL database and run the schema initialization:

```bash
psql -h <host> -U <user> -d <db_name> -f schema.sql
```

### 4. Running the Platform
Start the frontend dev server, Main FastAPI backend, and AI service concurrently with a single command from the root directory:

```bash
npm run dev
```

* **Frontend Dashboard:** [http://localhost:5173](http://localhost:5173)
* **Main API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **AI Service Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)

---

## 📘 Development Standards & Guidelines

* **Design Review & Log:** All structural decisions, database migrations, security changes, and custom endpoints must be documented inside [design-review.md](file:///c:/Users/hp/Desktop/complysense-clean/docs/design-review.md). Refer to this log to examine past modifications.
* **CSS tokens:** Do not inject inline styles or external design libraries. Utilize the custom design system in `styles.css`.
* **DRY Navigation:** Do not define hardcoded nav arrays inside route configuration files. All route options are centrally resolved based on user context in `Sidebar.tsx`.
