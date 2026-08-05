# ComplySense — Codebase Technical Presentation Audit

This audit provides a high-level, presentation-ready overview of the ComplySense technical architecture, engineering decisions, and core implementations. It focuses on the underlying systems, flows, and technical highlights of the codebase, omitting development timelines and bug/TODO tracking.

---

## 1. Project Overview

ComplySense is an enterprise-grade Governance, Risk, and Compliance (GRC) SaaS platform designed specifically to meet compliance, risk management, and security audit requirements for higher-education institutions (such as Indian universities). 

* **Primary Problem Solved:** Streamlining complex compliance audits, policy orchestration, vendor risk verification, and security incident response against multiple overlapping regulatory frameworks (including the Digital Personal Data Protection Act (DPDP), CERT-In security directives, UGC guidelines, NAAC accreditation criteria, ISO 27001, and NIST CSF).
* **Target Users:** Organization administrators, compliance officers, IT security officers, vendor risk reviewers, policy sign-off authorities, department reviewers, and external regulatory auditors.

---

## 2. System Architecture

ComplySense uses a modular, multi-tier microservices architecture consisting of a decoupled React single-page application (SPA), a main FastAPI transactional backend, an asynchronous AI reasoning service, and a dual-database persistence layer.

```
       +---------------------------------------------+
       |                  Frontend                   |
       |             React 19 / Vite SPA             |
       +-----------------------+---------------------+
                               |
                        HTTPS (REST API)
                               |
                               v
       +---------------------------------------------+
       |                Main Backend                 |
       |             FastAPI Server (8000)           |
       +-------+---------------------+-------+-------+
               |                     |       |
         SQL / Asyncpg          Motor Driver | HTTP (Proxy)
               |                     |       |
               v                     v       v
       +---------------+     +---------------+     +---------------------------+
       |  PostgreSQL   |     | MongoDB Atlas |     |        AI Service         |
       |  Relational   |     |  Document DB  |     |   FastAPI Server (8001)   |
       +---------------+     +---------------+     +-------------+-------------+
                                                                 |
                                                          Local Embeddings & RAG
                                                                 |
                                                                 v
                                                           [ BAAI/bge-m3 ]
                                                           [ FAISS / BM25 ]
                                                           [ Gemini 2.5 ]
```

### Module Interactions & Data Flow
1. **Frontend ↔ Main Backend:** The React frontend authenticates via JSON Web Tokens (JWT) and consumes REST APIs from the main FastAPI backend (e.g., executing transactions, uploading evidence, updating incident registers).
2. **Main Backend ↔ Databases:** The Main Backend persists transactional states, user profiles, audit logs, and workflow metadata in **PostgreSQL** using SQLAlchemy and `asyncpg`. It reads the master control checklists, framework descriptions, and requirements from **MongoDB Atlas** using the asynchronous `motor` driver.
3. **Main Backend ↔ AI Service:** When an actor triggers an AI feature (e.g., drafting a CERT-In report, evaluating a policy conflict), the Main Backend proxies the request via an HTTP helper in [proxy.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/app/routers/ai/proxy.py). It gathers contextual metadata from PostgreSQL and passes structured summaries (not raw database rows) to the AI service, protecting PII.
4. **AI Service ↔ Storage & Retrieval:** The AI service (running on port 8001) coordinates hybrid RAG retrieval from a local FAISS vector index and a BM25 keyword store, calling Google's `gemini-2.5-flash` LLM to generate context-grounded compliance answers, which are validated by downstream safety gates before returning.

---

## 3. Multi-Tenant Architecture

ComplySense is designed as a secure multi-tenant SaaS application that guarantees tenant isolation, fine-grained access control, and audited role context switching.

