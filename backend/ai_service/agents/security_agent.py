# Use: CERT-In reporting, incident analysis and security guidance.

from typing import Any, Dict, List
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.security import SECURITY_CERT_IN_DRAFT_PROMPT


class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="it_security", endpoint_name="chat")

    async def cert_in_draft(
        self,
        incident_details: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Drafts an official CERT-In cybersecurity incident report from incident details.
        """
        return await self.execute(
            query="Draft a CERT-In cybersecurity incident report.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=SECURITY_CERT_IN_DRAFT_PROMPT,
            extra_context=incident_details,
            endpoint_name="cert_in_draft",
        )

