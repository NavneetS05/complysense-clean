# Use: Compliance gap analysis and regulatory obligation checking.

from typing import Any, Dict, List
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.compliance import COMPLIANCE_TRIAGE_PROMPT, COMPLIANCE_CHANGE_PROMPT


class ComplianceAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="compliance_officer", endpoint_name="chat")

    async def triage(
        self,
        incident_log: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Priority triage of an incident log against ISO 27001 and CERT-In.
        """
        return await self.execute(
            query="Perform priority triage on this incident log.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=COMPLIANCE_TRIAGE_PROMPT,
            extra_context=incident_log,
            endpoint_name="triage",
        )

    async def regulatory_change(
        self,
        circular_text: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Gap analysis comparing a new regulatory circular against internal compliance posture.
        """
        return await self.execute(
            query="Analyze this regulatory circular for compliance gaps.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=COMPLIANCE_CHANGE_PROMPT,
            extra_context=circular_text,
            endpoint_name="regulatory_change",
        )

