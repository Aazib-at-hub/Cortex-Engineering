"use client";

import React, { useState } from "react";
import { FileCode, ChevronDown, ChevronUp, Copy, Check } from "lucide-react";
import type { Source } from "../../lib/api/types";

interface SourceCardProps {
  source: Source;
  onViewSource?: (filePath: string, startLine: number, endLine: number) => void;
}

export function SourceCard({ source, onViewSource }: SourceCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = (e: React.MouseEvent) => {
    e.stopPropagation();
    const citation = `${source.file_path}:${source.start_line}-${source.end_line}`;
    navigator.clipboard.writeText(citation);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const scorePct = source.similarity_score
    ? Math.round(source.similarity_score * 100)
    : null;

  return (
    <div
      onClick={() =>
        onViewSource?.(source.file_path, source.start_line, source.end_line)
      }
      className="group flex items-center justify-between gap-3 rounded-lg border border-border-default/80 bg-bg-tertiary/40 px-3 py-2 text-xs hover:border-indigo-500/40 hover:bg-bg-tertiary transition-all cursor-pointer"
    >
      <div className="flex items-center gap-2 min-w-0">
        <FileCode className="h-4 w-4 text-indigo-400 shrink-0" />
        <span className="font-mono text-text-primary truncate" title={source.file_path}>
          {source.file_path}
        </span>
        <span className="font-mono text-text-tertiary text-[11px] shrink-0">
          L{source.start_line}-{source.end_line}
        </span>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {scorePct !== null && (
          <span className="rounded bg-indigo-500/10 px-1.5 py-0.5 text-[10px] font-medium text-indigo-300 border border-indigo-500/20">
            {scorePct}% match
          </span>
        )}
        <button
          onClick={handleCopy}
          className="rounded p-1 text-text-tertiary hover:text-text-primary hover:bg-bg-elevated transition-colors"
          title="Copy citation"
        >
          {copied ? (
            <Check className="h-3 w-3 text-emerald-400" />
          ) : (
            <Copy className="h-3 w-3" />
          )}
        </button>
      </div>
    </div>
  );
}
