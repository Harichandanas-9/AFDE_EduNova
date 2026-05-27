"""
EduNova AI - FastAPI Application Entry Point.

Configures middleware, routers, exception handlers, lifespan startup/shutdown,
and serves the OpenAPI docs.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database.session import init_db
from app.middleware.exceptions import register_exception_handlers
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes import (
    chat,
    health,
    quiz,
    recommendation,
    resume,
    skill,
    study_plan,
)
from app.utils.logger import get_logger, setup_logging

setup_logging()
logger = get_logger("edunova.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    logger.info(
        "Starting %s v%s in %s mode",
        settings.APP_NAME, settings.APP_VERSION, settings.ENVIRONMENT,
    )
    await init_db()
    logger.info("Application started successfully.")
    yield
    logger.info("Application shutting down.")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="EduNova AI - Your AI Career & Learning Copilot",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # --- CORS middleware ---
    # In DEBUG mode we use a regex that matches localhost on any port so dev
    # is friction-free. In production we honour the configured CORS_ORIGINS
    # list exactly. We never mix "*" with allow_credentials=True (browsers
    # silently reject that combination).
    if settings.DEBUG:
        app.add_middleware(
            CORSMiddleware,
            allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Other middleware (order matters — outermost last)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # --- Exception handlers ---
    register_exception_handlers(app)

    # --- Routers ---
    prefix = settings.API_V1_PREFIX
    app.include_router(health.router, prefix=prefix, tags=["Health"])
    app.include_router(chat.router, prefix=prefix, tags=["Chat"])
    app.include_router(quiz.router, prefix=prefix, tags=["Quiz"])
    app.include_router(study_plan.router, prefix=prefix, tags=["Study Plan"])
    app.include_router(resume.router, prefix=prefix, tags=["Resume"])
    app.include_router(skill.router, prefix=prefix, tags=["Skill Analysis"])
    app.include_router(recommendation.router, prefix=prefix, tags=["Recommendations"])

    @app.get("/", include_in_schema=False)
    async def root():
        return JSONResponse({
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "tagline": "Your AI Career & Learning Copilot",
            "docs": "/docs",
            "api": prefix,
        })

    return app


app = create_app()
