"use client";

import React, { useState } from "react";
import { Modal } from "../ui/modal";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { repoApi } from "../../lib/api/client";
import { GitFork, GitBranch } from "lucide-react";
import type { Repository } from "../../lib/api/types";

interface ImportRepoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImportSuccess: (repo: Repository) => void;
}

export function ImportRepoModal({
  isOpen,
  onClose,
  onImportSuccess,
}: ImportRepoModalProps) {
  const [githubUrl, setGithubUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");

    // Quick client-side check
    if (!githubUrl.includes("github.com/")) {
      setErrorMsg("Please provide a valid GitHub repository URL.");
      return;
    }

    setLoading(true);
    try {
      const newRepo = await repoApi.importRepo({
        github_url: githubUrl.trim(),
        branch: branch.trim() || "main",
      });
      onImportSuccess(newRepo);
      onClose();
      setGithubUrl("");
      setBranch("main");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg("Failed to import repository. Please verify URL and access.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Import GitHub Repository"
      description="Provide a GitHub repository URL to index. Cortex will clone, chunk, and embed code in the background."
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4 pt-2">
        {errorMsg && (
          <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-2.5 text-xs text-rose-300">
            {errorMsg}
          </div>
        )}

        <div className="space-y-1">
          <Input
            label="Repository URL"
            type="url"
            required
            placeholder="https://github.com/pallets/flask"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
          />
          <p className="text-[11px] text-text-tertiary">
            Supported format: https://github.com/owner/repo
          </p>
        </div>

        <Input
          label="Branch (optional)"
          type="text"
          placeholder="main"
          value={branch}
          onChange={(e) => setBranch(e.target.value)}
        />

        <div className="rounded-lg border border-border-default bg-bg-primary/50 p-3 text-xs text-text-secondary flex items-start gap-2.5">
          <GitFork className="h-4 w-4 text-indigo-400 mt-0.5 shrink-0" />
          <span>
            Cortex will clone the default branch, discover all code files, apply smart filtering
            rules (ignoring node_modules, .git, binaries), and index embeddings into pgvector.
          </span>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" isLoading={loading}>
            Start Ingestion
          </Button>
        </div>
      </form>
    </Modal>
  );
}
