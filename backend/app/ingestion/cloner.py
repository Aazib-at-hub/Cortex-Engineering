"""
Cortex Engineering — Git Repository Cloner.

Handles cloning public GitHub repositories into isolated directories
using Git CLI with shallow clone (--depth 1) for speed and disk economy.
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
from pathlib import Path

from app.core.exceptions import ValidationError
from app.core.logging import get_logger

logger = get_logger("cloner")

GITHUB_URL_REGEX = re.compile(
    r"^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git)?/?$"
)


def validate_github_url(url: str) -> tuple[str, str]:
    """
    Validate that the given string is a valid GitHub repository URL.

    Returns:
        tuple[owner, repo_name]
    """
    cleaned = url.strip()
    match = GITHUB_URL_REGEX.match(cleaned)
    if not match:
        raise ValidationError(
            f"Invalid GitHub repository URL '{url}'. Expected format: https://github.com/owner/repository"
        )
    owner, repo = match.group(1), match.group(2)
    return owner, repo


async def clone_repository(
    github_url: str,
    target_dir: Path,
    branch: str = "main",
    timeout_seconds: int = 120,
) -> Path:
    """
    Clone a public git repository shallowly into target_dir.

    Args:
        github_url: HTTPS GitHub URL.
        target_dir: Local destination path.
        branch: Branch name to clone.
        timeout_seconds: Timeout for git command.

    Returns:
        Path to cloned directory.
    """
    owner, repo_name = validate_github_url(github_url)

    if target_dir.exists():
        logger.info("Cleaning up existing target directory", path=str(target_dir))
        shutil.rmtree(target_dir, ignore_errors=True)

    target_dir.parent.mkdir(parents=True, exist_ok=True)

    # Format normalized clone URL
    clone_url = f"https://github.com/{owner}/{repo_name}.git"

    # Try requested branch first, fallback to default branch if requested branch fails
    cmd = [
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        branch,
        clone_url,
        str(target_dir),
    ]

    logger.info(
        "Cloning repository",
        repo=f"{owner}/{repo_name}",
        branch=branch,
        dest=str(target_dir),
    )

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_seconds
        )
    except asyncio.TimeoutError:
        proc.kill()
        shutil.rmtree(target_dir, ignore_errors=True)
        raise RuntimeError(f"Cloning {clone_url} timed out after {timeout_seconds}s")

    if proc.returncode != 0:
        # If specific branch failed, try clone without --branch to get default
        stderr_msg = stderr.decode("utf-8", errors="ignore")
        logger.warning(
            "Clone with specified branch failed, retrying with default branch",
            error=stderr_msg,
        )

        fallback_cmd = [
            "git",
            "clone",
            "--depth",
            "1",
            clone_url,
            str(target_dir),
        ]
        fallback_proc = await asyncio.create_subprocess_exec(
            *fallback_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            _, fallback_stderr = await asyncio.wait_for(
                fallback_proc.communicate(), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            fallback_proc.kill()
            shutil.rmtree(target_dir, ignore_errors=True)
            raise RuntimeError(f"Fallback clone timed out after {timeout_seconds}s")

        if fallback_proc.returncode != 0:
            err = fallback_stderr.decode("utf-8", errors="ignore")
            shutil.rmtree(target_dir, ignore_errors=True)
            raise RuntimeError(f"Git clone failed: {err.strip()}")

    logger.info("Clone completed successfully", dest=str(target_dir))
    return target_dir
