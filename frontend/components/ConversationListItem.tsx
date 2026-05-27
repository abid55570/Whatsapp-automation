"use client";

import { Bot } from "lucide-react";
import Link from "next/link";

import { cn } from "@/lib/utils";
import type { ConversationListItem as Conv } from "@/types/api";

interface Props {
  conv: Conv;
}

function formatRelativeTime(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  const now = Date.now();
  const diffMs = now - d.getTime();
  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "now";
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d`;
  return d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export function ConversationListItem({ conv }: Props) {
  const displayName = conv.contact.name || conv.contact.whatsapp_phone;
  const initial = displayName.charAt(0).toUpperCase() || "?";
  const hasUnread = conv.unread_count > 0;
  const lastMsg = conv.last_message;

  return (
    <Link
      href={`/dashboard/inbox/${conv.id}`}
      className="flex items-center gap-3 p-3 bg-white hover:bg-slate-50 active:bg-slate-100 transition border-b border-slate-100 last:border-b-0"
    >
      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-brand-100 to-emerald-100 text-brand-700 font-semibold flex items-center justify-center text-lg flex-shrink-0">
        {initial}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <h3
            className={cn(
              "truncate text-sm",
              hasUnread ? "font-semibold text-slate-900" : "text-slate-800",
            )}
          >
            {displayName}
          </h3>
          <span
            className={cn(
              "text-[11px] flex-shrink-0",
              hasUnread ? "text-brand-600 font-semibold" : "text-slate-500",
            )}
          >
            {formatRelativeTime(conv.last_message_at)}
          </span>
        </div>
        <div className="flex items-center justify-between gap-2 mt-0.5">
          <div className="flex items-center gap-1.5 min-w-0 flex-1">
            {lastMsg?.is_auto_reply && (
              <Bot className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
            )}
            <p
              className={cn(
                "text-sm truncate",
                hasUnread
                  ? "text-slate-700 font-medium"
                  : "text-slate-500",
              )}
            >
              {lastMsg?.direction === "outbound" && "You: "}
              {lastMsg?.body || "No messages yet"}
            </p>
          </div>
          {hasUnread && (
            <span className="bg-brand-500 text-white text-xs font-semibold px-2 py-0.5 rounded-full flex-shrink-0 min-w-[20px] text-center">
              {conv.unread_count}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
