# Use: Combines and exports AI service routes.

from fastapi import APIRouter

from ai_service.routers import admin, assessor, audit, compliance, dept, digest, policy, security, vendor


def build_ai_router() -> APIRouter:
    router = APIRouter(prefix="/ai")
    router.include_router(compliance.router)
    router.include_router(security.router)
    router.include_router(audit.router)
    router.include_router(dept.router)
    router.include_router(vendor.router)
    router.include_router(policy.router)
    router.include_router(assessor.router)
    router.include_router(admin.router)
    router.include_router(digest.router)
    return router
