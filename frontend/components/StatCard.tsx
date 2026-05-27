"use client";

import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

interface Props {
  label: string;
  value: string | number;
  hint?: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
  highlight?: boolean;
}

export function StatCard({
  label,
  value,
  hint,
  icon: Icon,
  iconColor = "text-brand-600",
  iconBg = "bg-brand-100",
  highlight = false,
}: Props) {
  return (
    <div
      className={cn(
        "card flex-1 min-w-0",
        highlight && "ring-2 ring-brand-500/30 bg-brand-50",
      )}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <span className="text-xs text-slate-500 font-medium">{label}</span>
        <div
          className={cn(
            "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
            iconBg,
          )}
        >
          <Icon className={cn("h-4 w-4", iconColor)} strokeWidth={2.5} />
        </div>
      </div>
      <div className="text-2xl font-bold text-slate-900 font-mono">{value}</div>
      {hint && <p className="text-xs text-slate-500 mt-1">{hint}</p>}
    </div>
  );
}
