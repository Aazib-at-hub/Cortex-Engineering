"""
Cortex Engineering — Health Check Endpoint.

Provides liveness and readiness probes for the application.
Checks database connectivity and reports service status.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.database.session import get_db

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    timestamp: str
    version: str
    database: str
    embedding_provider: str
    llm_provider: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns application health status including database connectivity.",
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check application health and database connectivity."""
    settings = get_settings()

    # Verify database connectivity
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    overall_status = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.app_version,
        database=db_status,
        embedding_provider=settings.embedding_provider,
        llm_provider=settings.llm_provider,
    )
