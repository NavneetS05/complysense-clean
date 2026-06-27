# Use: CERT-In reporting, incident analysis and security guidance.

from ai_service.agents.base import BaseAgent


class SecurityAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="it_security")
