---
milestone: Cortex Engineering MVP
version: 0.1.0
updated: 2026-10-05T01:46:00+05:30
---

# Roadmap

> **Current Phase:** Phase 9 - Chat UI & Dashboard
> **Status:** 🔄 In Progress

## Must-Haves (from SPEC)

- [x] Backend architecture scaffolding, async SQLAlchemy models, and Alembic migrations
- [x] Repository ingestion pipeline (clone, discover, filter, extract, chunk)
- [x] Embedding generation (OpenAI & local sentence-transformers fallback) & pgvector integration
- [x] Semantic retrieval & RAG service with source citation extraction
- [ ] Complete frontend web UI (Auth, Repository Management, Chat UI, Source Viewer)
- [ ] Automated unit, integration, and API test coverage

---

## Phases

### Phase 1: Project Setup & Scaffolding
**Status:** ✅ Complete
**Objective:** Monorepo structure, FastAPI app, Next.js app, Docker compose, and environment configuration.

---

### Phase 2: Database & Migrations
**Status:** ✅ Complete
**Objective:** SQLAlchemy 2.0 async models, Alembic setup, initial migration schema with pgvector.

---

### Phase 3: Authentication & Security
**Status:** ✅ Complete
**Objective:** User registration, password hashing (bcrypt), JWT generation/validation, dependency injection (`get_current_user`).

---

### Phase 4: Repository Import & Status
**Status:** ✅ Complete
**Objective:** Repository URL validation, GitHub metadata handling, status transitions, and repository CRUD endpoints.

---

### Phase 5: Ingestion Pipeline
**Status:** ✅ Complete
**Objective:** Ingestion worker: clone, file discovery, filtering, text extraction, chunking.

---

### Phase 6: Embeddings & pgvector Storage
**Status:** ✅ Complete
**Objective:** Embedding service (OpenAI + local fallback), batch embedding generation, and vector insertion.

---

### Phase 7: Retrieval Engine
**Status:** ✅ Complete
**Objective:** Vector similarity search with pgvector cosine distance, repository scoping, top-K filtering.

---

### Phase 8: RAG & LLM Response Generation
**Status:** ✅ Complete
**Objective:** LLM service (OpenAI + Gemini), prompt templates with prompt injection guards, source citations parsing.

---

### Phase 9: Frontend Chat UI & Dashboard
**Status:** 🔄 In Progress
**Objective:** Next.js pages: Login/Register, Repository List/Import modal, Repository Chat interface with source citations.

---

### Phase 10: Source Viewer
**Status:** ⬜ Not Started
**Objective:** Read-only code viewer with syntax highlighting and line jumping for cited sources.

---

### Phase 11: Testing & Quality Assurance
**Status:** ⬜ Not Started
**Objective:** Unit tests (chunker, filter, prompt), API integration tests, and RAG evaluation script.

---

### Phase 12: Security Hardening & Documentation
**Status:** ⬜ Not Started
**Objective:** Path traversal audits, rate limiting checks, ADRs, and final Docker verification.

---

## Progress Summary

| Phase | Status | Objective |
|-------|--------|-----------|
| 1-8 (Backend Core) | ✅ | Backend models, ingestion, embeddings, RAG, and APIs |
| 9 (Chat UI & Dashboard) | 🔄 | Next.js frontend pages and interactive chat |
| 10 (Source Viewer) | ⬜ | Code viewer component with syntax highlight |
| 11 (Testing) | ⬜ | Pytest unit/integration test suite |
| 12 (Hardening & Docs) | ⬜ | Security hardening, Docker verification, and documentation |
