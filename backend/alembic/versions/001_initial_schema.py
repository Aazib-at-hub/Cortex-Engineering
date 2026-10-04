"""Initial schema with pgvector and all core tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-10-02 00:00:00.000000

Mirrors app/models/* exactly. If a model changes, add a new revision
rather than editing this one.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Must match EMBEDDING_DIMENSION (all-MiniLM-L6-v2 = 384)
EMBEDDING_DIM = 384


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    # ── repositories ─────────────────────────────────────────────────────────
    op.create_table(
        "repositories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("github_url", sa.String(2048), nullable=False),
        sa.Column("branch", sa.String(255), nullable=False, server_default="main"),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("file_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("languages", postgresql.JSONB(), nullable=True),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_repositories_user_id", "repositories", ["user_id"])
    op.create_index("ix_repositories_user_status", "repositories", ["user_id", "status"])

    # ── files ────────────────────────────────────────────────────────────────
    op.create_table(
        "files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("path", sa.String(1024), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("language", sa.String(50), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content_hash", sa.String(64), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_files_repository_id", "files", ["repository_id"])

    # ── code_chunks ──────────────────────────────────────────────────────────
    op.create_table(
        "code_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("language", sa.String(50), nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_code_chunks_repository_id", "code_chunks", ["repository_id"])
    op.create_index("ix_code_chunks_file_id", "code_chunks", ["file_id"])
    # HNSW: good recall without IVFFlat's training step; works on empty tables.
    op.execute(
        "CREATE INDEX ix_code_chunks_embedding_hnsw ON code_chunks "
        "USING hnsw (embedding vector_cosine_ops);"
    )

    # ── conversations ────────────────────────────────────────────────────────
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("repository_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_conversations_user_repo", "conversations", ["user_id", "repository_id"])

    # ── messages ─────────────────────────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])

    # ── message_sources ──────────────────────────────────────────────────────
    op.create_table(
        "message_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("code_chunks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=True),
    )
    op.create_index("ix_message_sources_message_id", "message_sources", ["message_id"])


def downgrade() -> None:
    op.drop_table("message_sources")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("code_chunks")
    op.drop_table("files")
    op.drop_table("repositories")
    op.drop_table("users")
