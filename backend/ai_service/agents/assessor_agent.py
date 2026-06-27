# Use: Read-only assessor Q&A and framework interpretation.

from ai_service.agents.base import BaseAgent


class AssessorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="read_only_assessor")
