# Cortex Engineering

**Cortex Engineering** is a repository intelligence platform that ingests GitHub repositories, indexes them semantically using vector embeddings stored in PostgreSQL with `pgvector`, and answers natural-language questions about codebases using Retrieval-Augmented Generation (RAG) with exact source citations.

---

## Architecture Overview

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 Async, Alembic, Pydantic v2.
- **Frontend**: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, TanStack Query, Zustand, Lucide Icons, Prism syntax highlighter.
- **Database & Vectors**: PostgreSQL 16 + `pgvector` (`vector` extension for cosine similarity search).
- **Embeddings**: Local sentence-transformers (`all-MiniLM-L6-v2`) or OpenAI (`text-embedding-3-small`).
- **LLM**: Google Gemini (`gemini-2.0-flash`) or OpenAI (`gpt-4o-mini`).

---

## Quickstart with Docker Compose

1. **Clone & Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and supply your GOOGLE_API_KEY or OPENAI_API_KEY
   ```

2. **Start All Services**:
   ```bash
   docker compose up -d --build
   ```

3. **Run Database Migrations**:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

4. **Access the Applications**:
   - Web Dashboard: [http://localhost:3000](http://localhost:3000)
   - FastAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Status: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## Local Development Setup

### Backend

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Run test suite:
```bash
python -m pytest tests/unit -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Build verification:
```bash
npm run build
```

---

## Key Features

1. **Repository Ingestion Pipeline**: Shallow cloning, intelligent file filtering (ignores binaries, minified bundles, lock files), and line-aware text chunking.
2. **Semantic Vector Search**: pgvector cosine distance `<=>` queries scoped strictly to the target repository.
3. **Prompt Injection Defense**: Boundary tagging isolates repository source content as untrusted data to protect the LLM.
4. **Source Grounding**: Every answer is paired with exact file paths, line ranges, and similarity scores.
5. **Interactive Source Viewer**: Modal viewer with code syntax highlighting and line targeting.
