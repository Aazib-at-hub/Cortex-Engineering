# SPEC.md — Project Specification

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: SPEC is finalized based on architecture proposal.

## Vision
Cortex Engineering is a repository intelligence platform that ingests GitHub repositories, indexes them semantically using code embeddings stored in PostgreSQL with pgvector, and answers natural-language questions about codebases using Retrieval-Augmented Generation (RAG) with exact source file and line-range citations.

## Goals
1. **GitHub Repository Ingestion** — Clone, discover, filter, extract, and chunk repository source files.
2. **Semantic Vector Search** — Generate embeddings (OpenAI / local fallback) and store them in PostgreSQL via pgvector for cosine similarity search.
3. **Grounded Codebase RAG** — Context-constrained LLM answering (OpenAI / Gemini) with prompt defense against untrusted code injection, citing precise file paths and line ranges.
4. **Interactive Web Dashboard** — Next.js 16 frontend with repository import, indexing status tracker, RAG chat interface, and read-only source viewer.
5. **Decoupled Architecture & Testing** — Modular monolith with repository pattern, unit and integration test suite, and evaluation harness.

## Non-Goals (Out of Scope for MVP)
- Multi-tenant enterprise RBAC / team workspaces.
- Real-time code editing / Git write-back (PR creation).
- Autonomous agent code modification or execution.
- Complex microservice orchestration (Celery/Redis avoided for MVP in favor of async background tasks).

## Constraints
- Single-server modular monolith deployment via Docker Compose.
- Single database: PostgreSQL 16 + pgvector.
- Backend: Python 3.12 + FastAPI + SQLAlchemy 2.0 Async + Alembic.
- Frontend: Next.js (App Router) + TypeScript + Tailwind CSS v4 + TanStack Query + Zustand.

## Success Criteria
- [x] Backend architecture scaffolding and models defined.
- [x] API routers for auth, repositories, chat, and health checks configured.
- [ ] Database migrations execute cleanly with pgvector.
- [ ] Complete end-to-end repository ingestion and chunking pipeline working.
- [ ] RAG question-answering returns answers with verified citations.
- [ ] Frontend user interface complete with auth, repository management, chat, and source viewer.
- [ ] Test suite passes with unit, integration, and API tests.

---

*Last updated: 2026-10-05*
