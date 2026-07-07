# PostgreSQL Audit

Schema source: `schema.sql`.

## Tables

| Table | Purpose | Current usage |
|---|---|---|
| `institutions` | Tenant/institution records | Used by institutions router, auth user context, audit joins |
| `roles` | Role catalog | Used by auth, users, RBAC |
| `permissions` | Permission catalog | Used by RBAC |
| `role_permissions` | Role-permission mapping | Used by `RbacRepository` |
| `users` | User accounts and profile data | Used by auth, users, assignments, audit joins |
| `password_reset_tokens` | Password reset token state | Used by auth service |
| `user_sessions` | Server-side auth sessions and active role | Used by auth dependency and refresh/logout |
| `allowed_role_transitions` | Intended role assumption controls | Table exists; start flow not found |
| `role_assumption_sessions` | Intended role assumption audit/session state | Table exists; insert flow not found |
| `departments` | Institution departments and reviewer assignment | Used by departments, users, tasks |
| `control_assignments` | Operational control assignment state | Used by controls, tasks, compliance, AI proxy |
| `assessments` | Compliance assessments | Used by assessments and audit reports |
| `assessment_responses` | Assessment answers | Used by assessment save/submit |
| `compliance_results` | Assessment result summary | Inserted on assessment submit |
| `compliance_gaps` | Gaps/remediation issues | Used by gaps, tasks, compliance AI proxy, reports |
| `mitigation_tasks` | Remediation tasks | Used by tasks and department pages |
| `evidence_documents` | Uploaded evidence metadata | Used by evidence, audit, tasks |
| `incidents` | Security incidents | Used by incidents and security AI proxy |
| `incident_timeline` | Incident action history | Read by incident detail; write path not found |
| `vendors` | Vendor register | Used by vendors |
| `vendor_risk_assessments` | Vendor risk history | Read by vendors; write path not found in main vendor router |
| `generated_policies` | Policy drafts and statuses | Used by policies |
| `audit_observations` | Auditor observations | Used by audit workspace |
| `audit_reports` | Generated report records | Used by policies and audit |
| `compliance_calendar` | Calendar events | Used by calendar router |
| `notifications` | Notification records | Table exists; router is empty |
| `audit_logs` | Audit trail | Used by auth, users, audit router |
| `ai_conversations` | AI conversation history | Used by AI conversation manager |

## Relationships

Implemented:

- Most operational rows include `institution_id` for tenant scoping.
- User/role relationships are joined in auth and user list queries.
- Assessment, response, result, gap, evidence, observation, and report tables are connected by IDs.

Partially Implemented:

- Application logic enforces tenancy in most queries, but not all ID relationships have explicit repository-level abstractions.
- Some dynamic SQL update clauses are built from whitelisted fields; this is acceptable but should remain tightly constrained.

## Indexes

Partially Implemented:

- Index details were not fully audited line by line in this pass.
- Query-heavy fields include `institution_id`, status fields, user/session IDs, and foreign keys.

## Unused or Underused Tables

- `allowed_role_transitions`
- `role_assumption_sessions`
- `incident_timeline` write path
- `notifications`
- `vendor_risk_assessments` write path

## Missing Constraints and Improvements

- Add stricter enum/check constraints for status/severity fields if not already present.
- Add file size/type metadata validation constraints or application-level enforcement for evidence.
- Ensure all tenant-scoped tables have indexes on `institution_id`.
- Ensure audit/event tables have indexes on `created_at`, `institution_id`, and `action_type`.

