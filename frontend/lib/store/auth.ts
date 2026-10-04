/**
 * Cortex Engineering — Authentication Store (Zustand)
 */

import { create } from "zustand";
import { authApi, clearToken, setToken } from "../api/client";
import type { User } from "../api/types";

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  initialize: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: null,
  isLoading: true,
  error: null,

  initialize: async () => {
    if (typeof window === "undefined") {
      set({ isLoading: false });
      return;
    }

    const savedToken = localStorage.getItem("cortex_token");
    if (!savedToken) {
      set({ user: null, token: null, isLoading: false });
      return;
    }

    set({ token: savedToken, isLoading: true });
    try {
      const user = await authApi.getMe();
      set({ user, isLoading: false, error: null });
    } catch {
      clearToken();
      set({ user: null, token: null, isLoading: false });
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const res = await authApi.login({ email, password });
      setToken(res.access_token);
      set({
        user: res.user,
        token: res.access_token,
        isLoading: false,
        error: null,
      });
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to sign in";
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  register: async (email: string, username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.register({ email, username, password });
      // Automatically log in after registration
      await get().login(email, password);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Registration failed";
      set({ error: message, isLoading: false });
      throw err;
    }
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore network errors during logout
    } finally {
      clearToken();
      set({ user: null, token: null, error: null });
    }
  },

  clearError: () => set({ error: null }),
}));
