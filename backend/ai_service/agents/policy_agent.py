# Use: Policy conflict detection and policy drafting assistance.

from ai_service.agents.base import BaseAgent


class PolicyAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="policy_approver")
