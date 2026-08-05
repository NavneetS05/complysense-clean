# Use: Defines custom HTTP exceptions and registers centralized FastAPI exception handlers.

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

_log = logging.getLogger("complysense.exceptions")


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Authentication is required") -> None:
        super().__init__(401, "UNAUTHORIZED", message)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(403, "FORBIDDEN", message)


class LockedError(AppError):
    def __init__(self, message: str = "Account is temporarily locked", blocked_until: str | None = None) -> None:
        super().__init__(423, "LOCKED", message)
        self.blocked_until = blocked_until


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        content = {"error": {"code": exc.code, "message": exc.message}}
        if hasattr(exc, "blocked_until") and exc.blocked_until:
            content["error"]["blocked_until"] = exc.blocked_until
            content["blocked_until"] = exc.blocked_until
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for any unhandled Python exception.

        WHY THIS EXISTS:
        Starlette's middleware stack order is (outermost first):
          [0] ServerErrorMiddleware
          [1] CORSMiddleware          <- added by app.add_middleware()
          [2] ExceptionMiddleware     <- handles registered exception_handlers
          [3] Router

        When an exception escapes layer 2 unhandled, ServerErrorMiddleware at
        layer 0 catches it and returns a bare 500 — but CORSMiddleware at layer
        1 never sees that response, so no Access-Control-Allow-Origin header is
        attached. The browser then reports it as a CORS block, masking the real
        500 error underneath.

        Registering a handler for the base Exception class here means
        ExceptionMiddleware (layer 2) catches it first, builds a JSON 500
        response, and that response flows outward through CORSMiddleware (layer
        1) which adds CORS headers. The browser now gets a proper 500 JSON body
        with CORS headers — the real error is visible instead of a CORS mystery.
        """
        _log.error(
            "Unhandled exception on %s %s\n%s",
            request.method,
            request.url.path,
            traceback.format_exc(),
        )
        detail = str(exc) if str(exc) else type(exc).__name__
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": detail}},
        )
