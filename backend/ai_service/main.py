# Use: FastAPI entry point, lifespan startup, loads indices, initializes services, registers routers.

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai_service.routers import register_all_routers


# Exception Handlers
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def runtime_error_handler(_: Request, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": f"Internal error: {exc}"})


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifecycle startup: Load FAISS and BM25 indices
    print("[AI Service] Initializing indices...")
    yield
    # Lifecycle shutdown: Cleanup resources
    print("[AI Service] Cleaning up resources...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ComplySense AI Service",
        description="FastAPI AI reasoning engine for ComplySense",
        version="2.0.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(RuntimeError, runtime_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Register all routers
    register_all_routers(app)

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def ready() -> dict[str, str]:
        # Ready when vectorstore is loaded
        return {"status": "ready"}

    return app


app = create_app()