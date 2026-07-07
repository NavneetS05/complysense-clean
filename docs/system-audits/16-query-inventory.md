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
| `controls.create_control_assignment` | `control_assignments` | Insert assignment | No enum validation for status |
| `assessments.list_assessments` | `assessments` | Assessment list | Tenant scoped |
| `assessments.save_assessment_response` | `assessment_responses` | Upsert-like save | Checks by assessment/question only |
| `assessments.submit_assessment` | `assessments`, `assessment_responses`, `compliance_results`, `compliance_gaps` | Complete assessment and create gaps | Scoring is simplistic |

## Evidence Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `evidence.list_evidence` | `evidence_documents` | Evidence list | Tenant scoped |
| `evidence.upload_evidence` | `control_assignments`, `evidence_documents` | Validate assignment and insert evidence | File written locally before DB insert |
| `evidence.get_evidence` | `evidence_documents` | Evidence detail | Does not return file bytes |

## Incident Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `incidents.list_incidents` | `incidents` | Filter/search incidents | Dynamic filters parameterized |
| `incidents.create_incident` | `incidents` | Insert incident | CERT-In deadline = detected + 6 hours |
| `incidents.get_dashboard_stats` | `incidents` | Aggregate dashboard stats | Timeline is generated, not queried |
| `incidents.get_incident_detail` | `incidents`, `incident_timeline` | Detail plus timeline | Timeline write path not visible |
| `incidents.update_incident` | `incidents` | Update status/reporting | Whitelisted dynamic fields |

## Vendor Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `vendors.list_vendors` | `vendors`, `vendor_risk_assessments` | Vendor list with latest risk | Uses `distinct on` latest assessment |
| `vendors.get_vendor` | `vendors`, `vendor_risk_assessments` | Vendor detail/history | Limits risk history to 5 |
| `vendors.create_vendor` | `vendors` | Insert vendor | No risk assessment insert |
| `vendors.update_vendor` | `vendors` | Update vendor | Dynamic fields from Pydantic dump |

## Policy and Audit Queries

| File/function | Tables | Query purpose | Observations |
|---|---|---|---|
| `policies.list_policies` | `generated_policies` | List policies | Tenant scoped |
| `policies.create_policy` | `generated_policies` | Create draft | Version hardcoded to 1 |
| `policies.generate_executive_report` | `audit_reports` | Insert report record | File path synthetic |
| `audit.get_audit_logs` | `audit_logs`, `institutions`, `users`, `roles` | Search/export audit logs | Supports CSV |
| `audit.create_observation` | `audit_observations`, `assessments`, `evidence_documents`, `audit_logs` | Add observation | Log entity ID not tied to created observation |
| `audit.generate_report` | `audit_reports`, `assessments` | Create report record | Returns summary counts |

## Duplicate or Overlapping Queries

- Report generation/listing exists in both `policies.py` and `audit.py`, using `audit_reports`.
- Smart sampling exists in `audit.py` and AI proxy/service routes.
- Draft observation exists locally in `audit.py` and through AI routes.

## Performance Observations

- Tenant-scoped indexes on `institution_id` are important across most operational tables.
- Audit log search should be indexed on `institution_id`, `created_at`, `action_type`, and possibly user ID.
- `lower(email)` lookups should be backed by a functional or normalized email index.
- `vendors.list_vendors` relies on latest risk assessment; index on `(vendor_id, created_at desc)` is recommended.

