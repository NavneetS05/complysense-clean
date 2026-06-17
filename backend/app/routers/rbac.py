# Use: Router for inspecting active roles and permissions.

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.permissions import require_permission
from app.domain.rbac import PermissionKey, ROLE_ROUTE_PREFIXES, RoleName
from app.schemas.auth import UserContext

router = APIRouter(prefix="/rbac", tags=["rbac"])


@router.get("/roles")
async def roles(
    _: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_ROLES))],
) -> dict[str, object]:
    return {
        "roles": [role.value for role in RoleName],
        "role_route_prefixes": {role.value: prefix for role, prefix in ROLE_ROUTE_PREFIXES.items()},
    }
