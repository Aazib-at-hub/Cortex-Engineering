"""
Cortex Engineering — Ingestion Pipeline Orchestrator.

Coordinates cloning, file discovery, filtering, extraction, line-aware chunking,
embedding generation, and database persistence with status reporting.
"""

from __future__ import annotations

import shutil
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.chunking.chunker import chunk_text
from app.core.config import Settings
from app.core.logging import get_logger
from app.embeddings.base import BaseEmbeddingService
from app.ingestion.cloner import clone_repository
from app.ingestion.discovery import discover_files
from app.ingestion.extractor import extract_content
from app.models.chunk import CodeChunk
from app.models.file import RepositoryFile
from app.repositories.chunk_repo import ChunkRepository
from app.repositories.file_repo import FileRepository
from app.repositories.repository_repo import RepositoryRepository

logger = get_logger("pipeline")


class IngestionPipeline:
    """Full repository ingestion and indexing workflow."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        embedding_service: BaseEmbeddingService,
        settings: Settings,
    ) -> None:
        self._session_factory = session_factory
        self._embedding_service = embedding_service
        self._settings = settings

    async def run(self, repository_id: UUID) -> None:
        """Execute complete ingestion pipeline for a repository."""
        logger.info("Starting repository ingestion", repo_id=str(repository_id))
        clone_dest: Path | None = None

        async with self._session_factory() as session:
            repo_dao = RepositoryRepository(session)
            repo = await repo_dao.get_by_id_unscoped(repository_id)
            if not repo:
                logger.error("Repository not found for ingestion", repo_id=str(repository_id))
                return

            github_url = repo.github_url
            branch = repo.branch or "main"

            # Transition status -> CLONING
            await repo_dao.update_status(repository_id, "CLONING")
            await session.commit()

        try:
            # 1. Clone repository
            clone_dest = Path(self._settings.repo_clone_dir) / str(repository_id)
            await clone_repository(
                github_url=github_url,
                target_dir=clone_dest,
                branch=branch,
            )

            # 2. File discovery & filtering
            async with self._session_factory() as session:
                repo_dao = RepositoryRepository(session)
                await repo_dao.update_status(repository_id, "INDEXING")
                await session.commit()

            discovered = discover_files(
                repo_root=clone_dest,
                max_file_size_bytes=self._settings.max_file_size_bytes,
            )

            if not discovered:
                logger.warning("No indexable files discovered", repo_id=str(repository_id))
                async with self._session_factory() as session:
                    repo_dao = RepositoryRepository(session)
                    await repo_dao.update_status(
                        repository_id,
                        status="READY",
                        file_count=0,
                        chunk_count=0,
                        languages={},
                        last_indexed_at=datetime.now(timezone.utc),
                    )
                    await session.commit()
                return

            # Compute language distribution
            lang_counts = Counter(d.language for d in discovered)
            total_files = len(discovered)
            languages_stat = {
                lang: round((count / total_files) * 100, 1)
                for lang, count in lang_counts.most_common()
            }

            # 3. Extract content and create chunks
            all_file_records: list[RepositoryFile] = []
            files_with_chunks: list[tuple[RepositoryFile, list[CodeChunk]]] = []
            all_chunks_to_embed: list[CodeChunk] = []

            for d in discovered:
                extracted = extract_content(d.absolute_path)
                if not extracted or not extracted.content.strip():
                    continue

                file_rec = RepositoryFile(
                    repository_id=repository_id,
                    path=d.relative_path,
                    filename=d.filename,
                    language=d.language,
                    size_bytes=d.size_bytes,
                    content_hash=extracted.content_hash,
                )
                all_file_records.append(file_rec)

                # Chunk content
                raw_chunks = chunk_text(
                    content=extracted.content,
                    chunk_size=self._settings.chunk_size,
                    chunk_overlap=self._settings.chunk_overlap,
                )

                chunk_records: list[CodeChunk] = []
                for tc in raw_chunks:
                    chunk_rec = CodeChunk(
                        repository_id=repository_id,
                        chunk_index=tc.chunk_index,
                        content=tc.content,
                        start_line=tc.start_line,
                        end_line=tc.end_line,
                        language=d.language,
                    )
                    chunk_records.append(chunk_rec)
                    all_chunks_to_embed.append(chunk_rec)

                files_with_chunks.append((file_rec, chunk_records))

            # 4. Generate embeddings in batches
            batch_size = 64
            chunk_contents = [c.content for c in all_chunks_to_embed]
            logger.info(
                "Generating embeddings for chunks",
                chunk_count=len(all_chunks_to_embed),
                batch_size=batch_size,
            )

            all_embeddings: list[list[float]] = []
            for i in range(0, len(chunk_contents), batch_size):
                batch_slice = chunk_contents[i : i + batch_size]
                batch_embeddings = await self._embedding_service.embed_texts(batch_slice)
                all_embeddings.extend(batch_embeddings)

            # Assign embeddings to chunks
            for chunk_obj, emb in zip(all_chunks_to_embed, all_embeddings):
                chunk_obj.embedding = emb

            # 5. Persist files and chunks in DB
            async with self._session_factory() as session:
                file_dao = FileRepository(session)
                chunk_dao = ChunkRepository(session)
                repo_dao = RepositoryRepository(session)

                for file_rec, chunk_list in files_with_chunks:
                    saved_file = await file_dao.create(file_rec)
                    for c in chunk_list:
                        c.file_id = saved_file.id
                    if chunk_list:
                        await chunk_dao.create_batch(chunk_list)

                # Transition status -> READY
                await repo_dao.update_status(
                    repository_id,
                    status="READY",
                    file_count=len(all_file_records),
                    chunk_count=len(all_chunks_to_embed),
                    languages=languages_stat,
                    last_indexed_at=datetime.now(timezone.utc),
                )
                await session.commit()

            logger.info(
                "Repository ingestion completed successfully",
                repo_id=str(repository_id),
                files=len(all_file_records),
                chunks=len(all_chunks_to_embed),
            )

        except Exception as exc:
            err_msg = f"{type(exc).__name__}: {str(exc)}"
            tb = traceback.format_exc()
            logger.error(
                "Ingestion pipeline failed",
                repo_id=str(repository_id),
                error=err_msg,
                traceback=tb,
            )
            async with self._session_factory() as session:
                repo_dao = RepositoryRepository(session)
                await repo_dao.update_status(
                    repository_id,
                    status="FAILED",
                    error_message=err_msg,
                )
                await session.commit()

        finally:
            # Clean up cloned local files
            if clone_dest and clone_dest.exists():
                logger.info("Cleaning clone directory", path=str(clone_dest))
                shutil.rmtree(clone_dest, ignore_errors=True)
