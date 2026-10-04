"use client";

import { useEffect, useState } from "react";
import { Cpu, GitFork, LogIn, LogOut, RefreshCw, Terminal, User as UserIcon } from "lucide-react";
import { useAuthStore } from "../lib/store/auth";
import { healthApi } from "../lib/api/client";
import type { HealthResponse } from "../lib/api/types";

interface NavbarProps {
  onOpenAuth: () => void;
  onOpenImport: () => void;
}

export function Navbar({ onOpenAuth, onOpenImport }: NavbarProps) {
  const { user, logout, initialize } = useAuthStore();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState(false);

  useEffect(() => {
    initialize();
    checkHealth();
  }, [initialize]);

  const checkHealth = async () => {
    setIsHealthLoading(true);
    try {
      const data = await healthApi.checkHealth();
      setHealth(data);
    } catch {
      setHealth(null);
    } finally {
      setIsHealthLoading(false);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border-default bg-bg-secondary/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 via-indigo-600 to-purple-600 shadow-md shadow-indigo-500/20">
            <Cpu className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold tracking-tight text-text-primary">
                Cortex
              </span>
              <span className="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-indigo-400 border border-indigo-500/20">
                Engineering
              </span>
            </div>
            <p className="text-xs text-text-tertiary">Repository Intelligence Platform</p>
          </div>
        </div>

        {/* Status & Actions */}
        <div className="flex items-center gap-3">
          {/* Health Indicator */}
          <div
            onClick={checkHealth}
            title={health ? `Backend: ${health.status} (${health.database})` : "Backend offline"}
            className="flex cursor-pointer items-center gap-2 rounded-full border border-border-default bg-bg-tertiary px-3 py-1.5 text-xs text-text-secondary transition hover:border-text-tertiary"
          >
            <span
              className={`h-2 w-2 rounded-full ${
                health?.status === "healthy"
                  ? "bg-emerald-400"
                  : health?.status === "degraded"
                  ? "bg-amber-400 animate-pulse"
                  : "bg-red-400"
              }`}
            />
            <span className="hidden sm:inline font-mono">
              {health?.status === "healthy"
                ? "System Online"
                : health?.status === "degraded"
                ? `DB ${health.database}`
                : "Offline"}
            </span>
            <RefreshCw
              className={`h-3 w-3 text-text-tertiary ${isHealthLoading ? "animate-spin" : ""}`}
            />
          </div>

          {/* Import Repo Button */}
          {user && (
            <button
              onClick={onOpenImport}
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition active:scale-95"
            >
              <GitFork className="h-3.5 w-3.5" />
              <span>Import Repo</span>
            </button>
          )}

          {/* Auth Button */}
          {user ? (
            <div className="flex items-center gap-3 pl-2 border-l border-border-default">
              <div className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-bg-surface text-text-primary border border-border-default text-xs font-semibold">
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-xs font-medium text-text-primary leading-none">{user.username}</p>
                  <p className="text-[10px] text-text-tertiary">{user.email}</p>
                </div>
              </div>
              <button
                onClick={() => logout()}
                title="Sign out"
                className="rounded-lg p-1.5 text-text-tertiary hover:bg-bg-tertiary hover:text-text-primary transition"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-2 rounded-lg border border-border-default bg-bg-tertiary px-3.5 py-1.5 text-xs font-medium text-text-primary hover:bg-bg-elevated transition"
            >
              <LogIn className="h-3.5 w-3.5 text-indigo-400" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
