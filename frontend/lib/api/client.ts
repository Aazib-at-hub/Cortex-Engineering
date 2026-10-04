/**
 * Cortex Engineering — Base API Client
 *
 * Centralized HTTP client wrapping fetch. All API communication
 * goes through this module. Handles auth headers, error parsing,
 * and base URL configuration.
 */

import type { APIError } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Custom error class that carries the parsed API error response. */
export class ApiError extends Error {
  public code: string;
  public status: number;
  public details: unknown;

  constructor(status: number, error: APIError["error"]) {
    super(error.message);
    this.name = "ApiError";
    this.status = status;
    this.code = error.code;
    this.details = error.details;
  }
}

/** Get the stored auth token from localStorage. */
function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("cortex_token");
}

/** Set the auth token in localStorage. */
export function setToken(token: string): void {
  localStorage.setItem("cortex_token", token);
}

/** Remove the auth token from localStorage. */
export function clearToken(): void {
  localStorage.removeItem("cortex_token");
}

/**
 * Core fetch wrapper with auth, error handling, and JSON parsing.
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = getToken();

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle no-content responses
  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json();

  if (!response.ok) {
    const apiError = data as APIError;
    throw new ApiError(response.status, apiError.error || {
      code: "UNKNOWN",
      message: "An unexpected error occurred",
      details: null,
    });
  }

  return data as T;
}

/** HTTP GET */
export function get<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: "GET" });
}

/** HTTP POST */
export function post<T>(endpoint: string, body?: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: "POST",
    body: body ? JSON.stringify(body) : undefined,
  });
}

/** HTTP PUT */
export function put<T>(endpoint: string, body?: unknown): Promise<T> {
  return request<T>(endpoint, {
    method: "PUT",
    body: body ? JSON.stringify(body) : undefined,
  });
}

/** HTTP DELETE */
export function del<T>(endpoint: string): Promise<T> {
  return request<T>(endpoint, { method: "DELETE" });
}

// ── Typed API Helpers ────────────────────────────────────────────────────────

import type {
  ChatResponse,
  Conversation,
  ConversationDetail,
  FileDetail,
  HealthResponse,
  Repository,
  RepositoryFile,
  TokenResponse,
  User,
} from "./types";

export const authApi = {
  register: (body: { email: string; username: string; password: string }) =>
    post<User>("/api/v1/auth/register", body),
  login: (body: { email: string; password: string }) =>
    post<TokenResponse>("/api/v1/auth/login", body),
  logout: () => post<{ message: string }>("/api/v1/auth/logout"),
  getMe: () => get<User>("/api/v1/auth/me"),
};

export const repoApi = {
  importRepo: (body: { github_url: string; branch?: string }) =>
    post<Repository>("/api/v1/repositories/import", body),
  listRepos: () => get<Repository[]>("/api/v1/repositories"),
  getRepo: (id: string) => get<Repository>(`/api/v1/repositories/${id}`),
  getStatus: (id: string) =>
    get<{
      id: string;
      status: Repository["status"];
      file_count: number;
      chunk_count: number;
      error_message: string | null;
      updated_at: string;
    }>(`/api/v1/repositories/${id}/status`),
  listFiles: (id: string) => get<RepositoryFile[]>(`/api/v1/repositories/${id}/files`),
  getFileDetail: (repoId: string, fileId: string) =>
    get<FileDetail>(`/api/v1/repositories/${repoId}/files/${fileId}`),
  reindex: (id: string) => post<Repository>(`/api/v1/repositories/${id}/reindex`),
  deleteRepo: (id: string) => del<void>(`/api/v1/repositories/${id}`),
};

export const chatApi = {
  askQuestion: (repoId: string, body: { question: string; conversation_id?: string | null }) =>
    post<ChatResponse>(`/api/v1/repositories/${repoId}/chat`, body),
  listConversations: (repoId: string) =>
    get<Conversation[]>(`/api/v1/repositories/${repoId}/conversations`),
  getConversation: (convId: string) =>
    get<ConversationDetail>(`/api/v1/conversations/${convId}`),
  deleteConversation: (convId: string) =>
    del<void>(`/api/v1/conversations/${convId}`),
};

export const healthApi = {
  checkHealth: () => get<HealthResponse>("/api/v1/health"),
};

