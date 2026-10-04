"""
Cortex Engineering — FastAPI Application Factory.

Creates and configures the FastAPI application with:
- CORS middleware
- Structured exception handlers
- API router mounting
- Startup/shutdown lifecycle events
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import CortexError
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager — runs on startup and shutdown."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info(
        "cortex_starting",
        version=settings.app_version,
        embedding_provider=settings.embedding_provider,
        llm_provider=settings.llm_provider,
        jev_enabled=settings.jev_enabled,
    )
    yield
    logger.info("cortex_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Codebase Intelligence Platform",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ───────────────────────────────────────────────

    @app.exception_handler(CortexError)
    async def cortex_exception_handler(request: Request, exc: CortexError) -> JSONResponse:
        """Handle all domain exceptions with consistent error format."""
        logger.warning(
            "cortex_error",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Catch-all for unhandled exceptions. Never expose stack traces to clients."""
        logger.error(
            "unhandled_exception",
            path=request.url.path,
            error=str(exc),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": None,
                }
            },
        )

    # ── Routes ───────────────────────────────────────────────────────────
    app.include_router(api_router)

    return app


# Application instance — used by uvicorn
app = create_app()
