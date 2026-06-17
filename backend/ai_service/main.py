# Use: Entry point for the AI FastAPI microservice running on port 8001.

from fastapi import FastAPI

from ai_service.routers import build_ai_router
from app.core.exceptions import register_exception_handlers


def create_ai_app() -> FastAPI:
    app = FastAPI(title="ComplySense AI Service", version="1.0.0")
    register_exception_handlers(app)

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(build_ai_router())
    return app


app = create_ai_app()
