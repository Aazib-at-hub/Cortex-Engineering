"""
Cortex Engineering — File Filtering & Language Detection.

Enforces boundaries on which files are processed: ignores build artifacts,
binary assets, package managers locks, and identifies source programming languages.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "venv",
    ".venv",
    "env",
    ".env",
    ".next",
    "dist",
    "build",
    "out",
    "target",
    "bin",
    "obj",
    ".idea",
    ".vscode",
    "vendor",
    "coverage",
    ".turbo",
    ".cache",
}

IGNORED_EXTENSIONS = {
    # Images & Media
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp", ".bmp", ".tiff",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".flv", ".webm",
    # Binaries & Archives
    ".exe", ".dll", ".so", ".dylib", ".bin", ".iso", ".dmg", ".msi",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".bz2", ".xz",
    # Fonts
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    # Generated / Data
    ".min.js", ".min.css", ".map", ".pyc", ".pyo", ".pyd",
    ".sqlite", ".sqlite3", ".db", ".class", ".jar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx",
}

IGNORED_FILENAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock",
    "composer.lock",
    "Gemfile.lock",
    ".DS_Store",
    "Thumbs.db",
}

EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "scss",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".xml": "xml",
    ".sql": "sql",
    ".md": "markdown",
    ".rst": "restructuredtext",
    ".txt": "text",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "bash",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".kt": "kotlin",
    ".swift": "swift",
    ".dart": "dart",
    ".lua": "lua",
    ".r": "r",
    ".dockerfile": "dockerfile",
}


def is_binary_string(bytes_sample: bytes) -> bool:
    """Check if byte chunk contains null bytes indicative of binary files."""
    return b"\x00" in bytes_sample


def detect_language(path: Path) -> str:
    """Detect language from filename or suffix."""
    name_lower = path.name.lower()
    if name_lower == "dockerfile" or name_lower.startswith("dockerfile."):
        return "dockerfile"
    if name_lower in ("makefile", "gnumakefile"):
        return "makefile"
    if name_lower in (".env.example", ".env.template"):
        return "config"

    suffix = path.suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(suffix, "plaintext")


def should_index_file(
    relative_path: Path,
    file_size_bytes: int,
    max_file_size_bytes: int = 1_048_576,
) -> tuple[bool, Optional[str]]:
    """
    Determine if file should be indexed into Cortex.

    Returns:
        (should_index, reason_if_ignored)
    """
    # Check directory components
    for part in relative_path.parts[:-1]:
        if part in IGNORED_DIRECTORIES or part.startswith("."):
            return False, f"Directory '{part}' is ignored"

    # Check filename
    filename = relative_path.name
    if filename in IGNORED_FILENAMES:
        return False, f"Filename '{filename}' is ignored"

    # Check file suffix
    suffix = relative_path.suffix.lower()
    if suffix in IGNORED_EXTENSIONS:
        return False, f"Extension '{suffix}' is ignored"

    # Check file size limit
    if file_size_bytes > max_file_size_bytes:
        return False, f"File size {file_size_bytes} exceeds limit {max_file_size_bytes}"

    # Empty file check
    if file_size_bytes == 0:
        return False, "File is empty"

    return True, None
