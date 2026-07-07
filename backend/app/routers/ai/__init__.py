# Use: Exports the central AI proxy APIRouter that bundles all role-specific sub-routers.

from fastapi import APIRouter
from app.routers.ai.compliance import router as compliance_router
from app.routers.ai.security import router as security_router
from app.routers.ai.audit import router as audit_router
from app.routers.ai.policy import router as policy_router
from app.routers.ai.vendor import router as vendor_router
from app.routers.ai.admin import router as admin_router
from app.routers.ai.dept import router as dept_router


def build_ai_router() -> APIRouter:
    router = APIRouter()
    router.include_router(compliance_router)
    router.include_router(security_router)
    router.include_router(audit_router)
    router.include_router(policy_router)
    router.include_router(vendor_router)
    router.include_router(admin_router)
    router.include_router(dept_router)
    return router
