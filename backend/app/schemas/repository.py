"""
Cortex Engineering — Repository Schemas.

Request and response schemas for repository import, listing, and status.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ── Requests ─────────────────────────────────────────────────────────────────


class ImportRepositoryRequest(BaseModel):
    """Repository import request."""

    github_url: str = Field(
        ...,
        description="Public GitHub repository URL",
        examples=["https://github.com/owner/repo"],
    )
    branch: str = Field(
        default="main",
        description="Branch to index",
        max_length=255,
    )

    @field_validator("github_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Validate that the URL is a valid GitHub repository URL."""
        import re

        pattern = r"^https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/?$"
        if not re.match(pattern, v.rstrip("/")):
            raise ValueError(
                "URL must be a valid GitHub repository URL "
                "(e.g., https://github.com/owner/repo)"
            )
        return v.rstrip("/")


# ── Responses ────────────────────────────────────────────────────────────────


class RepositoryResponse(BaseModel):
    """Repository summary for listing."""

    id: UUID
    name: str
    github_url: str
    branch: str
    status: str
    file_count: int
    chunk_count: int
    languages: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RepositoryDetailResponse(RepositoryResponse):
    """Extended repository details including files."""

    files: list[FileResponse] = []


class FileResponse(BaseModel):
    """File summary."""

    id: UUID
    path: str
    filename: str
    language: str
    size_bytes: int

    model_config = {"from_attributes": True}


class FileDetailResponse(FileResponse):
    """File with content for source viewer."""

    content: Optional[str] = None
    chunks: list[ChunkResponse] = []


class ChunkResponse(BaseModel):
    """Code chunk summary."""

    id: UUID
    chunk_index: int
    start_line: int
    end_line: int
    language: str
    content: str

    model_config = {"from_attributes": True}


class RepositoryStatusResponse(BaseModel):
    """Lightweight status polling response."""

    id: UUID
    status: str
    file_count: int
    chunk_count: int
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


# Fix forward references
RepositoryDetailResponse.model_rebuild()
FileDetailResponse.model_rebuild()
