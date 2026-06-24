# Use: Prepares and summarizes compliance and incident data for secure LLM consumption.

from __future__ import annotations

from typing import Any


class ContextBuilder:
    def build_for_compliance_officer(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = ["institution_name", "control_summary", "frameworks", "risk_findings"]
        return {k: data[k] for k in allowed_keys if k in data}

    def build_for_assessor(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = ["institution_name", "framework_summaries", "control_status", "compliance_scores"]
        return {k: data[k] for k in allowed_keys if k in data}

    def build_for_auditor(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = ["program_scope", "sample_results", "evidence_summary", "frameworks"]
        return {k: data[k] for k in allowed_keys if k in data}

    def build_for_policy_writer(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = ["policy_type", "scope", "data_types", "applicable_frameworks", "retention_period", "special_requirements"]
        return {k: data[k] for k in allowed_keys if k in data}

    def build_for_vendor_manager(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = ["contract_summary", "vendor_obligations", "risk_flags", "applicable_frameworks"]
        return {k: data[k] for k in allowed_keys if k in data}

    def build_for_security_officer(self, data: dict[str, Any]) -> dict[str, Any]:
        allowed_keys = ["incident_summary", "control_status", "cert_in_guidance", "framework_references"]
        return {k: data[k] for k in allowed_keys if k in data}
