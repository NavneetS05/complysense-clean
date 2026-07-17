import importlib
import os
import sys
import types
from pathlib import Path

from fastapi import FastAPI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "service-key")
os.environ.setdefault("SECRET_KEY", "test-secret-that-is-long-enough-for-validation")

routers_pkg = types.ModuleType("app.routers")
routers_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "app" / "routers")]
sys.modules.setdefault("app.routers", routers_pkg)

ai_pkg = types.ModuleType("app.routers.ai")
ai_pkg.__path__ = [str(Path(__file__).resolve().parents[1] / "app" / "routers" / "ai")]
sys.modules.setdefault("app.routers.ai", ai_pkg)

assessor_router = importlib.import_module("app.routers.ai.assessor").router
compliance_router = importlib.import_module("app.routers.ai.compliance").router
security_router = importlib.import_module("app.routers.ai.security").router
vendor_router = importlib.import_module("app.routers.ai.vendor").router
audit_router = importlib.import_module("app.routers.ai.audit").router
dept_router = importlib.import_module("app.routers.ai.dept").router


def test_ai_chat_proxy_routes_are_registered() -> None:
    app = FastAPI()
    app.include_router(assessor_router, prefix="/api/v1/ai")
    app.include_router(compliance_router, prefix="/api/v1/ai")
    app.include_router(security_router, prefix="/api/v1/ai")
    app.include_router(vendor_router, prefix="/api/v1/ai")
    app.include_router(audit_router, prefix="/api/v1/ai")
    app.include_router(dept_router, prefix="/api/v1/ai")

    paths = {route.path for route in app.routes if getattr(route, "path", None)}

    expected_paths = {
        "/api/v1/ai/assessor/chat",
        "/api/v1/ai/compliance/chat",
        "/api/v1/ai/security/chat",
        "/api/v1/ai/vendor/chat",
        "/api/v1/ai/audit/chat",
        "/api/v1/ai/dept/chat",
    }

    assert expected_paths.issubset(paths)
