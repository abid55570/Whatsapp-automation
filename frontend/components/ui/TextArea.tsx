"use client";

import { type TextareaHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/utils";

interface Props extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const TextArea = forwardRef<HTMLTextAreaElement, Props>(
  ({ label, hint, error, className, id, rows = 3, ...props }, ref) => {
    const textareaId =
      id ?? (label ? `textarea-${label.replace(/\s+/g, "-").toLowerCase()}` : undefined);

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-medium text-slate-700 mb-1.5"
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          rows={rows}
          className={cn(
            "w-full px-4 py-3 rounded-xl border bg-white text-slate-900 placeholder:text-slate-400 resize-none",
            "focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent",
            "transition disabled:bg-slate-50 disabled:cursor-not-allowed",
            error ? "border-red-400" : "border-slate-200",
            className,
          )}
          {...props}
        />
        {(hint || error) && (
          <p
            className={cn(
              "text-xs mt-1.5",
              error ? "text-red-500" : "text-slate-500",
            )}
          >
            {error ?? hint}
          </p>
        )}
      </div>
    );
  },
);
TextArea.displayName = "TextArea";
