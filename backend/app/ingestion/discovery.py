"""
Cortex Engineering — File Tree Discovery.

Traverses cloned repository directories, applies filtering rules,
and yields metadata for eligible files.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.core.logging import get_logger
from app.ingestion.filter import detect_language, is_binary_string, should_index_file

logger = get_logger("discovery")


@dataclass(frozen=True)
class DiscoveredFile:
    """Metadata for an eligible file found in the repository."""

    absolute_path: Path
    relative_path: str
    filename: str
    language: str
    size_bytes: int


def discover_files(
    repo_root: Path,
    max_file_size_bytes: int = 1_048_576,
    max_total_files: int = 2000,
) -> list[DiscoveredFile]:
    """
    Recursively scan repo_root and return list of DiscoveredFile objects.

    Args:
        repo_root: Absolute root directory of cloned repo.
        max_file_size_bytes: Max allowed size per file.
        max_total_files: Upper limit on total indexed files per repository.

    Returns:
        List of DiscoveredFile metadata instances.
    """
    discovered: list[DiscoveredFile] = []
    repo_root_resolved = repo_root.resolve()

    for root, dirs, files in os.walk(repo_root_resolved):
        root_path = Path(root)

        # In-place prune ignored directories so os.walk skips descending into them
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in {
                "node_modules",
                "__pycache__",
                "venv",
                ".venv",
                "env",
                "dist",
                "build",
                "target",
                "vendor",
            }
        ]

        for fname in files:
            if len(discovered) >= max_total_files:
                logger.warning(
                    "Hit max file limit for repository",
                    limit=max_total_files,
                )
                return discovered

            file_abs = root_path / fname
            try:
                rel_path = file_abs.relative_to(repo_root_resolved)
                size = file_abs.stat().st_size
            except (OSError, ValueError):
                continue

            should_index, reason = should_index_file(
                rel_path, size, max_file_size_bytes
            )
            if not should_index:
                continue

            # Quick binary check on first 1024 bytes
            try:
                with open(file_abs, "rb") as f:
                    chunk = f.read(1024)
                    if is_binary_string(chunk):
                        continue
            except OSError:
                continue

            lang = detect_language(rel_path)
            # Use forward slashes for stored paths
            normalized_rel_path = rel_path.as_posix()

            discovered.append(
                DiscoveredFile(
                    absolute_path=file_abs,
                    relative_path=normalized_rel_path,
                    filename=fname,
                    language=lang,
                    size_bytes=size,
                )
            )

    logger.info("File discovery complete", total_files=len(discovered))
    return discovered
