# Use: Middleware and dependencies for validating user permissions against required keys.

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.core.deps import get_current_user
from app.core.exceptions import ForbiddenError
from app.domain.rbac import PermissionKey
from app.schemas.auth import UserContext


def require_permission(permission: PermissionKey) -> Callable[..., UserContext]:
    async def dependency(user: Annotated[UserContext, Depends(get_current_user)]) -> UserContext:
        if permission.value not in user.permissions:
            raise ForbiddenError(f"Missing permission: {permission.value}")
        return user

    return dependency
