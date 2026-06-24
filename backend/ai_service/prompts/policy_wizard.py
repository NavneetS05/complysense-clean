from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PolicyWizardSchema:
    policy_type: str
    scope: list[str]
    data_types: list[str]
    applicable_frameworks: list[str]
    retention_period: str
    special_requirements: dict[str, Any]


def build_policy_wizard_payload(form_data: dict[str, Any]) -> PolicyWizardSchema:
    return PolicyWizardSchema(
        policy_type=form_data.get("policy_type", ""),
        scope=form_data.get("scope", []),
        data_types=form_data.get("data_types", []),
        applicable_frameworks=form_data.get("applicable_frameworks", []),
        retention_period=form_data.get("retention_period", ""),
        special_requirements=form_data.get("special_requirements", {}),
    )
