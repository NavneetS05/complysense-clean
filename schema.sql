-- Use: PostgreSQL database schema definition including institutions, users, roles, and compliance tables.

/*
===============================================================================
 COMPLYSENSE — REDESIGNED POSTGRESQL DATABASE SCHEMA
===============================================================================

PROJECT       : ComplySense — AI-Enabled GRC SaaS for Indian Universities
TIMELINE      : 20–30 Day Internship Build
DESIGNER      : Garv Jain
VERSION       : 2.0

DESIGN PHILOSOPHY:
- Multi-tenant SaaS with strict institution isolation
- Fixed static RBAC (9 roles, no dynamic role creation)
- Audit-first architecture (everything traceable)
- Workflow-centric (every object has a lifecycle status)
- Realistic for 20-30 day MVP scope
- Every feature discussed (roles, flows, pages) has a table

ROLES SUPPORTED:
  Super Admin         → Developer/platform god mode
  Institution Admin   → Org-wide admin
  Compliance Officer  → Daily operator, core user
  IT Security Officer → Technical controls + incidents
  Auditor             → Read + comment, audit reports
  Department Reviewer → Dept-level tasks + evidence
  Vendor Reviewer     → Vendor register + risk
  Policy Approver     → Policy sign-off
  Read-Only Assessor  → Pure observer

===============================================================================
*/

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


/*
===============================================================================
 BLOCK 1: PLATFORM FOUNDATION
 Tables: institutions, roles, permissions, role_permissions
===============================================================================
*/

-- INSTITUTIONS
-- One row per university/college tenant.
-- All business data is isolated by institution_id.

