# Use: Role-based authorization checks before AI execution.

from typing import List, Dict

# Explicit role mapping for endpoints as per the specification
ENDPOINT_ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "triage": ["compliance_officer"],
    "regulatory_change": ["compliance_officer"],
    "cert_in_draft": ["it_security"],
    "smart_sample": ["auditor"],
    "draft_observation": ["auditor"],
    "translate_control": ["dept_reviewer"],
    "preflight_check": ["dept_reviewer"],
    "analyze_contract": ["vendor_reviewer"],
    "conflict_detect": ["policy_approver"],
    "executive_summary": ["policy_approver"],
    "chat": ["read_only_assessor", "compliance_officer", "it_security", "auditor", "dept_reviewer", "vendor_reviewer", "policy_approver", "institution_admin"],
    "anomaly_detect": ["super_admin"],
    "risk_heatmap": ["institution_admin"],
    "digest": ["compliance_officer", "it_security", "auditor", "dept_reviewer", "vendor_reviewer", "policy_approver", "institution_admin"],
}


class RoleGuard:
    def __init__(self, allowed_roles: List[str] | None = None):
        self.allowed_roles = allowed_roles

    def verify_role_access(self, user_role: str, endpoint_name: str | None = None) -> bool:
        """
        Validates whether the user's role is authorized to invoke a particular endpoint/agent.
        """
        if not user_role:
            return False
            
        role_key = user_role.lower().replace(" ", "_")
        
        # If initialized with allowed roles list, use that
        if self.allowed_roles is not None:
            allowed = [r.lower().replace(" ", "_") for r in self.allowed_roles]
            return role_key in allowed
            
        # Otherwise look up the endpoint name in permission table
        if endpoint_name:
            allowed = ENDPOINT_ROLE_PERMISSIONS.get(endpoint_name, [])
            return role_key in allowed
            
        return False

