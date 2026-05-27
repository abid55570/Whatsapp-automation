"use client";

import { type InputHTMLAttributes, forwardRef } from "react";

import { cn } from "@/lib/utils";

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  leftAdornment?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, Props>(
  ({ label, hint, error, leftAdornment, className, id, ...props }, ref) => {
    const inputId =
      id ?? (label ? `input-${label.replace(/\s+/g, "-").toLowerCase()}` : undefined);

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-slate-700 mb-1.5"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftAdornment && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
              {leftAdornment}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              "w-full px-4 py-3 rounded-xl border bg-white text-slate-900 placeholder:text-slate-400",
              "focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent",
              "transition disabled:bg-slate-50 disabled:cursor-not-allowed",
              leftAdornment && "pl-10",
              error ? "border-red-400" : "border-slate-200",
              className,
            )}
            {...props}
          />
        </div>
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
Input.displayName = "Input";
