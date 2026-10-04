"""
Cortex Engineering — Repository API Routes.

Endpoints for importing repositories, checking indexing status,
listing files, retrieving file details, reindexing, and deletion.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id
from app.database.session import async_session_maker, get_db
from app.schemas.repository import (
    ChunkResponse,
    FileDetailResponse,
    FileResponse,
    ImportRepositoryRequest,
    RepositoryDetailResponse,
    RepositoryResponse,
    RepositoryStatusResponse,
)
from app.services.repository_service import RepositoryService

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post(
    "/import",
    response_model=RepositoryResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Import a GitHub repository",
)
async def import_repository(
    data: ImportRepositoryRequest,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> RepositoryResponse:
    """Import a public GitHub repository and begin background indexing."""
    service = RepositoryService(db, async_session_maker)
    repo = await service.import_repository(
        user_id=current_user_id,
        github_url=data.github_url,
        branch=data.branch,
    )
    return RepositoryResponse.model_validate(repo)


@router.get(
    "",
    response_model=list[RepositoryResponse],
    summary="List all user repositories",
)
async def list_repositories(
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[RepositoryResponse]:
    """Retrieve all repositories imported by current user."""
    service = RepositoryService(db, async_session_maker)
    repos = await service.list_repositories(current_user_id)
    return [RepositoryResponse.model_validate(r) for r in repos]


@router.get(
    "/{repo_id}",
    response_model=RepositoryDetailResponse,
    summary="Get repository details",
)
async def get_repository(
    repo_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> RepositoryDetailResponse:
    """Retrieve repository information including file tree."""
    service = RepositoryService(db, async_session_maker)
    repo = await service.get_repository(repo_id, current_user_id)
    files = await service.list_files(repo_id, current_user_id)

    resp = RepositoryDetailResponse.model_validate(repo)
    resp.files = [FileResponse.model_validate(f) for f in files]
    return resp


@router.get(
    "/{repo_id}/status",
    response_model=RepositoryStatusResponse,
    summary="Get repository indexing status",
)
async def get_repository_status(
    repo_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> RepositoryStatusResponse:
    """Poll current indexing progress and counts."""
    service = RepositoryService(db, async_session_maker)
    repo = await service.get_repository(repo_id, current_user_id)
    return RepositoryStatusResponse.model_validate(repo)


@router.get(
    "/{repo_id}/files",
    response_model=list[FileResponse],
    summary="List repository files",
)
async def list_repository_files(
    repo_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[FileResponse]:
    """Retrieve all indexed files in repository."""
    service = RepositoryService(db, async_session_maker)
    files = await service.list_files(repo_id, current_user_id)
    return [FileResponse.model_validate(f) for f in files]


@router.get(
    "/{repo_id}/files/{file_id}",
    response_model=FileDetailResponse,
    summary="Get file content and chunks",
)
async def get_file_detail(
    repo_id: UUID,
    file_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> FileDetailResponse:
    """Fetch file metadata and chunk segments for code viewer."""
    service = RepositoryService(db, async_session_maker)
    file_rec, chunks = await service.get_file_detail(repo_id, file_id, current_user_id)

    full_content = _reconstruct_content(chunks)
    resp = FileDetailResponse.model_validate(file_rec)
    resp.content = full_content
    resp.chunks = [ChunkResponse.model_validate(c) for c in chunks]
    return resp


def _reconstruct_content(chunks: list) -> str:
    """
    Rebuild file text from overlapping chunks using their line ranges.

    Chunks overlap (CHUNK_OVERLAP), so concatenation would duplicate lines.
    Each line is written once at its 1-indexed position.
    """
    if not chunks:
        return ""
    lines: dict[int, str] = {}
    for chunk in chunks:
        for offset, text in enumerate(chunk.content.split("\n")):
            lines.setdefault(chunk.start_line + offset, text)
    max_line = max(lines)
    return "\n".join(lines.get(i, "") for i in range(1, max_line + 1))


@router.post(
    "/{repo_id}/reindex",
    response_model=RepositoryResponse,
    summary="Re-index repository",
)
async def reindex_repository(
    repo_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> RepositoryResponse:
    """Reset repository status and rerun full indexing pipeline."""
    service = RepositoryService(db, async_session_maker)
    repo = await service.reindex_repository(repo_id, current_user_id)
    return RepositoryResponse.model_validate(repo)


@router.delete(
    "/{repo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete repository",
)
async def delete_repository(
    repo_id: UUID,
    current_user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Permanently delete repository, files, chunks, and conversations."""
    service = RepositoryService(db, async_session_maker)
    await service.delete_repository(repo_id, current_user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

