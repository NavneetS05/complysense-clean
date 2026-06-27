# Use: Vendor agreement, SOC2, DPA and contract analysis.

from ai_service.agents.base import BaseAgent


class VendorAgent(BaseAgent):
    def __init__(self):
        super().__init__(role="vendor_reviewer")
