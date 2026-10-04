"""
Cortex Engineering — Common Response Schemas.

Shared response structures used across multiple API endpoints.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Standard error response body."""

    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Wrapper for error responses."""

    error: ErrorDetail


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str