CREATE TABLE institutions (
    institution_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_name    VARCHAR(255) NOT NULL,
    institution_type    VARCHAR(100),           -- University / College / Institute
    email               VARCHAR(255),
    phone               VARCHAR(15),
    address             TEXT,
    city                VARCHAR(100),
    state               VARCHAR(100),
    country             VARCHAR(100) DEFAULT 'India',
    staff_count         INTEGER,
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_institutions_name ON institutions(institution_name);


-- ROLES
-- Fixed static roles. Never created by institution users.
-- Seeded at deployment.

CREATE TABLE roles (
    role_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_name   VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- PERMISSIONS
-- Permission key catalog. Seeded by developers.
-- Examples: view_controls, upload_evidence, approve_policy, manage_users

CREATE TABLE permissions (
    permission_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    permission_key  VARCHAR(100) UNIQUE NOT NULL,
    description     TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ROLE PERMISSIONS
-- Maps which permissions belong to which role.
-- Checked server-side on every API call.

CREATE TABLE role_permissions (
    role_permission_id  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id             UUID NOT NULL REFERENCES roles(role_id) ON DELETE CASCADE,
    permission_id       UUID NOT NULL REFERENCES permissions(permission_id) ON DELETE CASCADE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);


/*
===============================================================================
 BLOCK 2: USERS, SESSIONS, ROLE ASSUMPTION
 Tables: users, password_reset_tokens, user_sessions,
         allowed_role_transitions, role_assumption_sessions
===============================================================================
*/

-- USERS
-- One user belongs to one institution with one primary role.

CREATE TABLE users (
    user_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(institution_id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES roles(role_id),
    full_name       VARCHAR(255) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    phone           VARCHAR(15),
    designation     VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    failed_login_attempts INTEGER DEFAULT 0,
    blocked_until   TIMESTAMP,
    last_login      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_institution ON users(institution_id);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_email_lower ON users(lower(email));


-- PASSWORD RESET TOKENS

CREATE TABLE password_reset_tokens (
    token_id    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token       TEXT NOT NULL,
    expires_at  TIMESTAMP NOT NULL,
    used        BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- USER SESSIONS
-- Tracks active login sessions and current operational role context.

CREATE TABLE user_sessions (
    session_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    active_role_id  UUID REFERENCES roles(role_id),
    user_agent      TEXT,
    ip_address      VARCHAR(100),
    expires_at      TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ALLOWED ROLE TRANSITIONS
-- Defines which roles can assume which other roles.
-- Prevents privilege escalation.

CREATE TABLE allowed_role_transitions (
    transition_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_role_id    UUID NOT NULL REFERENCES roles(role_id),
    to_role_id      UUID NOT NULL REFERENCES roles(role_id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_role_id, to_role_id)
);


-- ROLE ASSUMPTION SESSIONS
-- Tracks when a user temporarily operates under a different role.
-- Always stores original user identity for audit.

CREATE TABLE role_assumption_sessions (
    role_session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(user_id),
    institution_id  UUID NOT NULL REFERENCES institutions(institution_id),
    from_role_id    UUID NOT NULL REFERENCES roles(role_id),
    to_role_id      UUID NOT NULL REFERENCES roles(role_id),
    reason          TEXT,
    started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP,
    ended_at        TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE
);


/*
===============================================================================
 BLOCK 3: DEPARTMENTS
 New in v2. Required for Department Reviewer assignment and
 dept-level compliance tracking.
===============================================================================
*/

-- DEPARTMENTS
-- Academic/administrative departments inside an institution.
-- Department Reviewers are scoped to one department.

CREATE TABLE departments (
    department_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id      UUID NOT NULL REFERENCES institutions(institution_id) ON DELETE CASCADE,
    department_name     VARCHAR(255) NOT NULL,
    department_code     VARCHAR(50),
    hod_name            VARCHAR(255),           -- Head of Department name
    reviewer_user_id    UUID REFERENCES users(user_id),  -- assigned Department Reviewer
    is_active           BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(institution_id, department_name)
);

CREATE INDEX idx_departments_institution ON departments(institution_id);


/*
===============================================================================
 BLOCK 4: CONTROL LIBRARY
 MongoDB holds the master control library (framework mappings, evidence
 requirements). PostgreSQL tracks per-institution control assignment
 status and evidence.
===============================================================================
*/

-- CONTROL ASSIGNMENTS
-- Tracks the status of each control for each institution.
-- control_id references MongoDB control library document ID.
-- This is the operational state of a control — assigned, in progress, done.

CREATE TABLE control_assignments (
    assignment_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id      UUID NOT NULL REFERENCES institutions(institution_id) ON DELETE CASCADE,
    control_id          VARCHAR(100) NOT NULL,      -- MongoDB control library ref
    framework_name      VARCHAR(100) NOT NULL,      -- DPDP / ISO27001 / NIST / UGC etc.
    assigned_to         UUID REFERENCES users(user_id),
    department_id       UUID REFERENCES departments(department_id),
    status              VARCHAR(50) DEFAULT 'not_started',
                        -- not_started / in_progress / submitted / compliant / non_compliant / na
    due_date            TIMESTAMP,
    completed_at        TIMESTAMP,
    assigned_by         UUID REFERENCES users(user_id),
    notes               TEXT,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(institution_id, control_id)
);

CREATE INDEX idx_control_assignments_institution ON control_assignments(institution_id);
CREATE INDEX idx_control_assignments_status ON control_assignments(status);
CREATE INDEX idx_control_assignments_dept ON control_assignments(department_id);


/*
===============================================================================
 BLOCK 5: ASSESSMENTS & COMPLIANCE RESULTS
 Tables: assessments, assessment_responses, compliance_results, compliance_gaps
===============================================================================
*/

-- ASSESSMENTS
-- A formal compliance assessment run.
-- One assessment → many responses → compliance results and gaps.

CREATE TABLE assessments (
    assessment_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id      UUID NOT NULL REFERENCES institutions(institution_id),
    assessment_name     VARCHAR(255),
    framework_name      VARCHAR(100),               -- which framework this assessment covers
    assessment_status   VARCHAR(50) DEFAULT 'draft',
    -- draft / in_progress / completed / archived
    started_by          UUID REFERENCES users(user_id),
    started_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at        TIMESTAMP
);

CREATE INDEX idx_assessments_institution ON assessments(institution_id);
CREATE INDEX idx_assessments_status ON assessments(assessment_status);


-- ASSESSMENT RESPONSES
-- Individual answers submitted during an assessment.

CREATE TABLE assessment_responses (
    response_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id   UUID NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    question_id     VARCHAR(100),
    control_id      VARCHAR(100),               -- MongoDB control ref
    response_value  TEXT,
    score_value     NUMERIC(5,2),
    answered_by     UUID REFERENCES users(user_id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_responses_assessment ON assessment_responses(assessment_id);


-- COMPLIANCE RESULTS
-- Framework-wise aggregate output of an assessment.

CREATE TABLE compliance_results (
    result_id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id               UUID REFERENCES assessments(assessment_id),
    institution_id              UUID REFERENCES institutions(institution_id),
    framework_name              VARCHAR(100),
    compliance_percentage       NUMERIC(5,2),
    compliant_controls          INTEGER,
    partial_controls            INTEGER,
    non_compliant_controls      INTEGER,
    critical_gap_count          INTEGER,
    created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_compliance_results_institution ON compliance_results(institution_id);


-- COMPLIANCE GAPS
-- Individual gaps identified during an assessment.
-- Gaps feed into mitigation tasks.

CREATE TABLE compliance_gaps (
    gap_id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id       UUID REFERENCES assessments(assessment_id),
    institution_id      UUID NOT NULL REFERENCES institutions(institution_id),
    control_id          VARCHAR(100),
    framework_name      VARCHAR(100),
    severity            VARCHAR(50),            -- critical / high / medium / low
    title               TEXT,
    description         TEXT,
    remediation_status  VARCHAR(50) DEFAULT 'open',
    -- open / in_progress / resolved / accepted_risk
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gaps_institution ON compliance_gaps(institution_id);
CREATE INDEX idx_gaps_severity ON compliance_gaps(severity);


/*
===============================================================================
 BLOCK 6: MITIGATION TASKS
 Operational remediation assigned to users, linked to gaps or controls.
===============================================================================
*/

CREATE TABLE mitigation_tasks (
    task_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID REFERENCES institutions(institution_id),
    gap_id          UUID REFERENCES compliance_gaps(gap_id),
    assignment_id   UUID REFERENCES control_assignments(assignment_id),
    assigned_to     UUID REFERENCES users(user_id),
    department_id   UUID REFERENCES departments(department_id),
    task_title      TEXT NOT NULL,
    task_description TEXT,
    priority        VARCHAR(50),                -- critical / high / medium / low
    task_status     VARCHAR(50) DEFAULT 'open',
    -- open / in_progress / completed / overdue / cancelled
    due_date        TIMESTAMP,
    completed_at    TIMESTAMP,
    created_by      UUID REFERENCES users(user_id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_institution ON mitigation_tasks(institution_id);
CREATE INDEX idx_tasks_assigned ON mitigation_tasks(assigned_to);
CREATE INDEX idx_tasks_status ON mitigation_tasks(task_status);


/*
===============================================================================
 BLOCK 7: EVIDENCE
 Uploaded by Dept Reviewer / IT Security.
 Reviewed and approved by Compliance Officer.
 Auditor can view all evidence.
===============================================================================
*/

CREATE TABLE evidence_documents (
    evidence_id         UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id      UUID REFERENCES institutions(institution_id),
    control_id          VARCHAR(100),               -- MongoDB control ref
    assignment_id       UUID REFERENCES control_assignments(assignment_id),
    department_id       UUID REFERENCES departments(department_id),
    file_name           TEXT NOT NULL,
    file_path           TEXT NOT NULL,              -- object storage path
    mime_type           VARCHAR(100),
    file_size_kb        INTEGER,
    description         TEXT,
    uploaded_by         UUID REFERENCES users(user_id),
    approval_status     VARCHAR(50) DEFAULT 'pending',
    -- pending / approved / rejected
    approved_by         UUID REFERENCES users(user_id),
    approved_at         TIMESTAMP,
    rejection_reason    TEXT,
    uploaded_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evidence_institution ON evidence_documents(institution_id);
CREATE INDEX idx_evidence_control ON evidence_documents(control_id);
CREATE INDEX idx_evidence_status ON evidence_documents(approval_status);


/*
===============================================================================
 BLOCK 8: INCIDENTS
 New in v2. Managed by IT Security Officer.
 Triggers CERT-In 6hr obligation and DPDP breach notification workflow.
===============================================================================
*/

CREATE TABLE incidents (
    incident_id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id          UUID NOT NULL REFERENCES institutions(institution_id),
    title                   VARCHAR(255) NOT NULL,
    description             TEXT,
    incident_type           VARCHAR(100),
    -- data_breach / unauthorized_access / ransomware / phishing / system_failure / other
    severity                VARCHAR(50),            -- critical / high / medium / low
    status                  VARCHAR(50) DEFAULT 'open',
    -- open / investigating / contained / resolved / closed
    occurred_at             TIMESTAMP,
    detected_at             TIMESTAMP,
    cert_in_deadline        TIMESTAMP,              -- detected_at + 6 hours
    cert_in_reported        BOOLEAN DEFAULT FALSE,
    cert_in_reported_at     TIMESTAMP,
    dpdp_notification_required BOOLEAN DEFAULT FALSE,
    dpdp_notified_at        TIMESTAMP,
    affected_systems        TEXT,
    affected_data_categories TEXT,
    reported_by             UUID REFERENCES users(user_id),
    assigned_to             UUID REFERENCES users(user_id),
    resolved_at             TIMESTAMP,
    resolution_notes        TEXT,
    checklist_items         JSONB DEFAULT '[]'::jsonb,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incidents_institution ON incidents(institution_id);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);


-- INCIDENT TIMELINE
-- Step-by-step log of actions taken during incident response.

CREATE TABLE incident_timeline (
    timeline_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id     UUID NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    action_taken    TEXT NOT NULL,
    action_by       UUID REFERENCES users(user_id),
    action_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
===============================================================================
 BLOCK 9: VENDORS
 Managed by Vendor Reviewer.
 Compliance Officer notified on high risk vendors.
===============================================================================
*/

CREATE TABLE vendors (
    vendor_id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id          UUID REFERENCES institutions(institution_id),
    vendor_name             VARCHAR(255) NOT NULL,
    product_name            VARCHAR(255),
    vendor_category         VARCHAR(100),
    -- cloud / edtech / erp / security / communication / other
    processing_location     VARCHAR(100),           -- India / US / EU / Other
    dpa_available           BOOLEAN DEFAULT FALSE,  -- Data Processing Agreement
    model_training_allowed  BOOLEAN DEFAULT FALSE,
    contract_expiry_date    DATE,
    contact_email           VARCHAR(255),
    created_by              UUID REFERENCES users(user_id),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendors_institution ON vendors(institution_id);


-- VENDOR RISK ASSESSMENTS
-- Each formal assessment of a vendor's compliance posture.

CREATE TABLE vendor_risk_assessments (
    vendor_risk_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id           UUID REFERENCES vendors(vendor_id),
    institution_id      UUID REFERENCES institutions(institution_id),
    risk_level          VARCHAR(50),            -- critical / high / medium / low
    assessment_summary  TEXT,
    recommendations     TEXT,
    dpdp_compliant      BOOLEAN,
    assessed_by         UUID REFERENCES users(user_id),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vendor_risk_institution ON vendor_risk_assessments(institution_id);
CREATE INDEX idx_vendor_risk_vendor_created ON vendor_risk_assessments(vendor_id, created_at DESC);


/*
===============================================================================
 BLOCK 10: POLICIES
 Drafted by Compliance Officer.
 Approved/rejected by Policy Approver.
 Versioned for diff comparison.
===============================================================================
*/

CREATE TABLE generated_policies (
    policy_id           UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id      UUID REFERENCES institutions(institution_id),
    related_control_id  VARCHAR(100),
    policy_name         VARCHAR(255) NOT NULL,
    policy_content      TEXT,
    version_number      INTEGER DEFAULT 1,
    policy_status       VARCHAR(50) DEFAULT 'draft',
    -- draft / pending_approval / approved / rejected / superseded
    generated_by        UUID REFERENCES users(user_id),
    submitted_to        UUID REFERENCES users(user_id),     -- Policy Approver
    approved_by         UUID REFERENCES users(user_id),
    approved_at         TIMESTAMP,
    rejection_reason    TEXT,
    parent_policy_id    UUID REFERENCES generated_policies(policy_id),  -- previous version
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policies_institution ON generated_policies(institution_id);
CREATE INDEX idx_policies_status ON generated_policies(policy_status);


/*
===============================================================================
 BLOCK 11: AUDIT WORKSPACE
 Auditor adds observations against controls/evidence.
 Feeds into audit reports.
===============================================================================
*/

-- AUDIT OBSERVATIONS
-- Auditor-only. Comments/findings during an audit cycle.

CREATE TABLE audit_observations (
    observation_id      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id      UUID REFERENCES institutions(institution_id),
    assessment_id       UUID REFERENCES assessments(assessment_id),
    control_id          VARCHAR(100),
    evidence_id         UUID REFERENCES evidence_documents(evidence_id),
    observation_text    TEXT NOT NULL,
    severity            VARCHAR(50),            -- finding / observation / recommendation
    status              VARCHAR(50) DEFAULT 'open',
    -- open / acknowledged / resolved
    added_by            UUID REFERENCES users(user_id),  -- must be Auditor role
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_observations_institution ON audit_observations(institution_id);
CREATE INDEX idx_observations_assessment ON audit_observations(assessment_id);


-- AUDIT REPORTS
-- Final generated reports (PDF). Visible to Institution Admin + Read-Only Assessor.

CREATE TABLE audit_reports (
    report_id       UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID REFERENCES institutions(institution_id),
    assessment_id   UUID REFERENCES assessments(assessment_id),
    report_name     VARCHAR(255),
    report_type     VARCHAR(100),
    -- naac / iso_readiness / dpdp_assessment / custom
    file_path       TEXT,
    generated_by    UUID REFERENCES users(user_id),
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_reports_institution ON audit_reports(institution_id);


/*
===============================================================================
 BLOCK 12: COMPLIANCE CALENDAR
 Tracks control due dates, review cycles, and assessment schedules
 visible to Institution Admin and Compliance Officer.
===============================================================================
*/

CREATE TABLE compliance_calendar (
    calendar_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID NOT NULL REFERENCES institutions(institution_id),
    event_type      VARCHAR(100),
    -- control_due / assessment_scheduled / evidence_expiry /
    -- policy_review / vendor_contract_expiry / audit_scheduled
    related_entity_type VARCHAR(100),           -- control / vendor / policy / assessment
    related_entity_id   UUID,
    title           VARCHAR(255) NOT NULL,
    due_date        TIMESTAMP NOT NULL,
    is_completed    BOOLEAN DEFAULT FALSE,
    created_by      UUID REFERENCES users(user_id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_calendar_institution ON compliance_calendar(institution_id);
CREATE INDEX idx_calendar_due ON compliance_calendar(due_date);


/*
===============================================================================
 BLOCK 13: NOTIFICATIONS
 System-generated alerts for all roles.
===============================================================================
*/

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id  UUID REFERENCES institutions(institution_id),
    user_id         UUID REFERENCES users(user_id),
    title           VARCHAR(255) NOT NULL,
    message         TEXT,
    notification_type VARCHAR(100),
    -- task_assigned / evidence_approved / evidence_rejected /
    -- incident_logged / policy_pending / control_overdue / vendor_risk_flagged
    related_entity_type VARCHAR(100),
    related_entity_id   UUID,
    is_read         BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_read ON notifications(is_read);


/*
===============================================================================
 BLOCK 14: AUDIT LOGS
 Central enterprise audit trail. Never deleted.
 Every action by every user is recorded here.
===============================================================================
*/

CREATE TABLE audit_logs (
    audit_log_id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id          UUID REFERENCES institutions(institution_id),
    user_id                 UUID REFERENCES users(user_id),
    active_role_id          UUID REFERENCES roles(role_id),
    assumed_role_session_id UUID REFERENCES role_assumption_sessions(role_session_id),
    action_type             VARCHAR(100),
    entity_type             VARCHAR(100),
    entity_id               UUID,
    action_details          JSONB,
    ip_address              VARCHAR(100),
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_institution ON audit_logs(institution_id);
CREATE INDEX idx_audit_logs_institution_created_action ON audit_logs(institution_id, created_at, action_type);

-- Master-plan addition. Run only if the deployed Neon schema does not already include this table.
CREATE TABLE IF NOT EXISTS ai_conversations (
    conversation_id   UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institution_id    UUID REFERENCES institutions(institution_id),
    user_id           UUID REFERENCES users(user_id),
    agent_type        VARCHAR(100) NOT NULL,
    messages          JSONB NOT NULL DEFAULT '[]',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ai_conversations_user ON ai_conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_conversations_type ON ai_conversations(agent_type);


/*
===============================================================================
 SEED DATA — ROLES
===============================================================================
*/

INSERT INTO roles (role_name, description) VALUES
('Super Admin',         'Platform-level developer administrator. God mode.'),
('Institution Admin',   'Institution-wide administrative authority. Manages users, departments, calendar.'),
('Compliance Officer',  'Primary daily operator. Manages controls, evidence, gap assessments, report building.'),
('IT Security Officer', 'Technical controls, incident management, CERT-In reporting, vulnerability tracking.'),
('Auditor',             'Read and comment only. Reviews evidence, adds observations, generates audit reports.'),
('Department Reviewer', 'Dept-level tasks. Fills self-assessments and uploads evidence for their department.'),
('Vendor Reviewer',     'Manages vendor register, conducts vendor risk assessments.'),
('Policy Approver',     'Approves or rejects drafted policies. Sees version diffs.'),
('Read-Only Assessor',  'Pure observer. Can view dashboards, control status, and reports. No edits.');


/*
===============================================================================
 SEED DATA — ALLOWED ROLE TRANSITIONS
 (Inserted after roles table is populated with real UUIDs.
  This is a reference — execute after seeding roles.)

 Institution Admin  → can assume Compliance Officer, IT Security Officer,
                       Auditor, Dept Reviewer, Vendor Reviewer, Read-Only Assessor
 Compliance Officer → can assume Dept Reviewer, Read-Only Assessor
 No role can assume upward (no privilege escalation).

===============================================================================
*/

-- Execute manually after roles are seeded with known UUIDs.


/*
===============================================================================
 TABLE SUMMARY
===============================================================================

  BLOCK 1  — Platform Foundation
    institutions, roles, permissions, role_permissions

  BLOCK 2  — Users & Sessions
    users, password_reset_tokens, user_sessions,
    allowed_role_transitions, role_assumption_sessions

  BLOCK 3  — Departments              [NEW v2]
    departments

  BLOCK 4  — Control Assignments      [NEW v2]
    control_assignments

  BLOCK 5  — Assessments & Results
    assessments, assessment_responses, compliance_results, compliance_gaps

  BLOCK 6  — Mitigation Tasks
    mitigation_tasks

  BLOCK 7  — Evidence
    evidence_documents

  BLOCK 8  — Incidents                [NEW v2]
    incidents, incident_timeline

  BLOCK 9  — Vendors
    vendors, vendor_risk_assessments

  BLOCK 10 — Policies
    generated_policies  (+ version_number, parent_policy_id added)

  BLOCK 11 — Audit Workspace          [NEW v2]
    audit_observations, audit_reports

  BLOCK 12 — Compliance Calendar      [NEW v2]
    compliance_calendar

  BLOCK 13 — Notifications
    notifications

  BLOCK 14 — Audit Logs
    audit_logs

  TOTAL: 28 tables

===============================================================================
 END OF SCHEMA v2.0
===============================================================================
*/