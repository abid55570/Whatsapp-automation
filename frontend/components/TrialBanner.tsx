"use client";

import { AlertCircle, Sparkles } from "lucide-react";
import Link from "next/link";

import { cn } from "@/lib/utils";
import type { Subscription } from "@/types/api";

interface Props {
  subscription: Subscription | null;
}

export function TrialBanner({ subscription }: Props) {
  if (!subscription) return null;

  // ---------- FROZEN: trial expired ----------
  if (subscription.status === "frozen") {
    return (
      <div className="rounded-2xl p-4 mb-4 flex items-center justify-between gap-3 bg-gradient-to-r from-red-100 to-orange-100 border border-red-300">
        <div className="flex items-center gap-3 min-w-0">
          <AlertCircle className="h-5 w-5 flex-shrink-0 text-red-600" />
          <div className="min-w-0">
            <p className="font-semibold text-sm text-red-900">
              Trial ended · Auto-replies stopped
            </p>
            <p className="text-xs text-red-700">
              Upgrade to keep your bot running
            </p>
          </div>
        </div>
        <Link
          href="/dashboard/settings/billing"
          className="text-sm font-semibold whitespace-nowrap px-3 py-1.5 rounded-lg transition active:scale-95 bg-red-500 text-white hover:bg-red-600"
        >
          Upgrade
        </Link>
      </div>
    );
  }

  // ---------- TRIALING: show countdown ----------
  if (subscription.plan !== "trial") return null;

  const days = subscription.days_remaining_in_trial ?? 0;
  const urgent = days <= 3;

  return (
    <div
      className={cn(
        "rounded-2xl p-4 mb-4 flex items-center justify-between gap-3",
        urgent
          ? "bg-gradient-to-r from-amber-100 to-orange-100 border border-amber-200"
          : "bg-gradient-to-r from-brand-50 to-emerald-50 border border-brand-200",
      )}
    >
      <div className="flex items-center gap-3 min-w-0">
        <Sparkles
          className={cn(
            "h-5 w-5 flex-shrink-0",
            urgent ? "text-amber-600" : "text-brand-600",
          )}
        />
        <div className="min-w-0">
          <p
            className={cn(
              "font-semibold text-sm",
              urgent ? "text-amber-900" : "text-slate-900",
            )}
          >
            {days > 0 ? `${days} days` : "Trial ending today"}
            {days > 0 ? " left in trial" : ""}
          </p>
          <p
            className={cn(
              "text-xs",
              urgent ? "text-amber-700" : "text-slate-600",
            )}
          >
            {subscription.conversations_used}/
            {subscription.conversations_included} conversations used
          </p>
        </div>
      </div>
      <Link
        href="/dashboard/settings/billing"
        className={cn(
          "text-sm font-semibold whitespace-nowrap px-3 py-1.5 rounded-lg transition active:scale-95",
          urgent
            ? "bg-amber-500 text-white hover:bg-amber-600"
            : "bg-brand-500 text-white hover:bg-brand-600",
        )}
      >
        Upgrade
      </Link>
    </div>
  );
}
