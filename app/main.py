"""
Personalized Networking Assistant — FastAPI Application Entry Point.

This module wires together all routers, middleware, exception handlers,
and lifecycle events to produce a production-ready ASGI application.

Usage:
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models.responses import ErrorResponse, HealthResponse
from app.routers import analyze, factcheck, feedback, generate, history
from app.utils.exceptions import AppBaseException
from app.utils.logger import get_logger, setup_logging

# Initialize logging at import time so all subsequent modules inherit it
setup_logging()
logger = get_logger(__name__)

_start_time: float = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown logic. Models are loaded lazily on first
    request, but we log startup metadata here.
    """
    settings = get_settings()
    logger.info(
        "Starting %s v%s | debug=%s",
        settings.app_name,
        settings.app_version,
        settings.debug,
    )
    yield
    logger.info("Shutting down %s.", settings.app_name)


def create_app() -> FastAPI:
    """
    Application factory — creates and configures the FastAPI instance.

    Returns:
        FastAPI: Fully configured application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # -----------------------------------------------------------------------
    # CORS Middleware
    # -----------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------
    # Request logging middleware
    # -----------------------------------------------------------------------
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Log every incoming request and its processing time."""
        start = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s | status=%d | %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response

    # -----------------------------------------------------------------------
    # Global exception handlers
    # -----------------------------------------------------------------------
    @app.exception_handler(AppBaseException)
    async def app_exception_handler(
        request: Request, exc: AppBaseException
    ) -> JSONResponse:
        """Return structured JSON for all application-level exceptions."""
        logger.warning(
            "AppBaseException: %s (status=%d)", exc.message, exc.status_code
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=type(exc).__name__,
                message=exc.message,
                status_code=exc.status_code,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all handler for unexpected errors."""
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="InternalServerError",
                message="An unexpected error occurred. Please try again.",
                status_code=500,
            ).model_dump(),
        )

    # -----------------------------------------------------------------------
    # Routers — all under /api/v1
    # -----------------------------------------------------------------------
    api_prefix = "/api/v1"
    app.include_router(analyze.router, prefix=api_prefix)
    app.include_router(generate.router, prefix=api_prefix)
    app.include_router(factcheck.router, prefix=api_prefix)
    app.include_router(history.router, prefix=api_prefix)
    app.include_router(feedback.router, prefix=api_prefix)

    # -----------------------------------------------------------------------
    # Health check endpoint
    # -----------------------------------------------------------------------
    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Health Check",
        description="Returns application health status and uptime.",
    )
    async def health_check() -> HealthResponse:
        """Return application health and uptime."""
        from app.services import generation_service, nlp_service  # lazy check

        return HealthResponse(
            status="ok",
            version=settings.app_version,
            uptime_seconds=round(time.time() - _start_time, 2),
            models_loaded={
                "zero_shot_classifier": nlp_service._classifier is not None,
                "text_generator": generation_service._generator is not None,
            },
        )

    @app.get("/", tags=["Root"], summary="API Root", include_in_schema=False)
    async def root() -> dict:
        """Return a simple welcome message with links."""
        return {
            "message": f"Welcome to {settings.app_name} API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health",
        }

    return app


# Create the ASGI application instance
app = create_app()
