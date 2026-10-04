"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { AuthModal } from "../components/auth/AuthModal";
import { ImportRepoModal } from "../components/repository/ImportRepoModal";
import { RepoCard } from "../components/repository/RepoCard";
import { ChatInterface } from "../components/chat/ChatInterface";
import { Button } from "../components/ui/button";
import { useAuthStore } from "../lib/store/auth";
import { repoApi } from "../lib/api/client";
import type { Repository } from "../lib/api/types";
import {
  Plus,
  GitBranch,
  Search,
  Sparkles,
  Terminal,
  ShieldCheck,
  RefreshCw,
  FolderGit2,
} from "lucide-react";

export default function Home() {
  const { user } = useAuthStore();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [importModalOpen, setImportModalOpen] = useState(false);

  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(false);
  const [selectedRepo, setSelectedRepo] = useState<Repository | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchRepositories = async () => {
    if (!user) {
      setRepositories([]);
      return;
    }
    setLoadingRepos(true);
    try {
      const data = await repoApi.listRepos();
      setRepositories(data);
    } catch {
      // Repos list error handling (e.g. unauth)
    } finally {
      setLoadingRepos(false);
    }
  };

  useEffect(() => {
    fetchRepositories();
  }, [user]);

  const handleSelectRepo = (repo: Repository) => {
    setSelectedRepo(repo);
  };

  const handleDeleteRepo = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this repository and its vector index?")) {
      return;
    }
    try {
      await repoApi.deleteRepo(id);
      setRepositories((prev) => prev.filter((r) => r.id !== id));
      if (selectedRepo?.id === id) {
        setSelectedRepo(null);
      }
    } catch {
      alert("Failed to delete repository.");
    }
  };

  const handleImportSuccess = (newRepo: Repository) => {
    setRepositories((prev) => [newRepo, ...prev]);
    // Optionally open the newly imported repo
    setSelectedRepo(newRepo);
  };

  const filteredRepos = repositories.filter(
    (r) =>
      r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.github_url.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen flex flex-col bg-bg-primary text-text-primary">
      <Navbar
        onOpenAuth={() => setAuthModalOpen(true)}
        onOpenImport={() => {
          if (!user) {
            setAuthModalOpen(true);
          } else {
            setImportModalOpen(true);
          }
        }}
      />

      <main className="flex-1 flex flex-col">
        {selectedRepo ? (
          <ChatInterface
            repository={selectedRepo}
            onBack={() => setSelectedRepo(null)}
          />
        ) : (
          <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
            {/* Hero / Welcome Banner if unauthenticated or no repos */}
            {!user ? (
              <div className="relative overflow-hidden rounded-3xl border border-border-default bg-gradient-to-b from-bg-secondary via-bg-secondary/60 to-bg-primary p-8 sm:p-12 text-center shadow-2xl">
                <div className="mx-auto max-w-2xl space-y-4">
                  <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-medium text-indigo-400">
                    <Sparkles className="h-3.5 w-3.5" />
                    <span>PostgreSQL pgvector + Codebase RAG</span>
                  </div>

                  <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-text-primary">
                    Codebase Intelligence with{" "}
                    <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-indigo-300 bg-clip-text text-transparent">
                      Precise Citations
                    </span>
                  </h1>

                  <p className="text-sm sm:text-base text-text-secondary leading-relaxed">
                    Ingest public or private GitHub repositories into vector embeddings. Query
                    architecture, implementations, and call graphs with source-grounded answers.
                  </p>

                  <div className="pt-4 flex flex-wrap items-center justify-center gap-3">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={() => setAuthModalOpen(true)}
                      className="px-6"
                    >
                      Get Started / Sign In
                    </Button>
                    <a
                      href="https://github.com"
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-2 rounded-lg border border-border-default bg-bg-tertiary px-4 py-2.5 text-sm font-medium text-text-secondary hover:text-text-primary hover:border-indigo-500/40 transition-colors"
                    >
                      <Terminal className="h-4 w-4 text-indigo-400" />
                      View Documentation
                    </a>
                  </div>
                </div>

                {/* Features grid */}
                <div className="mt-12 grid grid-cols-1 sm:grid-cols-3 gap-4 text-left pt-6 border-t border-border-default/60">
                  <div className="rounded-xl border border-border-default/60 bg-bg-tertiary/20 p-4">
                    <div className="flex items-center gap-2 font-semibold text-sm text-text-primary">
                      <FolderGit2 className="h-4 w-4 text-indigo-400" />
                      Automated Ingestion
                    </div>
                    <p className="mt-1 text-xs text-text-secondary">
                      Deep directory discovery, language detection, binary exclusion, and semantic code chunking.
                    </p>
                  </div>
                  <div className="rounded-xl border border-border-default/60 bg-bg-tertiary/20 p-4">
                    <div className="flex items-center gap-2 font-semibold text-sm text-text-primary">
                      <ShieldCheck className="h-4 w-4 text-indigo-400" />
                      Prompt Defense
                    </div>
                    <p className="mt-1 text-xs text-text-secondary">
                      System prompt boundary tags isolate untrusted code and prevent prompt injection attacks.
                    </p>
                  </div>
                  <div className="rounded-xl border border-border-default/60 bg-bg-tertiary/20 p-4">
                    <div className="flex items-center gap-2 font-semibold text-sm text-text-primary">
                      <Sparkles className="h-4 w-4 text-indigo-400" />
                      Exact Line Citations
                    </div>
                    <p className="mt-1 text-xs text-text-secondary">
                      Every answer references the exact source file path, line numbers, and similarity score.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              /* Authenticated User Dashboard */
              <div className="space-y-6">
                {/* Header toolbar */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-border-default pb-5">
                  <div>
                    <h2 className="text-xl font-bold tracking-tight text-text-primary">
                      Repositories
                    </h2>
                    <p className="text-xs text-text-secondary mt-0.5">
                      Manage indexed codebases and query them with semantic vector RAG
                    </p>
                  </div>

                  <div className="flex items-center gap-3 w-full sm:w-auto">
                    <div className="relative flex-1 sm:w-64">
                      <Search className="absolute left-3 top-2.5 h-4 w-4 text-text-tertiary" />
                      <input
                        type="text"
                        placeholder="Search repositories..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full rounded-lg border border-border-default bg-bg-secondary pl-9 pr-3 py-1.5 text-xs text-text-primary placeholder:text-text-tertiary focus:border-indigo-500 focus:outline-none"
                      />
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => setImportModalOpen(true)}
                      className="gap-1.5 shrink-0"
                    >
                      <Plus className="h-4 w-4" /> Import Repo
                    </Button>
                  </div>
                </div>

                {/* Repositories grid */}
                {loadingRepos ? (
                  <div className="flex flex-col items-center justify-center py-20 text-center">
                    <RefreshCw className="h-6 w-6 animate-spin text-indigo-400" />
                    <p className="mt-2 text-xs text-text-secondary">Loading repositories...</p>
                  </div>
                ) : filteredRepos.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {filteredRepos.map((repo) => (
                      <RepoCard
                        key={repo.id}
                        repository={repo}
                        onSelect={handleSelectRepo}
                        onDelete={handleDeleteRepo}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border-default bg-bg-secondary/40 py-16 text-center">
                    <FolderGit2 className="h-10 w-10 text-text-tertiary" />
                    <h3 className="mt-3 text-sm font-semibold text-text-primary">
                      No repositories found
                    </h3>
                    <p className="mt-1 text-xs text-text-secondary max-w-sm">
                      {searchQuery
                        ? "No indexed repositories matched your search query."
                        : "You haven't imported any GitHub repositories yet. Import one to start querying."}
                    </p>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => setImportModalOpen(true)}
                      className="mt-4 gap-1.5"
                    >
                      <Plus className="h-4 w-4" /> Import First Repository
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Modals */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
      />

      <ImportRepoModal
        isOpen={importModalOpen}
        onClose={() => setImportModalOpen(false)}
        onImportSuccess={handleImportSuccess}
      />
    </div>
  );
}
