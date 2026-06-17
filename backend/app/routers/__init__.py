# Use: Combines and builds the core API router that includes all resource sub-routers.

from fastapi import APIRouter

from app.config import get_settings
from app.routers import (
    assessments,
    audit,
    auth,
    calendar,
    controls,
    departments,
    evidence,
    health,
    incidents,
    institutions,
    modules,
    notifications,
    policies,
    rbac,
    users,
    vendors,
)


def build_api_router() -> APIRouter:
    settings = get_settings()
    api_router = APIRouter(prefix=f"/api/{settings.api_version}")
    api_router.include_router(auth.router)
    api_router.include_router(rbac.router)
    api_router.include_router(modules.router)
    api_router.include_router(institutions.router)
    api_router.include_router(users.router)
    api_router.include_router(departments.router)
    api_router.include_router(controls.router)
    api_router.include_router(assessments.router)
    api_router.include_router(evidence.router)
    api_router.include_router(incidents.router)
    api_router.include_router(vendors.router)
    api_router.include_router(policies.router)
    api_router.include_router(audit.router)
    api_router.include_router(notifications.router)
    api_router.include_router(calendar.router)
    return api_router


__all__ = ["build_api_router", "health"]
