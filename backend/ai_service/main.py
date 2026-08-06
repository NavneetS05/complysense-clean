# Use: FastAPI entry point — lifespan startup/shutdown, exception handlers, router registration.
# Lifespan: loads/builds indices once and keeps them in memory via HybridRetriever singleton.

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ai_service.utils.logger import StructuredLogger, configure_logging
from ai_service.routers import register_all_routers

logger = StructuredLogger("ai_service.main")

# Simple middleware to log any exception to stdout immediately (captures dependency errors)
class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            from fastapi import HTTPException
            if isinstance(exc, HTTPException):
                raise
            print(f"MIDDLEWARE CAUGHT EXCEPTION: {exc}")
            import traceback

            traceback.print_exc()
            raise

# Readiness flag — True once FAISS + BM25 are loaded in memory
_index_ready: bool = False


# ── Exception handlers ──────────────────────────────────────────────────────────

async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def runtime_error_handler(_: Request, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


import traceback


async def generic_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    try:
        tb = traceback.format_exc()
    except Exception:
        tb = "<traceback unavailable>"
    print(f"CRITICAL AI SERVICE EXCEPTION: {exc}\n{tb}", flush=True)
    logger.error("unhandled_exception", error=str(exc), traceback=tb)
    return JSONResponse(status_code=500, content={"detail": f"Internal error: {exc}"})


# ── Lifespan ────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _index_ready

    # Configure structured logging first
    from ai_service.config import get_ai_settings
    get_ai_settings.cache_clear()
    settings = get_ai_settings()
    configure_logging(settings.log_level)

    logger.info("ai_service.startup_begin")

    # ── Import here to avoid circular module load ──────────────────────────────
    from ai_service.rag.indexing.index_builder import IndexBuilder
    from ai_service.agents.base import _get_retriever

    builder = IndexBuilder()

    if builder.is_built():
        # Indices exist on disk — load into memory via the retriever singleton
        logger.info("ai_service.loading_existing_indices")
        try:
            retriever = _get_retriever()
            retriever.reload_indices()
            _index_ready = True
            logger.info("ai_service.indices_loaded")
        except Exception as exc:
            logger.warning(
                "ai_service.load_failed_rebuilding",
                error=str(exc),
            )
            try:
                await builder.run_reindex_pipeline(triggered_by="startup_fallback_rebuild")
                _get_retriever().reload_indices()
                _index_ready = True
                logger.info("ai_service.rebuild_complete")
            except Exception as exc2:
                logger.error(
                    "ai_service.rebuild_failed",
                    error=str(exc2),
                    detail="Service starting in degraded mode.",
                )
    else:
        # No vectorstore found — cold start
        logger.info("ai_service.cold_start_begin")
        try:
            await builder.run_reindex_pipeline(triggered_by="startup_cold_start")
            _get_retriever().reload_indices()
            _index_ready = True
            logger.info("ai_service.cold_start_complete")
        except Exception as exc:
            logger.error(
                "ai_service.cold_start_failed",
                error=str(exc),
                detail="Service starting in degraded mode. Use /admin/reindex to retry.",
            )

    yield

    # ── Shutdown ───────────────────────────────────────────────────────────────
    logger.info("ai_service.shutdown")


# ── App factory ─────────────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    from ai_service.config import get_ai_settings
    settings = get_ai_settings()

    app = FastAPI(
        title="ComplySense AI Service",
        description="Decoupled AI reasoning engine for ComplySense — RAG + Gemini 2.5 Flash",
        version="2.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ensure middleware catches and logs exceptions (including dependency errors)
    app.add_middleware(ExceptionLoggingMiddleware)

    # Register application-wide exception handlers from the main backend so
    # AppError/UnauthorizedError are handled consistently (returns 4xx for auth/perm failures).
    try:
        from app.core.exceptions import register_exception_handlers
        register_exception_handlers(app)
    except ImportError:
        pass

    # Keep specific lightweight handlers for common error classes
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(RuntimeError, runtime_error_handler)

    register_all_routers(app)

    @app.get("/health/live", tags=["Health"])
    async def live() -> dict:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["Health"])
    async def ready() -> dict:
        """Returns ready=true only once FAISS + BM25 indices are loaded in memory."""
        return {
            "status": "ready" if _index_ready else "initializing",
            "index_ready": _index_ready,
        }

    return app


app = create_app()
