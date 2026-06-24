from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from ai_service.rag import vectorstore as vs_module
from ai_service.rag.loader import load_all_frameworks, load_from_supabase
from ai_service.routers import build_ai_router


# ---------------------------------------------------------------------------
# EXCEPTION HANDLERS
# ---------------------------------------------------------------------------

async def _value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def _runtime_error_handler(_: Request, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": str(exc)})


async def _generic_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": f"Internal error: {exc}"})


# ---------------------------------------------------------------------------
# LIFESPAN — vectorstore is built once, loaded on every subsequent restart
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[AI Service] Starting up...")
    if vs_module.is_built():
        vs_module.load_vectorstore()
        print("[AI Service] Loaded existing FAISS index.")
    else:
        print("[AI Service] No existing index — building from knowledge base...")
        try:
            docs = load_all_frameworks()
        except FileNotFoundError:
            print("[AI Service] Local knowledge_base/ empty — attempting Supabase download...")
            docs = load_from_supabase()
        vs_module.build_vectorstore(docs)
        print(f"[AI Service] FAISS index built from {len(docs)} chunks.")

    print("[AI Service] Ready.")
    yield
    print("[AI Service] Shutting down.")


# ---------------------------------------------------------------------------
# APP FACTORY
# ---------------------------------------------------------------------------

def create_ai_app() -> FastAPI:
    app = FastAPI(
        title="ComplySense AI Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_exception_handler(ValueError, _value_error_handler)
    app.add_exception_handler(RuntimeError, _runtime_error_handler)
    app.add_exception_handler(Exception, _generic_handler)

    @app.get("/health/live", tags=["health"])
    async def live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    async def ready() -> dict[str, str]:
        try:
            vs_module.get_vectorstore()
            return {"status": "ready"}
        except RuntimeError:
            raise HTTPException(status_code=503, detail="Vectorstore not initialised yet.")

    app.include_router(build_ai_router())
    return app


app = create_ai_app()