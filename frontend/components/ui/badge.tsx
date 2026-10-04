"use client";

import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "error" | "info" | "outline";
}

export function Badge({
  children,
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const variants = {
    default: "bg-bg-tertiary text-text-secondary border-border-default",
    success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    error: "bg-rose-500/10 text-rose-400 border-rose-500/20",
    info: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    outline: "bg-transparent text-text-secondary border-border-default",
  };

  return (
    <span
      className={twMerge(
        clsx(
          "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-wide",
          variants[variant],
          className
        )
      )}
      {...props}
    >
      {children}
    </span>
  );
}
