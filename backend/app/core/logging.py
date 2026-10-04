"""
Cortex Engineering — Structured Logging.

Configures structlog for JSON-formatted, structured logging with useful
context (timestamp, log level, logger name). Sensitive data is never logged.
"""

from __future__ import annotations

import logging
import sys

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: The minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Configure structlog processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure the standard library logging
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer()
            if log_level == "DEBUG"
            else structlog.processors.JSONRenderer(),
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Quiet noisy third-party loggers
    for logger_name in ("uvicorn.access", "httpx", "httpcore", "sqlalchemy.engine"):
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        A bound structlog logger.
    """
    return structlog.get_logger(name)
