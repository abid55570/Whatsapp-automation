"use client";

import { ArrowLeft, Loader2, Send } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { MessageBubble } from "@/components/MessageBubble";
import { apiErrorMessage } from "@/lib/api";
import {
  useConversation,
  useMarkRead,
  useMessages,
  useSendMessage,
} from "@/lib/queries";

export default function ConversationThreadPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const conversationId = params.id;

  const { data: conv } = useConversation(conversationId);
  const { data: messagesPage, isLoading } = useMessages(conversationId);
  const sendMessage = useSendMessage(conversationId);
  const markRead = useMarkRead(conversationId);

  const [draft, setDraft] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Reverse so newest is at bottom (we fetched newest-first)
  const messages = messagesPage?.items
    ? [...messagesPage.items].reverse()
    : [];

  // Mark conversation read once on mount
  useEffect(() => {
    if (conv && conv.unread_count > 0) {
      markRead.mutate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [conv?.id]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length]);

  async function handleSend() {
    const body = draft.trim();
    if (!body) return;
    try {
      await sendMessage.mutateAsync({ body });
      setDraft("");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  const displayName =
    conv?.contact.name || conv?.contact.whatsapp_phone || "Loading...";
  const initial = displayName.charAt(0).toUpperCase() || "?";

  const sessionExpired = conv?.expires_at
    ? new Date(conv.expires_at) < new Date()
    : false;

  return (
    <div className="flex flex-col h-dvh bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-3 py-3 flex items-center gap-3 sticky top-0 z-10">
        <button
          onClick={() => router.back()}
          aria-label="Back"
          className="p-2 hover:bg-slate-100 rounded-lg active:scale-95 min-h-[44px] min-w-[44px] flex items-center justify-center"
        >
          <ArrowLeft className="h-5 w-5 text-slate-700" />
        </button>
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-100 to-emerald-100 text-brand-700 font-semibold flex items-center justify-center text-base">
          {initial}
        </div>
        <div className="flex-1 min-w-0">
          <h1 className="font-semibold text-slate-900 text-sm truncate">
            {displayName}
          </h1>
          <p className="text-[11px] text-slate-500 truncate">
            {conv?.contact.whatsapp_phone}
          </p>
        </div>
      </header>

      {/* Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-3 space-y-2 pb-4"
      >
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
          </div>
        ) : messages.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-sm text-slate-500">No messages yet</p>
          </div>
        ) : (
          messages.map((m) => <MessageBubble key={m.id} message={m} />)
        )}
      </div>

      {/* Composer */}
      {sessionExpired ? (
        <div className="bg-amber-50 border-t border-amber-200 p-3 text-xs text-amber-900 text-center">
          ⏰ 24-hour window expired. Send a template message to re-engage
          (coming soon).
        </div>
      ) : (
        <div className="bg-white border-t border-slate-200 p-3 flex items-end gap-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Type a message..."
            rows={1}
            className="flex-1 resize-none px-3 py-2 rounded-2xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent max-h-32"
            style={{ minHeight: "40px" }}
            maxLength={4000}
          />
          <button
            onClick={handleSend}
            disabled={!draft.trim() || sendMessage.isPending}
            className="w-10 h-10 rounded-full bg-brand-500 hover:bg-brand-600 text-white flex items-center justify-center transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
          >
            {sendMessage.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </button>
        </div>
      )}
    </div>
  );
}
