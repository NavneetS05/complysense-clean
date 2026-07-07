# Use: Policy conflict detection and policy drafting assistance.

from typing import Any, Dict, List
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.policy import POLICY_CONFLICT_PROMPT, POLICY_EXECUTIVE_SUMMARY_PROMPT


class PolicyAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="policy_approver", endpoint_name="chat")

    async def conflict_detect(
        self,
        policy_text: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Validates a policy draft against retrieved frameworks, detecting conflicts and missing clauses.
        """
        return await self.execute(
            query="Detect conflicts and missing clauses in this policy document.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=POLICY_CONFLICT_PROMPT,
            extra_context=policy_text,
            endpoint_name="conflict_detect",
        )

    async def executive_summary(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Generates an executive compliance briefing for university leadership.
        """
        return await self.execute(
            query=query,
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=POLICY_EXECUTIVE_SUMMARY_PROMPT,
            endpoint_name="executive_summary",
        )

