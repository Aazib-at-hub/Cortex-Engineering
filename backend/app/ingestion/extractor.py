"""
Cortex Engineering — File Content Extractor.

Reads file contents safely using multiple encodings and computes SHA-256 hashes
for deduplication and content integrity checks.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.core.logging import get_logger

logger = get_logger("extractor")


@dataclass(frozen=True)
class ExtractedContent:
    """Extracted text content and SHA256 hash."""

    content: str
    content_hash: str
    line_count: int


def extract_content(file_path: Path) -> Optional[ExtractedContent]:
    """
    Read text content from file_path, trying UTF-8 first, then Latin-1.

    Returns:
        ExtractedContent if read successfully, None otherwise.
    """
    try:
        raw_bytes = file_path.read_bytes()
    except OSError as err:
        logger.warning("Failed to read file", path=str(file_path), error=str(err))
        return None

    # Compute SHA256
    content_hash = hashlib.sha256(raw_bytes).hexdigest()

    # Decode text
    text: Optional[str] = None
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            text = raw_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue

    if text is None:
        logger.warning("Could not decode file content", path=str(file_path))
        return None

    lines = text.splitlines()
    return ExtractedContent(
        content=text,
        content_hash=content_hash,
        line_count=len(lines),
    )
