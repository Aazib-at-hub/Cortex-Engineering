"use client";

import React, { useState } from "react";
import { Modal } from "../ui/modal";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { useAuthStore } from "../../lib/store/auth";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultMode?: "login" | "register";
}

export function AuthModal({
  isOpen,
  onClose,
  defaultMode = "login",
}: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">(defaultMode);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setLoading(true);

    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, username, password);
      }
      onClose();
      setEmail("");
      setUsername("");
      setPassword("");
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg("Authentication failed. Please check credentials.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={mode === "login" ? "Sign In to Cortex" : "Create Account"}
      description={
        mode === "login"
          ? "Access your indexed repositories and intelligence conversations"
          : "Start indexing repositories and querying codebases with RAG"
      }
      maxWidth="sm"
    >
      <form onSubmit={handleSubmit} className="space-y-4 pt-2">
        {errorMsg && (
          <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-2.5 text-xs text-rose-300">
            {errorMsg}
          </div>
        )}

        <Input
          label="Email Address"
          type="email"
          required
          placeholder="developer@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        {mode === "register" && (
          <Input
            label="Username"
            type="text"
            required
            placeholder="octocat"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        )}

        <Input
          label="Password"
          type="password"
          required
          placeholder="••••••••••••"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <Button type="submit" variant="primary" className="w-full" isLoading={loading}>
          {mode === "login" ? "Sign In" : "Create Account"}
        </Button>

        <div className="text-center pt-2 text-xs text-text-tertiary">
          {mode === "login" ? (
            <span>
              Don&apos;t have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("register");
                  setErrorMsg("");
                }}
                className="text-indigo-400 hover:text-indigo-300 font-medium underline-offset-2 hover:underline cursor-pointer"
              >
                Sign up
              </button>
            </span>
          ) : (
            <span>
              Already have an account?{" "}
              <button
                type="button"
                onClick={() => {
                  setMode("login");
                  setErrorMsg("");
                }}
                className="text-indigo-400 hover:text-indigo-300 font-medium underline-offset-2 hover:underline cursor-pointer"
              >
                Sign in
              </button>
            </span>
          )}
        </div>
      </form>
    </Modal>
  );
}
