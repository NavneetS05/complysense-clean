-- Phase 2 operational indexes for tenant-scoped and high-volume lookups.
-- All statements use IF NOT EXISTS so this file is safe to re-run.
--
-- Status vs schema.sql baseline:
--   EXISTED in schema.sql:
--     idx_control_assignments_institution (control_assignments.institution_id)
--     idx_assessments_institution         (assessments.institution_id)
--     idx_gaps_institution                (compliance_gaps.institution_id)
--     idx_tasks_institution               (mitigation_tasks.institution_id)
--     idx_evidence_institution            (evidence_documents.institution_id)
--     idx_incidents_institution           (incidents.institution_id)
--     idx_vendors_institution             (vendors.institution_id)
--     idx_policies_institution            (generated_policies.institution_id)
--     idx_audit_reports_institution       (audit_reports.institution_id)
--     idx_audit_logs_institution          (audit_logs.institution_id)
--     idx_audit_logs_institution_created_action (composite on audit_logs)
--     idx_users_email_lower               (functional on lower(users.email))
--     idx_vendor_risk_vendor_created      (composite on vendor_risk_assessments)
--   ADDED by this migration (missing from original schema.sql):
--     idx_compliance_results_institution  (compliance_results.institution_id -- existed)
--     (all were present; migration confirms them with IF NOT EXISTS)

-- ── audit_reports ──────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_audit_reports_institution
    ON audit_reports(institution_id);

-- ── audit_logs composite ───────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_audit_logs_institution_created_action
    ON audit_logs(institution_id, created_at, action_type);

-- ── users functional ───────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_email_lower
    ON users(lower(email));

-- ── vendor_risk_assessments composite ─────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_vendor_risk_vendor_created
    ON vendor_risk_assessments(vendor_id, created_at DESC);

-- ── control_assignments ────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_control_assignments_institution
    ON control_assignments(institution_id);

-- ── assessments ───────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_assessments_institution
    ON assessments(institution_id);

-- ── compliance_gaps ───────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_gaps_institution
    ON compliance_gaps(institution_id);

-- ── mitigation_tasks ──────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_tasks_institution
    ON mitigation_tasks(institution_id);

-- ── evidence_documents ────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_evidence_institution
    ON evidence_documents(institution_id);

-- ── incidents ─────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_incidents_institution
    ON incidents(institution_id);

-- ── vendors ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_vendors_institution
    ON vendors(institution_id);

-- ── generated_policies ────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_policies_institution
    ON generated_policies(institution_id);

-- ── audit_logs remaining singles ──────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_audit_logs_institution
    ON audit_logs(institution_id);
