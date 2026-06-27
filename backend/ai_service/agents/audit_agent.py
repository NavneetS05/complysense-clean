# Use: Smart evidence sampling and audit observation drafting.

from ai_service.agents.base import BaseAgent


class AuditAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="auditor")
