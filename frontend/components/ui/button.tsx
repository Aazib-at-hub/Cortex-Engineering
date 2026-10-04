"use client";

import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { Loader2 } from "lucide-react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      className,
      variant = "primary",
      size = "md",
      isLoading = false,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium transition-all duration-150 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/50 disabled:opacity-50 disabled:cursor-not-allowed select-none cursor-pointer";

    const variants = {
      primary:
        "bg-indigo-600 text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 shadow-indigo-500/25 border border-indigo-500/30",
      secondary:
        "bg-bg-tertiary text-text-primary hover:bg-bg-elevated active:bg-bg-surface border border-border-default",
      outline:
        "bg-transparent text-text-primary hover:bg-bg-secondary active:bg-bg-tertiary border border-border-default hover:border-indigo-500/40",
      ghost:
        "bg-transparent text-text-secondary hover:text-text-primary hover:bg-bg-secondary active:bg-bg-tertiary",
      danger:
        "bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 active:bg-rose-500/30 border border-rose-500/30",
    };

    const sizes = {
      sm: "h-8 px-3 text-xs gap-1.5",
      md: "h-9 px-4 text-sm gap-2",
      lg: "h-11 px-5 text-base gap-2.5",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={twMerge(clsx(baseStyles, variants[variant], sizes[size], className))}
        {...props}
      >
        {isLoading && <Loader2 className="h-4 w-4 animate-spin text-current" />}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
