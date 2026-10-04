"""
Cortex Engineering — Root API Router.

Aggregates all versioned route modules into a single router
that the FastAPI application mounts.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.repositories import router as repositories_router

# Root API router — all v1 routes are prefixed with /api/v1
api_router = APIRouter(prefix="/api/v1")

# Mount route modules
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(repositories_router)
api_router.include_router(chat_router)
