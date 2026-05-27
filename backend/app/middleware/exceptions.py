"""Global exception handlers."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.logger import get_logger

logger = get_logger("edunova.exceptions")


class EduNovaError(Exception):
    """Base exception class for application-level errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GuardrailViolation(EduNovaError):
    def __init__(self, message: str = "Content blocked by guardrails."):
        super().__init__(message, status_code=403)


class EvaluationFailure(EduNovaError):
    def __init__(self, message: str = "Response failed quality evaluation."):
        super().__init__(message, status_code=422)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all exception handlers to the FastAPI app."""

    @app.exception_handler(EduNovaError)
    async def handle_app_error(request: Request, exc: EduNovaError):
        logger.warning("app_error path=%s message=%s", request.url.path, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": exc.__class__.__name__},
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "type": "HTTPException"},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        logger.info("validation_error path=%s errors=%s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        logger.exception("unhandled_error path=%s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "type": "ServerError"},
        )
