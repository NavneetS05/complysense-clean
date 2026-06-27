# Use: Role-based authorization checks before AI execution.

from typing import List


class RoleGuard:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def verify_role_access(self, user_role: str) -> bool:
        """
        Validates whether the user's role is authorized to invoke a particular endpoint/agent.
        """
        return user_role in self.allowed_roles
