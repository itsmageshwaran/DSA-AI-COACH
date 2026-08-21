"""Global exception handlers for translating application errors into JSON responses."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from src.core.logging.logger import logger


class ApplicationException(Exception):
    """Base class for domain-specific errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


def _error_response(message: str, status_code: int) -> JSONResponse:
    """Standardized JSON error payload."""
    payload = {
        "error": {
            "message": message,
            "code": status_code,
        },
    }
    return JSONResponse(status_code=status_code, content=payload)


def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTP exceptions."""
    req_id = getattr(request.state, "request_id", None)
    logger.error("HTTPException: {}", exc.detail, request_id=req_id)
    return _error_response(str(exc.detail), exc.status_code)


def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle request validation exceptions."""
    req_id = getattr(request.state, "request_id", None)
    logger.error("ValidationError: {}", exc.errors(), request_id=req_id)
    return _error_response("Request validation failed", status.HTTP_422_UNPROCESSABLE_ENTITY)


def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic data validation errors."""
    req_id = getattr(request.state, "request_id", None)
    logger.error("PydanticError: {}", exc.errors(), request_id=req_id)
    return _error_response("Data validation error", status.HTTP_400_BAD_REQUEST)


def application_exception_handler(request: Request, exc: ApplicationException) -> JSONResponse:
    """Handle domain application exceptions."""
    req_id = getattr(request.state, "request_id", None)
    logger.error("ApplicationException: {}", exc.detail, request_id=req_id)
    return _error_response(exc.detail, exc.status_code)


def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    req_id = getattr(request.state, "request_id", None)
    logger.exception("Unhandled exception", request_id=req_id)
    return _error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to FastAPI application."""
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, pydantic_validation_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ApplicationException, application_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
