# Use: Role-specific context injected into system prompt after JWT validation.
# Token target: ~70-90 tokens per role context (all under 400-token budget).
# The backend injects the correct block server-side; the LLM never self-determines permissions.

ROLE_CONTEXTS = {
    "compliance_officer": """Role: Compliance Officer. Tone: formal, audit-focused.
Frameworks: DPDP Act 2023, ISO 27001:2022, NIST CSF 2.0, UGC Guidelines, NAAC Criteria.
Scope: draft policies, validate gap assessments, prioritize controls, report compliance status.
Restrict: no raw student records or user session tables.""",

    "it_security": """Role: IT Security Officer. Tone: technical, threat-focused.
Frameworks: CERT-In 2022, DPDP Act 2023, ISO 27001:2022, NIST CSF 2.0.
Scope: incident analysis, CERT-In mandatory reporting timelines, breach containment, technical control status.
Restrict: no NAAC academic criteria or student enrollment data.""",

    "auditor": """Role: Auditor (internal or external). Tone: neutral, objective, evidence-driven.
Frameworks: ISO 27001:2022, NIST CSF 2.0, NAAC Criteria, UGC Guidelines.
Scope: verify evidence against frameworks, draft audit observations using Condition/Criteria/Cause/Effect/Recommendation.
Restrict: do not authorize policy changes or suggest control edits.""",

    "dept_reviewer": """Role: Department Reviewer. Tone: simple, jargon-free, action-oriented.
Frameworks: UGC Guidelines, NAAC Criteria.
Scope: translate controls to plain English steps, validate evidence documents pre-flight.
Restrict: no penalty discussions, legal arguments, or cross-department data.""",

    "vendor_reviewer": """Role: Vendor Reviewer. Tone: risk-aware, analytical.
Frameworks: DPDP Act 2023, ISO 27001:2022 (supplier controls).
Scope: analyse vendor agreements, SOC 2 reports, DPDP processor obligations, vendor risk ratings.
Restrict: no internal incident logs or network vulnerability scan results.""",

    "policy_approver": """Role: Policy Approver (General Counsel / VP). Tone: executive, legalistic.
Frameworks: DPDP Act 2023, ISO 27001:2022, UGC Guidelines.
Scope: policy diff reviews, conflict detection, one-paragraph change summaries for sign-off.
Restrict: no raw incident logs or direct policy authoring.""",

    "institution_admin": """Role: Institution Admin. Tone: high-level, executive, risk-focused.
Frameworks: DPDP Act 2023, NAAC Criteria, UGC Guidelines.
Scope: department compliance scores, emerging institutional risks, executive briefings and readiness calendars.
Restrict: no granular technical security configurations or raw credentials.""",

    "read_only_assessor": """Role: Read-Only Assessor (Board / Regulator). Tone: informative, conversational.
Frameworks: all — DPDP Act 2023, ISO 27001:2022, NIST CSF 2.0, CERT-In 2022, UGC Guidelines, NAAC Criteria.
Scope: conversational Q&A on compliance regulations, framework mappings, GRC definitions.
Restrict: no user names, vendor contacts, or raw database table contents.""",
}


def get_role_context(role: str) -> str:
    """
    Returns role-specific instructions matching the user's JWT role mapping.
    Injected server-side after JWT validation — the LLM never determines its own permissions.
    """
    if not role:
        return ""
    role_key = role.lower().replace(" ", "_")
    return ROLE_CONTEXTS.get(role_key, f"Role: {role}. Answer only from provided regulatory context.")
