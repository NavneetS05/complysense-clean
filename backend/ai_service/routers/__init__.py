# Use: Registers all AI routers.

from fastapi import FastAPI
from ai_service.routers.assessor import router as assessor_router
from ai_service.routers.audit import router as audit_router
from ai_service.routers.compliance import router as compliance_router
from ai_service.routers.dept import router as dept_router
from ai_service.routers.digest import router as digest_router
from ai_service.routers.policy import router as policy_router
from ai_service.routers.security import router as security_router
from ai_service.routers.vendor import router as vendor_router
from ai_service.routers.admin import router as admin_router


def register_all_routers(app: FastAPI) -> None:
    app.include_router(assessor_router)
    app.include_router(audit_router)
    app.include_router(compliance_router)
    app.include_router(dept_router)
    app.include_router(digest_router)
    app.include_router(policy_router)
    app.include_router(security_router)
    app.include_router(vendor_router)
    app.include_router(admin_router)
