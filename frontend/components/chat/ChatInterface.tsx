"use client";

import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User, ArrowLeft, RefreshCw, Sparkles, BookOpen } from "lucide-react";
import { Button } from "../ui/button";
import { SourceCard } from "./SourceCard";
import { SourceViewerModal } from "../source-viewer/SourceViewerModal";
import { chatApi, repoApi } from "../../lib/api/client";
import type { Repository, Message, Source } from "../../lib/api/types";

interface ChatInterfaceProps {
  repository: Repository;
  onBack: () => void;
}

export function ChatInterface({ repository, onBack }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "initial-assistant-greeting",
      role: "assistant",
      content: `Hello! I have indexed **${repository.name}**. Ask me anything about the architecture, key algorithms, auth flows, or file locations. All responses will cite exact lines in the repository.`,
      sources: [],
      created_at: new Date().toISOString(),
    },
  ]);
  const [inputQuestion, setInputQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  // Source viewer modal state
  const [viewerOpen, setViewerOpen] = useState(false);
  const [viewerData, setViewerData] = useState<{
    filePath: string;
    startLine: number;
    endLine: number;
    content?: string;
  }>({ filePath: "", startLine: 1, endLine: 1 });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    const query = inputQuestion.trim();
    if (!query || loading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: query,
      sources: [],
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputQuestion("");
    setLoading(true);

    try {
      const response = await chatApi.askQuestion(repository.id, {
        question: query,
        conversation_id: conversationId,
      });

      setConversationId(response.conversation_id);
      setMessages((prev) => [...prev, response.message]);
    } catch (err: unknown) {
      const errMsg =
        err instanceof Error
          ? err.message
          : "Failed to generate answer. Ensure the repository has finished indexing.";

      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: `⚠️ **Error querying repository:** ${errMsg}`,
          sources: [],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenSource = async (
    filePath: string,
    startLine: number,
    endLine: number
  ) => {
    setViewerData({
      filePath,
      startLine,
      endLine,
      content: `// Source Citation: ${filePath} (lines ${startLine}-${endLine})\n// Loaded from semantic vector match in pgvector`,
    });
    setViewerOpen(true);
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col bg-bg-primary">
      {/* Top Header */}
      <div className="flex h-14 items-center justify-between border-b border-border-default bg-bg-secondary px-6">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onBack}
            className="text-text-secondary hover:text-text-primary gap-1 pl-1"
          >
            <ArrowLeft className="h-4 w-4" /> Back to Repositories
          </Button>
          <div className="h-4 w-px bg-border-default" />
          <div className="flex items-center gap-2">
            <span className="font-semibold text-text-primary text-sm">
              {repository.name}
            </span>
            <span className="font-mono text-xs text-text-tertiary">
              ({repository.branch})
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-text-secondary">
          <div className="flex items-center gap-1.5">
            <BookOpen className="h-3.5 w-3.5 text-indigo-400" />
            <span>{repository.file_count} files</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5 text-indigo-400" />
            <span>{repository.chunk_count} chunks indexed</span>
          </div>
        </div>
      </div>

      {/* Message List */}
      <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl space-y-6">
          {messages.map((msg) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`flex flex-col space-y-2 max-w-[85%] ${
                    isUser ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      isUser
                        ? "bg-indigo-600 text-white rounded-br-sm"
                        : "bg-bg-secondary border border-border-default text-text-primary rounded-bl-sm"
                    }`}
                  >
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>

                  {/* Sources section */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="w-full space-y-1.5 pt-1">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-text-tertiary">
                        Referenced Sources ({msg.sources.length})
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {msg.sources.map((src, i) => (
                          <SourceCard
                            key={i}
                            source={src}
                            onViewSource={handleOpenSource}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  <span className="text-[10px] text-text-tertiary px-1">
                    {new Date(msg.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>

                {isUser && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-bg-tertiary border border-border-default text-text-secondary">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600/10 border border-indigo-500/20 text-indigo-400">
                <Bot className="h-4 w-4" />
              </div>
              <div className="flex items-center gap-2 rounded-2xl border border-border-default bg-bg-secondary px-4 py-2.5 text-xs text-text-secondary">
                <RefreshCw className="h-3.5 w-3.5 animate-spin text-indigo-400" />
                <span>Searching codebase embeddings & formulating response...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <div className="border-t border-border-default bg-bg-secondary p-4">
        <form
          onSubmit={handleSend}
          className="mx-auto flex max-w-4xl items-center gap-2"
        >
          <input
            type="text"
            placeholder={`Ask a question about ${repository.name}... (e.g. How does error handling work?)`}
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            disabled={loading}
            className="flex-1 rounded-xl border border-border-default bg-bg-primary px-4 py-2.5 text-sm text-text-primary placeholder:text-text-tertiary focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 transition-colors"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={!inputQuestion.trim() || loading}
            isLoading={loading}
            className="h-10 px-4 rounded-xl"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>

      {/* Source Viewer Modal */}
      <SourceViewerModal
        isOpen={viewerOpen}
        onClose={() => setViewerOpen(false)}
        filePath={viewerData.filePath}
        startLine={viewerData.startLine}
        endLine={viewerData.endLine}
        codeContent={viewerData.content}
      />
    </div>
  );
}
