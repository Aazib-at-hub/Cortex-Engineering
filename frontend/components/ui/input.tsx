"use client";

import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

    return (
      <div className="w-full space-y-1.5 text-left">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-xs font-medium text-text-secondary"
          >
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={twMerge(
            clsx(
              "flex h-9 w-full rounded-lg border bg-bg-secondary px-3 py-1.5 text-sm text-text-primary placeholder:text-text-tertiary",
              "border-border-default focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/50",
              "transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50",
              error && "border-rose-500/60 focus:border-rose-500 focus:ring-rose-500/30",
              className
            )
          )}
          {...props}
        />
        {error ? (
          <p className="text-xs text-rose-400">{error}</p>
        ) : helperText ? (
          <p className="text-xs text-text-tertiary">{helperText}</p>
        ) : null}
      </div>
    );
  }
);

Input.displayName = "Input";
