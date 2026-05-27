"use client";

import { Inbox, Loader2 } from "lucide-react";
import { useState } from "react";

import { ConversationListItem } from "@/components/ConversationListItem";
import { useConversations } from "@/lib/queries";
import { cn } from "@/lib/utils";

export default function InboxPage() {
  const [filter, setFilter] = useState<"all" | "unread">("all");
  const { data, isLoading } = useConversations(filter);

  const total = data?.total ?? 0;
  const items = data?.items ?? [];

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10">
        <div className="p-4">
          <h1 className="text-xl font-bold text-slate-900">Inbox</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {total} {total === 1 ? "conversation" : "conversations"}
          </p>
        </div>
        <div className="px-4 pb-3 flex gap-2">
          {(["all", "unread"] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "px-3 py-1.5 rounded-full text-xs font-medium transition active:scale-95",
                filter === f
                  ? "bg-brand-500 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200",
              )}
            >
              {f === "all" ? "All" : "Unread"}
            </button>
          ))}
        </div>
      </header>

      {/* List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
        </div>
      ) : items.length === 0 ? (
        <div className="text-center py-16 px-4">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-slate-100 items-center justify-center mb-4">
            <Inbox className="h-7 w-7 text-slate-400" />
          </div>
          <h2 className="font-semibold text-slate-900 mb-1">
            {filter === "unread" ? "All caught up!" : "No conversations yet"}
          </h2>
          <p className="text-sm text-slate-500">
            {filter === "unread"
              ? "No unread messages right now."
              : "Customer messages will show up here."}
          </p>
        </div>
      ) : (
        <div className="bg-white">
          {items.map((conv) => (
            <ConversationListItem key={conv.id} conv={conv} />
          ))}
        </div>
      )}
    </div>
  );
}
