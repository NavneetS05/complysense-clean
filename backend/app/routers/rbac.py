# Use: Router for inspecting active roles and permissions.

from typing import Annotated, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_permission
from app.database import get_db_session
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


@router.get("/matrix")
async def rbac_matrix(
    _: Annotated[UserContext, Depends(require_permission(PermissionKey.VIEW_ROLES))],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Generates the permission mapping matrix across all roles.
    If the database lacks seeded permissions, it falls back to a statically defined RBAC matrix.
    """
    try:
        # Fetch seeded roles and permissions from DB
        res = await session.execute(
            text(
                """
                select r.role_name, p.permission_key
                  from role_permissions rp
                  join roles r on r.role_id = rp.role_id
                  join permissions p on p.permission_id = rp.permission_id
                """
            )
        )
        mappings = res.all()

        # Build list of unique permission keys in the system
        p_keys_res = await session.execute(text("select permission_key from permissions order by permission_key"))
        all_permissions = [str(row[0]) for row in p_keys_res.all()]

        # If DB is empty, use static fallback matrix so UI still functions
        if not mappings or not all_permissions:
            all_permissions = [p.value for p in PermissionKey]
            # Populate fallback definitions
            fallback_matrix: dict[str, dict[str, bool]] = {}
            for p in all_permissions:
                fallback_matrix[p] = {r.value: False for r in RoleName}
                
                # Assign core permission logic to fallbacks
                if p == "view_roles":
                    fallback_matrix[p]["Super Admin"] = True
                    fallback_matrix[p]["Institution Admin"] = True
                elif p == "manage_institutions":
                    fallback_matrix[p]["Super Admin"] = True
                elif p == "view_audit_trail":
                    fallback_matrix[p]["Super Admin"] = True
                    fallback_matrix[p]["Institution Admin"] = True
                elif "view_" in p:
                    # Give read access to most roles for testing
                    for r in RoleName:
                        fallback_matrix[p][r.value] = True
                else:
                    # Admin/Officer permissions
                    fallback_matrix[p]["Super Admin"] = True
                    fallback_matrix[p]["Institution Admin"] = True
                    if "triage" in p or "compliance" in p or "controls" in p:
                        fallback_matrix[p]["Compliance Officer"] = True
                    if "security" in p or "incidents" in p:
                        fallback_matrix[p]["IT Security Officer"] = True

            return {
                "permissions": all_permissions,
                "matrix": fallback_matrix,
            }

        # Otherwise build from active database definitions
        matrix: dict[str, dict[str, bool]] = {}
        for p in all_permissions:
            matrix[p] = {r.value: False for r in RoleName}

        for role_name, permission_key in mappings:
            if permission_key in matrix and role_name in matrix[permission_key]:
                matrix[permission_key][role_name] = True

        return {
            "permissions": all_permissions,
            "matrix": matrix,
        }
    except Exception as exc:
        # Final safety check: static fallback
        all_permissions = [p.value for p in PermissionKey]
        fallback_matrix = {}
        for p in all_permissions:
            fallback_matrix[p] = {r.value: (r.value == "Super Admin") for r in RoleName}
        return {
            "permissions": all_permissions,
            "matrix": fallback_matrix,
            "error": str(exc),
        }
