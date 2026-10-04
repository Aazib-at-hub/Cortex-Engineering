/**
 * Cortex Engineering — Shared TypeScript Types
 *
 * All API response types and domain models.
 * These mirror the backend Pydantic schemas.
 */

// ── User ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Repository ────────────────────────────────────────────────────────────────

export type RepositoryStatus =
  | "PENDING"
  | "CLONING"
  | "DISCOVERING"
  | "FILTERING"
  | "EXTRACTING"
  | "CHUNKING"
  | "EMBEDDING"
  | "INDEXING"
  | "READY"
  | "FAILED";

export interface Repository {
  id: string;
  name: string;
  github_url: string;
  branch: string;
  status: RepositoryStatus;
  file_count: number;
  chunk_count: number;
  languages: Record<string, number> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface RepositoryFile {
  id: string;
  path: string;
  filename: string;
  language: string;
  size_bytes: number;
}

export interface CodeChunk {
  id: string;
  chunk_index: number;
  start_line: number;
  end_line: number;
  language: string;
  content: string;
}

export interface FileDetail extends RepositoryFile {
  content: string | null;
  chunks: CodeChunk[];
}

// ── Chat ──────────────────────────────────────────────────────────────────────

export interface Source {
  file_path: string;
  start_line: number;
  end_line: number;
  similarity_score: number | null;
  chunk_id: string | null;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources: Source[];
  created_at: string;
}

export interface ChatResponse {
  conversation_id: string;
  message: Message;
}

export interface Conversation {
  id: string;
  repository_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  repository_id: string;
  title: string | null;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

// ── Health ─────────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  database: string;
  embedding_provider: string;
  llm_provider: string;
}

// ── API Error ──────────────────────────────────────────────────────────────────

export interface APIError {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
}
