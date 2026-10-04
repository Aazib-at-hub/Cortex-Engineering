"""
Cortex Engineering — Application Exceptions.

Defines a hierarchy of domain exceptions that are caught by the API layer
and translated into consistent HTTP error responses. Business logic raises
these exceptions; the API layer handles them.
"""

from __future__ import annotations

from typing import Any, Optional


class CortexError(Exception):
    """Base exception for all Cortex application errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Any] = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


# ── Authentication ───────────────────────────────────────────────────────────


class AuthenticationError(CortexError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid credentials") -> None:
        super().__init__(message=message, code="AUTHENTICATION_FAILED", status_code=401)


class InvalidTokenError(CortexError):
    """Raised when a JWT token is invalid or expired."""

    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(message=message, code="INVALID_TOKEN", status_code=401)


class UserAlreadyExistsError(CortexError):
    """Raised when attempting to register with existing email or username."""

    def __init__(self, field: str = "email") -> None:
        super().__init__(
            message=f"A user with this {field} already exists",
            code="USER_ALREADY_EXISTS",
            status_code=409,
        )


# ── Authorization ────────────────────────────────────────────────────────────


class ForbiddenError(CortexError):
    """Raised when a user lacks permission for the requested operation."""

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(message=message, code="FORBIDDEN", status_code=403)


# ── Repository ───────────────────────────────────────────────────────────────


class RepositoryNotFoundError(CortexError):
    """Raised when a repository is not found."""

    def __init__(self, repository_id: str | None = None) -> None:
        msg = "Repository not found"
        if repository_id:
            msg = f"Repository '{repository_id}' not found"
        super().__init__(message=msg, code="REPOSITORY_NOT_FOUND", status_code=404)


class InvalidRepositoryURLError(CortexError):
    """Raised when a GitHub repository URL is invalid."""

    def __init__(self, url: str = "") -> None:
        super().__init__(
            message=f"Invalid GitHub repository URL: {url}",
            code="INVALID_REPOSITORY_URL",
            status_code=400,
        )


class RepositoryAlreadyExistsError(CortexError):
    """Raised when attempting to import a repository that already exists for this user."""

    def __init__(self, url: str = "") -> None:
        super().__init__(
            message=f"Repository already imported: {url}",
            code="REPOSITORY_ALREADY_EXISTS",
            status_code=409,
        )


class RepositoryProcessingError(CortexError):
    """Raised when repository ingestion/processing fails."""

    def __init__(self, message: str = "Repository processing failed") -> None:
        super().__init__(message=message, code="PROCESSING_FAILED", status_code=500)


class RepositoryNotReadyError(CortexError):
    """Raised when attempting to query a repository that hasn't finished processing."""

    def __init__(self) -> None:
        super().__init__(
            message="Repository is not ready for querying. Please wait for processing to complete.",
            code="REPOSITORY_NOT_READY",
            status_code=422,
        )


# ── Conversation ─────────────────────────────────────────────────────────────


class ConversationNotFoundError(CortexError):
    """Raised when a conversation is not found."""

    def __init__(self) -> None:
        super().__init__(
            message="Conversation not found",
            code="CONVERSATION_NOT_FOUND",
            status_code=404,
        )


# ── RAG / LLM ───────────────────────────────────────────────────────────────


class LLMServiceError(CortexError):
    """Raised when the LLM service is unavailable or returns an error."""

    def __init__(self, message: str = "LLM service is currently unavailable") -> None:
        super().__init__(message=message, code="LLM_UNAVAILABLE", status_code=503)


class EmbeddingServiceError(CortexError):
    """Raised when the embedding service fails."""

    def __init__(self, message: str = "Embedding generation failed") -> None:
        super().__init__(message=message, code="EMBEDDING_FAILED", status_code=500)


class InsufficientContextError(CortexError):
    """Raised when retrieval finds no relevant context for the query."""

    def __init__(self) -> None:
        super().__init__(
            message="No relevant repository context found for this question",
            code="INSUFFICIENT_CONTEXT",
            status_code=200,  # Not an error per se, still a valid response
        )


# ── Rate Limiting ────────────────────────────────────────────────────────────


class RateLimitExceededError(CortexError):
    """Raised when a client exceeds the rate limit."""

    def __init__(self) -> None:
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
        )


# ── Generic Common Exceptions ────────────────────────────────────────────────


class NotFoundError(CortexError):
    """Raised when any requested resource is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message=message, code="NOT_FOUND", status_code=404)


class ValidationError(CortexError):
    """Raised when client input or parameter validation fails."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", status_code=400)


class ConflictError(CortexError):
    """Raised when an operation conflicts with existing resource state."""

    def __init__(self, message: str = "Resource conflict") -> None:
        super().__init__(message=message, code="CONFLICT", status_code=409)


class InternalServerError(CortexError):
    """Raised when an internal or external integration error occurs."""

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(message=message, code="INTERNAL_SERVER_ERROR", status_code=500)


