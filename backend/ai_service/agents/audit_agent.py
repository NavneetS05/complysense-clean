# Use: Smart evidence sampling and audit observation drafting.

from typing import Any, Dict, List
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.audit import AUDIT_SAMPLE_SIZE_PROMPT, AUDIT_OBSERVATION_PROMPT


class AuditAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="auditor", endpoint_name="chat")

    async def smart_sample(
        self,
        control_details: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Calculates statistically valid audit sample sizes for control testing.
        """
        return await self.execute(
            query="Calculate the audit sample size for these controls.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=AUDIT_SAMPLE_SIZE_PROMPT,
            extra_context=control_details,
            endpoint_name="smart_sample",
        )

    async def draft_observation(
        self,
        finding_details: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Drafts a formal audit observation with Condition/Criteria/Cause/Effect/Recommendation.
        """
        return await self.execute(
            query="Draft a formal audit observation for this finding.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=AUDIT_OBSERVATION_PROMPT,
            extra_context=finding_details,
            endpoint_name="draft_observation",
        )

