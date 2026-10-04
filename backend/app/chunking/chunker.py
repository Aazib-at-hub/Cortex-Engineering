"""
Cortex Engineering — Line-Aware Code and Text Chunker.

Splits source code and documentation into overlapping chunks strictly along
line boundaries, tracking exact 1-indexed start and end line numbers for source citation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    """A single chunk of code or text with line metadata."""

    chunk_index: int
    content: str
    start_line: int
    end_line: int


def chunk_text(
    content: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
) -> list[TextChunk]:
    """
    Split text into overlapping chunks respecting line boundaries.

    Args:
        content: Raw text or code string.
        chunk_size: Target maximum characters per chunk.
        chunk_overlap: Target character overlap between consecutive chunks.

    Returns:
        List of TextChunk instances with accurate 1-indexed start and end line ranges.
    """
    if not content or not content.strip():
        return []

    lines = content.splitlines(keepends=True)
    if not lines:
        return []

    chunks: list[TextChunk] = []
    chunk_idx = 0

    current_lines: list[str] = []
    current_chars = 0
    start_line = 1  # 1-indexed

    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        line_len = len(line)

        # If single line exceeds chunk size by itself, flush current buffer and emit long line as isolated chunk
        if line_len >= chunk_size and not current_lines:
            chunk_content = line.rstrip("\r\n")
            chunks.append(
                TextChunk(
                    chunk_index=chunk_idx,
                    content=chunk_content,
                    start_line=i + 1,
                    end_line=i + 1,
                )
            )
            chunk_idx += 1
            i += 1
            start_line = i + 1
            continue

        if current_chars + line_len > chunk_size and current_lines:
            # Emit current chunk
            chunk_content = "".join(current_lines).rstrip("\r\n")
            end_line = start_line + len(current_lines) - 1

            chunks.append(
                TextChunk(
                    chunk_index=chunk_idx,
                    content=chunk_content,
                    start_line=start_line,
                    end_line=end_line,
                )
            )
            chunk_idx += 1

            # Calculate overlap lines to retain for the next chunk
            overlap_lines: list[str] = []
            overlap_chars = 0
            for prev_line in reversed(current_lines):
                if overlap_chars + len(prev_line) > chunk_overlap:
                    break
                overlap_lines.insert(0, prev_line)
                overlap_chars += len(prev_line)

            # Next chunk starts with overlap lines
            current_lines = list(overlap_lines)
            current_chars = overlap_chars
            start_line = end_line - len(overlap_lines) + 1

        current_lines.append(line)
        current_chars += line_len
        i += 1

    # Emit final remaining chunk
    if current_lines:
        chunk_content = "".join(current_lines).rstrip("\r\n")
        end_line = start_line + len(current_lines) - 1
        chunks.append(
            TextChunk(
                chunk_index=chunk_idx,
                content=chunk_content,
                start_line=start_line,
                end_line=end_line,
            )
        )

    return chunks
