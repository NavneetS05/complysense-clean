# Query Inventory Audit

This inventory lists significant query patterns found in the inspected routers and repositories.

## Authentication Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `UserRepository.find_active_by_email` | `users`, `roles` | Login lookup | Uses lower(email), active-only |
| `UserRepository.create` | `users` | Register/create user | Parameterized insert |
| `UserRepository.increment_failed_attempts` | `users` | Login throttle | Atomic increment |
| `UserRepository.create_reset_token` | `password_reset_tokens` | Password reset | Raw token stored directly |
| `SessionRepository.find_active` | `user_sessions`, `roles` | Validate session | Checks expiry |
| `RbacRepository.permissions_for_role` | `role_permissions`, `permissions` | Permission list | Used on each user context build |

## Control and Assessment Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `controls.list_controls` | `control_assignments`, `departments`, `users` | Control list | Tenant scoped |
| `controls.create_control_assignment` | `control_assignments` | Insert assignment | Status uses application enum validation |
| `assessments.list_assessments` | `assessments` | Assessment list | Tenant scoped |
| `assessments.save_assessment_response` | `assessment_responses` | Upsert-like save | Checks by assessment/question only |
| `assessments.submit_assessment` | `assessments`, `assessment_responses`, `compliance_results`, `compliance_gaps` | Complete assessment and recreate derived result/gaps | Deterministic and idempotent for same saved responses; framework weighting remains a product decision |

## Evidence Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `evidence.list_evidence` | `evidence_documents` | Evidence list | Tenant scoped |
| `evidence.upload_evidence` | `control_assignments`, `evidence_documents`, MongoDB documents | Validate assignment, stream file, insert evidence, write document metadata | Size/type validation and malware-scan hook are in place |
| `evidence.review_evidence` | `evidence_documents`, `audit_logs` | Approve/reject pending evidence | Gated by `REVIEW_EVIDENCE`; writes transition audit event |
| `evidence.get_evidence` | `evidence_documents` | Evidence detail | Does not return file bytes |

## Incident Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `incidents.list_incidents` | `incidents` | Filter/search incidents | Dynamic filters parameterized |
| `incidents.create_incident` | `incidents` | Insert incident | CERT-In deadline = detected + 6 hours |
| `incidents.get_dashboard_stats` | `incidents`, `incident_timeline` | Aggregate dashboard stats | Uses real incident/reporting buckets and timeline event counts |
| `incidents.get_incident_detail` | `incidents`, `incident_timeline` | Detail plus timeline | Timeline is written on create/update |
| `incidents.update_incident` | `incidents`, `incident_timeline`, `audit_logs` | Update status/reporting | Whitelisted dynamic fields; writes timeline and audit event |

## Vendor Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `vendors.list_vendors` | `vendors`, `vendor_risk_assessments` | Vendor list with latest risk | Uses `distinct on` latest assessment |
| `vendors.get_vendor` | `vendors`, `vendor_risk_assessments` | Vendor detail/history | Limits risk history to 5 |
| `vendors.create_vendor` | `vendors`, `audit_logs` | Insert vendor | Writes vendor audit event |
| `vendors.update_vendor` | `vendors` | Update vendor | Dynamic fields from Pydantic dump |
| `vendors.upsert_vendor_risk_assessment` | `vendor_risk_assessments`, `audit_logs` | Create/update vendor risk assessment | Writes assessment audit event |
| `ai.vendor.ai_analyze_contract` | `vendors`, `vendor_risk_assessments`, `audit_logs`, MongoDB vendor contracts | Analyze contract and persist risk assessment | AI output is normalized into risk assessment fields where possible |

## Policy and Audit Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `policies.list_policies` | `generated_policies` | List policies | Tenant scoped |
| `policies.create_policy` | `generated_policies` | Create draft or redraft | New drafts start at v1; redrafts with `parent_policy_id` increment from parent |
| `policies.generate_executive_report` | `audit_reports` | Compatibility wrapper for report record creation | Uses canonical audit report insert helper |
| `audit.get_audit_logs` | `audit_logs`, `institutions`, `users`, `roles` | Search/export audit logs | Supports CSV |
| `audit.create_observation` | `audit_observations`, `assessments`, `evidence_documents`, `audit_logs` | Add observation | Audit log uses created observation ID |
| `audit.generate_report` | `audit_reports`, `assessments` | Canonical audit report generation route | Uses shared audit report insert helper and returns summary counts |

## Duplicate or Overlapping Queries

- Report generation canonical implementation is `audit.py`; `policies.py` uses the shared audit report insert helper for compatibility.
- Smart sampling canonical implementation is `/api/v1/ai/audit/smart-sample`; old local audit route redirects with HTTP 307.
- Draft observation canonical implementation is `/api/v1/ai/audit/draft-observation`; old local audit route redirects with HTTP 307.

## Performance Observations

- Tenant-scoped indexes on `institution_id` are important across most operational tables.
- Audit log search is backed by `audit_logs(institution_id, created_at, action_type)` plus existing single-column/entity indexes.
- `lower(email)` lookups are backed by `idx_users_email_lower`.
- `vendors.list_vendors` latest-risk lookup is backed by `idx_vendor_risk_vendor_created`.