* **Tenant Isolation Strategy:** The database uses logical tenant isolation. Every data table in the database schema (defined in [schema.sql](file:///c:/Users/hp/Desktop/complysense-clean/schema.sql)), from `users` and `departments` to `evidence_documents` and `incidents`, contains an `institution_id` foreign key. Query builders strictly filter select, update, and delete actions by the user's authenticated `institution_id` retrieved from the JWT session.
* **Seeded User Roles:** The system enforces 9 fixed organizational and administrative roles, which are seeded in [schema.sql](file:///c:/Users/hp/Desktop/complysense-clean/schema.sql#L692-L701):
  * *Administrative:* `Super Admin` (global god mode) and `Institution Admin` (tenant administrator).
  * *Compliance & Risk:* `Compliance Officer` (daily operator) and `Auditor` (external reviewer).
  * *Operations:* `IT Security Officer`, `Department Reviewer`, `Vendor Reviewer`, `Policy Approver`, and `Read-Only Assessor`.
* **Authentication and Session Lifecycle:** Realized in [auth_service.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/app/services/auth_service.py):
  * Users authenticate via credentials, generating a JWT access token and a refresh token.
  * Sessions are stored in the `user_sessions` database table, enabling token rotation and immediate global session revocation.
  * A brute-force lockout policy increments login failure counters in the `users` table, temporarily blocking account access for 5 minutes after 3 consecutive failures.
* **Role Assumption / Impersonation Flow:** To allow privileged admins to test and verify views, the platform supports temporary role assumption:
  * Allowed transitions are governed by the `allowed_role_transitions` table (e.g., an `Institution Admin` can assume a `Dept Reviewer` role, but not vice versa).
  * The transition writes an active record to `role_assumption_sessions` for audit logs and updates the session context.
  * FastAPI's auth dependency [deps.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/app/core/deps.py#L23) intercepts the request, reads the active assumed role ID, loads permissions for the assumed role, and populates a dynamic `UserContext`. Exiting the assumption resets the active ID and generates a clean JWT.

---

## 4. AI Architecture

The AI module is built as an asynchronous microservice decoupled from transactional databases. It runs a custom RAG (Retrieval-Augmented Generation) pipeline designed for fast retrieval, framework compliance, and guardrailed generation.

```
                  +-----------------------------------------+
                  |               User Query                |
                  +--------------------+--------------------+
                                       |
                                       v
                  +-----------------------------------------+
                  |         Query Classification            |
                  |          [ QueryClassifier ]            |
                  +--------------------+--------------------+
                                       |
                                       v
                  +--------------------+--------------------+
                  |       Parallel Retrieval Pipeline       |
                  |  +-------------------+---------------+  |
                  |  |  Dense Search     | Sparse Search |  |
                  |  |  (FAISS + BGE-M3) |    (BM25)     |  |
                  |  +---------+---------+-------+-------+  |
                  +------------|-----------------|----------+
                               |                 |
                               +--------+--------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |         Role & Tenant Filtering         |
                  |     (Enforces Permitted Frameworks)     |
                  +---------------------+-------------------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |      Reciprocal Rank Fusion (RRF)       |
                  |        [ Rank Merging: k=60 ]           |
                  +---------------------+-------------------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |     Cross-Reference Linked Injection    |
                  |      (Injects up to 2 linked sections)  |
                  +---------------------+-------------------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |       Input Guardrails & Sanitizer       |
                  |      (Block injections, wrap XML tags)  |
                  +---------------------+-------------------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |          Gemini 2.5 Inference           |
                  +---------------------+-------------------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |         Output Validation Gate          |
                  |      (Detects jailbreaks & citations)   |
                  +---------------------+-------------------+
                                        |
                                        v
                  +---------------------+-------------------+
                  |          Structured Output              |
                  +-----------------------------------------+
```

### Decoupled Hybrid RAG Pipeline
* **Dual Index Architecture:** Search index generation is orchestrated by [index_builder.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/indexing/index_builder.py). During startup, it checks disk persistence and builds indexes if missing. Dense embeddings are generated locally using the `BAAI/bge-m3` model via the [EmbeddingsGenerator](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/indexing/embeddings.py) singleton.
  * *Dense Retrieval:* Handled via native [FAISSIndexStore](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/indexing/faiss_store.py). Chunks are normalized under L2 norm, and search uses a flat Inner Product index (`IndexFlatIP`), guaranteeing that Inner Product results reflect true cosine similarity scores.
  * *Sparse Retrieval:* Handled via [BM25IndexStore](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/indexing/bm25_store.py), capturing exact keywords and standard identifiers (e.g. "Section 43A", "ISO-A8").
* **RRF Rank Fusion:** Dense and sparse retrieval outputs (20 candidates each) are combined in [rrf.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/retrieval/rrf.py) using the Reciprocal Rank Fusion formula:
  $$\text{Score}(d) = \sum_{m \in M} \frac{1}{k + \text{rank}_m(d)}$$
  This merges semantic intent and key term matching into a single ranked result list.
* **Role-Gated & Tenant-Aware Filtering:** Implemented in [hybrid_retriever.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/retrieval/hybrid_retriever.py#L109-L129):
  * *Tenant Isolation:* User-uploaded documents (ingested from MongoDB) are filtered on retrieval to match the user's `institution_id`.
  * *Framework Gating:* Global frameworks are filtered against the user's role framework matrix (e.g., a `Dept Reviewer` can retrieve from UGC and NAAC, while an `IT Security Officer` can retrieve from CERT-In and NIST).
  * *Override Rules:* Node-level `applies_to` metadata rules override role settings for specific sections.
* **Cross-Reference Section Injection:** To prevent loss of context when documents cite other sections, [cross_reference.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/retrieval/cross_reference.py) inspects the primary retrieved chunks, extracts explicitly linked section IDs, retrieves the target chunks, and injects up to 2 referenced chunks as secondary context.
* **Jailbreak and Sanitization Guardrails:**
  * *Input Sanitizer:* The [InputSanitizer](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/security/sanitizer.py) checks query text against prompt-injection keywords and wraps external documents in XML delimiters (`<external_content>`).
  * *Output Validator:* The [OutputValidator](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/security/response_validator.py) checks LLM output for jailbreak patterns and verifies that every framework mentioned in the output is backed by a retrieved context chunk, neutralizing citation hallucinations.

---

## 5. Knowledge Base

The system's RAG knowledge base represents standard guidelines structured as local files.

* **Folder Hierarchy:** Knowledge documents are stored within structured markdown folders under the `knowledge-base` folder, mapped by framework domains:
  ```
  ai_service/knowledge-base/
  ├── cert-in/       # CERT-In Directions 2022
  ├── dpdp/          # DPDP Act 2023
  ├── iso27001/      # ISO 27001:2022 Standard
  ├── naac/          # NAAC Criteria 4 & 6
  ├── nist/          # NIST CSF 2.0
  └── ugc/           # UGC Guidelines
  ```
* **Frontmatter & Metadata Strategy:** Standard YAML frontmatter defines framework names, document types, and global applicability. Heading nodes carry inline markdown comment metadata (e.g., `<!-- meta: section_id="4" applies_to="it_security" keywords="audit,log" -->`), allowing the parser to associate properties to specific clauses.
* **Atomic Obligation Chunking:** Standard recursive text splitters break compliance requirements mid-sentence, destroying conditional clauses. ComplySense solves this via [atomic_chunker.py](file:///c:/Users/hp/Desktop/complysense-clean/backend/ai_service/rag/indexing/atomic_chunker.py):
  * Parses markdown into a heading tree.
  * Uses regex matches to catch regulatory obligation triggers (e.g., `shall not`, `must not`, `except`, `unless`, `notwithstanding`, `provided that`).
  * If a paragraph is flagged as an atomic obligation or a table, it is marked `keep_whole` and kept intact up to 800 tokens, bypassing sentence splits to preserve complete compliance context.
  * Normal chunks are bounded between 350 and 600 tokens with a 100-token overlap.

---

## 6. Backend REST API

The backend services are built using **FastAPI**, leveraging asynchronous event loops for performance.

* **API Routing and RBAC Dependency:** Endpoints are decoupled by domains (auth, users, departments, controls, audits, incidents, vendors, policies). Role protection is enforced via dynamic FastAPI dependencies. Declaring `Depends(require_permission(PermissionKey.MANAGE_INCIDENTS))` automatically checks user permissions at the API gate, raising an HTTP 403 error on unauthorized access.
* **Database Session Lifecycle:** Transactional operations use SQLAlchemy Async Engine with the `asyncpg` driver, injecting scoped async database sessions into router endpoints.
* **Background Tasks:** Time-consuming workloads (such as generating PDF risk summaries, running vector indexing, or distributing multi-user notifications) are executed asynchronously outside the request-response thread using FastAPI's native `BackgroundTasks`.
* **Security Implementations:**
  * Strict CORS policies limit access to validated origin endpoints.
  * Input sanitization prevents SQL injection (using parameterized query generation) and prompt injection.
  * Token-based authentication with rotation guarantees session security.

---

## 7. Databases

ComplySense uses a hybrid persistence design, matching relational transactional requirements and schema-less flexibility to their ideal database technologies.

| Database | Technology | Primary Role | Why Chosen |
|---|---|---|---|
| **Transactional DB** | PostgreSQL (Neon / Local) | Core Entities, Relationships, Workflows, Session Tracking, Audit Trails. | Enforces strict schema validations, foreign key constraints (protecting relational integrity across 28 tables), atomic transaction guarantees, and standard indexed queries. |
| **Document DB** | MongoDB Atlas | Master Control Library, framework mapping templates, evidence checklists, raw file text extraction. | Compliance frameworks and checklist structures change depending on the standard (e.g. ISO uses Annex controls, UGC uses criteria metrics). A document store allows rich nested schemas without migrations. |

### PostgreSQL Schema Highlights (28 Tables)
* **platform_foundation:** `institutions`, `roles`, `permissions`, `role_permissions`
* **user_management:** `users`, `password_reset_tokens`, `user_sessions`, `allowed_role_transitions`, `role_assumption_sessions`
* **workflows:** `departments`, `control_assignments`, `assessments`, `assessment_responses`, `compliance_results`, `compliance_gaps`, `mitigation_tasks`, `evidence_documents`, `incidents`, `incident_timeline`, `vendors`, `vendor_risk_assessments`, `generated_policies`, `audit_observations`, `audit_reports`, `compliance_calendar`
* **system:** `notifications`, `audit_logs`, `ai_conversations`

---

## 8. Frontend Engineering

The frontend is a custom-designed single-page application built on **React 19**, **Vite 6**, and **Zustand 5** for state management, bypassing external CSS frameworks in favor of vanilla CSS to implement a high-performance design system.

* **State Management Architecture:** Decoupled Zustand stores manage global states:
  * [authStore.ts](file:///c:/Users/hp/Desktop/complysense-clean/frontend/src/store/authStore.ts): Persists access tokens, active session IDs, user roles, permission sets, and active role assumption profiles.
  * `notificationStore`: Syncs unread events and tasks.
  * `themeStore`: Coordinates dark and light themes using CSS variables.
* **Centralized Navigation:** Navigation links, badge counters, and operational configurations are resolved inside [Sidebar.tsx](file:///c:/Users/hp/Desktop/complysense-clean/frontend/src/components/shared/Sidebar.tsx) by evaluating the active role from the auth store.
* **Core User Workflows:**
  * *IT Security Officer Command Center:* Tracks incidents with a live 6-hour countdown timer calculated from `detected_at` to enforce CERT-In reporting windows, complete with an AI one-click report generator.
  * *Compliance Officer Task Manager:* Kanban-style board tracking control lifecycle status (not started, in progress, submitted, compliant) with framework filtering.
  * *Policy Approver Interface:* A split-screen policy review interface displaying live diff comparisons between policy versions, supported by AI conflict detection summaries.

---

## 9. Technical Challenges & Engineering Tradeoffs

* **Index Load Penalty Mitigations:** During initial iterations, instantiating the hybrid retriever triggered reloading FAISS and BM25 index files from disk, causing a 2+ second delay on every AI prompt. The service resolved this by moving index loading to the FastAPI `lifespan` context. Index stores are loaded once into memory on startup and managed as hot-loaded singletons.
* **Dual Database Coordination:** Linking SQL assignments to MongoDB control templates could cause relational separation. The system addresses this by using static, canonical string IDs (`control_id`) inside PostgreSQL tables, which reference the primary keys in MongoDB Atlas collections.
* **Decoupled AI context limits:** The AI service does not connect to PostgreSQL. Instead, the main API serializes transactional data into structured XML context strings, passing them as payloads. To prevent context window overflow when processing large compliance documents, the AI service uses a tokenizer utility to track input length and enforces token caps.

---

## 10. Technologies Used

* **Frontend:** React 19, Vite 6, TypeScript, Zustand 5, Custom Vanilla CSS, Lucide React (Icons).
* **Backend:** FastAPI, Python, SQLAlchemy, Uvicorn, HTTPX (microservice calls).
* **AI & RAG:** LangChain-Google-GenAI, ChatGoogleGenerativeAI, Google Gemini 2.5 Flash, BAAI/bge-m3 (Embeddings), FAISS (Dense Store), Rank-BM25 (Sparse Store), NumPy, Python Pickle.
* **Databases:** PostgreSQL (via Neon or Local), pg8000/asyncpg, MongoDB Atlas, Motor (Async MongoDB driver).
* **Authentication:** JWT (Jose), bcrypt (password hashing), HTTPBearer.
* **Infrastructure:** Render (API and AI service hosting), Vercel (Frontend deployment), Supabase Storage (Evidence and PDF storage).

---

## 11. Presentation Highlights

1. **Dual-Database Architecture:** Emphasize the separation of concerns: structured relational workflows in PostgreSQL and unstructured compliance framework templates in MongoDB Atlas.
2. **Hybrid RAG Retrieval Engine:** Highlight the implementation of dense semantic search (FAISS + BGE-M3) and sparse keyword retrieval (BM25) fused via Reciprocal Rank Fusion (RRF).
3. **Decoupled Microservice Design:** The transactional backend is completely separate from the AI reasoning engine. Communications happen over secure HTTP proxy channels, ensuring data safety.
4. **Atomic Obligation Chunker:** Explain how standard sentence splitting breaks conditional law clauses. ComplySense solves this by preserving regulatory clauses containing modal verbs (e.g. *shall*, *unless*).
5. **Secure Multi-Tenancy:** Describe how logical separation is enforced via `institution_id` across 28 PostgreSQL tables and verified at the API routing layer.
6. **Audited Role Assumption:** Showcase how administrators can impersonate lower roles to preview pages. Emphasize that all role changes are fully monitored and written to the immutable `audit_logs` table.
7. **Jailbreak and Hallucination Gates:** Discuss the dual guardrail design: sanitizing input queries and checking output response citations against retrieved chunks to block hallucinations.
8. **Compliance Calendar Engine:** The calendar acts as a central scheduler, automatically converting control deadlines, contract expiries, and scheduled assessments into event rows.
9. **Incident Clock Manager:** The 6-hour CERT-In countdown dashboard provides real-time alerts, displaying an automated template drafter to meet regulatory deadlines.
10. **Zustand State Stores:** Highlight how Zustands lightweight stores unify auth, notifications, and visual styling, keeping page components clean and reactive.
11. **CSS Variable Design System:** Emphasize that ComplySense implements a bespoke glassmorphic UI using pure Vanilla CSS, optimized for rapid rendering and custom dark/light theme switching.

---

## 12. Diagrams Needed for Presentation

* **Overall System Architecture:** A diagram illustrating the user accessing the React SPA, communicating with the FastAPI backend, and showing database calls alongside proxy routing to the AI microservice.
* **Multi-Tenant Isolation Flow:** A diagram showing how a user request carries a JWT, resolving to a `UserContext` on the backend, which appends `WHERE institution_id = X` filters to PostgreSQL database transactions.
* **RAG Pipeline Flowchart:** A step-by-step flowchart tracking a user query as it gets classified, retrieved in parallel via FAISS and BM25, merged using RRF, enriched via cross-references, and validated for citations after Gemini inference.
* **Role Assumption Sequence:** A sequence diagram tracking the Admin requesting role assumption, the backend validating transitions and updating the session, and returning a fresh JWT to re-hydrate the frontend.
* **Incident Lifecycle and CERT-In Timeline:** A timeline diagram showing an incident being logged, triggering the 6-hour deadline, generating the CERT-In draft, and updating the database.
