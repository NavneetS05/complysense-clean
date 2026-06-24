from __future__ import annotations

from typing import Sequence

ENDPOINT_ROLE_MAP: dict[str, Sequence[str]] = {
    "compliance": ["compliance_officer", "admin"],
    "security": ["security_officer", "admin"],
    "audit": ["auditor", "admin"],
    "dept": ["department_head", "admin"],
    "vendor": ["vendor_manager", "admin"],
    "policy": ["policy_writer", "admin"],
    "assessor": ["assessor", "admin"],
    "digest": ["compliance_officer", "admin"],
}


def has_role_access(endpoint: str, role: str) -> bool:
    allowed = ENDPOINT_ROLE_MAP.get(endpoint, [])
    return role in allowed
