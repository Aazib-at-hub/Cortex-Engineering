"use client";

import React, { useState } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Modal } from "../ui/modal";
import { FileCode, Copy, Check } from "lucide-react";

interface SourceViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  filePath: string;
  startLine: number;
  endLine: number;
  codeContent?: string;
  language?: string;
}

export function SourceViewerModal({
  isOpen,
  onClose,
  filePath,
  startLine,
  endLine,
  codeContent = "",
  language = "python",
}: SourceViewerModalProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(codeContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={filePath || "Source Code"}
      description={`Citing lines ${startLine} to ${endLine}`}
      maxWidth="2xl"
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between border-b border-border-default pb-2">
          <div className="flex items-center gap-2 text-xs font-mono text-text-secondary">
            <FileCode className="h-4 w-4 text-indigo-400" />
            <span>{filePath}</span>
          </div>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 rounded-md border border-border-default bg-bg-tertiary px-2.5 py-1 text-xs text-text-secondary hover:text-text-primary transition-colors"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy Code</span>
              </>
            )}
          </button>
        </div>

        <div className="max-h-[500px] overflow-auto rounded-lg border border-border-default bg-[#1e1e1e] font-mono text-xs">
          <SyntaxHighlighter
            language={language || "typescript"}
            style={vscDarkPlus}
            showLineNumbers={true}
            startingLineNumber={startLine || 1}
            wrapLines={true}
            customStyle={{
              margin: 0,
              padding: "1rem",
              background: "transparent",
              fontSize: "0.85rem",
            }}
          >
            {codeContent || "// No file snippet available for direct preview."}
          </SyntaxHighlighter>
        </div>
      </div>
    </Modal>
  );
}
