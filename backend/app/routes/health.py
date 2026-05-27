"""Health-check endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/health/ready")
async def readiness():
    return {"ready": True}
