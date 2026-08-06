# Use: Read-only assessor Q&A and framework interpretation.

from typing import Any, Dict, List
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.assessor import ASSESSOR_TASK_PROMPT


class AssessorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="read_only_assessor", endpoint_name="chat")

    async def chat(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
        user_role: str = "",
    ) -> Dict[str, Any]:
        """
        General regulatory Q&A from framework knowledge base.
        """
        return await self.execute(
            query=query,
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            user_role=user_role,
            task_prompt=ASSESSOR_TASK_PROMPT,
            endpoint_name="chat",
        )

