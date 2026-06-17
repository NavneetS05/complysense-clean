# Use: Defines the fixed roles, permission keys, and role prefix mappings for the RBAC matrix.

from enum import StrEnum


class RoleName(StrEnum):
    SUPER_ADMIN = "Super Admin"
    INSTITUTION_ADMIN = "Institution Admin"
    COMPLIANCE_OFFICER = "Compliance Officer"
    IT_SECURITY_OFFICER = "IT Security Officer"
    AUDITOR = "Auditor"
    DEPARTMENT_REVIEWER = "Department Reviewer"
    VENDOR_REVIEWER = "Vendor Reviewer"
    POLICY_APPROVER = "Policy Approver"
    READ_ONLY_ASSESSOR = "Read-Only Assessor"


class PermissionKey(StrEnum):
    VIEW_ROLES = "view_roles"
    MANAGE_INSTITUTIONS = "manage_institutions"
    VIEW_AUDIT_TRAIL = "view_audit_trail"
    MANAGE_USERS = "manage_users"
    MANAGE_DEPARTMENTS = "manage_departments"
    VIEW_CALENDAR = "view_calendar"
    MANAGE_CALENDAR = "manage_calendar"
    VIEW_CONTROLS = "view_controls"
    MANAGE_CONTROLS = "manage_controls"
    VIEW_ASSESSMENTS = "view_assessments"
    MANAGE_ASSESSMENTS = "manage_assessments"
    VIEW_GAPS = "view_gaps"
    MANAGE_GAPS = "manage_gaps"
    VIEW_TASKS = "view_tasks"
    MANAGE_TASKS = "manage_tasks"
    UPLOAD_EVIDENCE = "upload_evidence"
    REVIEW_EVIDENCE = "review_evidence"
    VIEW_EVIDENCE = "view_evidence"
    MANAGE_INCIDENTS = "manage_incidents"
    VIEW_INCIDENTS = "view_incidents"
    MANAGE_VENDORS = "manage_vendors"
    VIEW_VENDORS = "view_vendors"
    DRAFT_POLICIES = "draft_policies"
    APPROVE_POLICIES = "approve_policies"
    VIEW_POLICIES = "view_policies"
    ADD_AUDIT_OBSERVATIONS = "add_audit_observations"
    GENERATE_AUDIT_REPORTS = "generate_audit_reports"
    VIEW_AUDIT_REPORTS = "view_audit_reports"
    VIEW_NOTIFICATIONS = "view_notifications"
    USE_ASSESSOR_CHAT = "use_assessor_chat"
    USE_ROLE_ASSUMPTION = "use_role_assumption"


ROLE_ROUTE_PREFIXES: dict[RoleName, str] = {
    RoleName.SUPER_ADMIN: "super-admin",
    RoleName.INSTITUTION_ADMIN: "admin",
    RoleName.COMPLIANCE_OFFICER: "compliance",
    RoleName.IT_SECURITY_OFFICER: "security",
    RoleName.AUDITOR: "auditor",
    RoleName.DEPARTMENT_REVIEWER: "dept",
    RoleName.VENDOR_REVIEWER: "vendor",
    RoleName.POLICY_APPROVER: "policy",
    RoleName.READ_ONLY_ASSESSOR: "assessor",
}
