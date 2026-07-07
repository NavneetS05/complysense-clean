# Use: Vendor agreement, SOC2, DPA and contract analysis.

from typing import Any, Dict, List
from ai_service.agents.base import BaseAgent
from ai_service.prompts.tasks.vendor import VENDOR_CONTRACT_PROMPT


class VendorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="vendor_reviewer", endpoint_name="chat")

    async def analyze_contract(
        self,
        contract_text: str,
        conversation_history: List[Dict[str, str]],
        institution_id: str,
        user_id: str = "",
    ) -> Dict[str, Any]:
        """
        Analyzes a vendor contract, DPA, or SOC2 report for DPDP and ISO 27001 compliance.
        """
        return await self.execute(
            query="Analyze this vendor document for compliance risks.",
            conversation_history=conversation_history,
            institution_id=institution_id,
            user_id=user_id,
            task_prompt=VENDOR_CONTRACT_PROMPT,
            extra_context=contract_text,
            endpoint_name="analyze_contract",
        )

