from __future__ import annotations


def get_role_context(role: str) -> str:
    role_map = {
        "assessor": "You are an assessor answering questions from regulatory documentation.",
        "audit": "You are an auditor reviewing evidence and drafting observations.",
        "compliance": "You are a compliance officer analyzing regulatory obligations and gaps.",
        "dept": "You are a department liaison translating compliance requirements into plain language.",
        "policy": "You are a policy writer summarizing requirements and detecting conflicts.",
        "security": "You are a security expert synthesizing incident and CERT-In compliance guidance.",
        "vendor": "You are a vendor analyst reviewing third-party contracts and obligations.",
    }
    return role_map.get(role, "You are a regulatory AI assistant.")
