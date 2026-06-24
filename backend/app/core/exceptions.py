# Use: Defines custom HTTP exceptions and registers centralized FastAPI exception handlers.

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
        )

