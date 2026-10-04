---
milestone: Cortex Engineering MVP
version: 0.1.0
updated: 2026-10-05T02:00:00+05:30
---

# Roadmap

> **Current Phase:** Complete MVP
> **Status:** ✅ Complete

## Must-Haves (from SPEC)

- [x] Backend architecture scaffolding, async SQLAlchemy models, and Alembic migrations
- [x] Repository ingestion pipeline (clone, discover, filter, extract, chunk)
- [x] Embedding generation (OpenAI & local sentence-transformers fallback) & pgvector integration
- [x] Semantic retrieval & RAG service with source citation extraction
- [x] Complete frontend web UI (Auth, Repository Management, Chat UI, Source Viewer)
- [x] Automated unit test suite passing with empirical proof

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
**Status:** ✅ Complete
**Objective:** Next.js pages: Login/Register modal, Repository List/Import modal, Repository Chat interface with source citations.

---

### Phase 10: Source Viewer
**Status:** ✅ Complete
**Objective:** Read-only code viewer with syntax highlighting and line targeting for cited sources.

---

### Phase 11: Testing & Quality Assurance
**Status:** ✅ Complete
**Objective:** Unit tests for URL validation, file filtering, chunking, prompt templates, and authentication security (16 tests passed).

---

### Phase 12: Documentation & Build Verification
**Status:** ✅ Complete
**Objective:** Root README, Docker compose setup, Next.js production build (`npm run build`) passing.
