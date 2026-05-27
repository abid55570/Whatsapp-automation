"use client";

import { AlertCircle, Bot, Check, CheckCheck } from "lucide-react";

import { cn } from "@/lib/utils";
import type { MessageDetail } from "@/types/api";

interface Props {
  message: MessageDetail;
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

function StatusIcon({ status }: { status: string }) {
  if (status === "read") return <CheckCheck className="h-3.5 w-3.5 text-blue-300" />;
  if (status === "delivered") return <CheckCheck className="h-3.5 w-3.5 text-brand-50" />;
  if (status === "sent") return <Check className="h-3.5 w-3.5 text-brand-50" />;
  if (status === "failed")
    return <AlertCircle className="h-3.5 w-3.5 text-red-300" />;
  return null;
}

export function MessageBubble({ message }: Props) {
  const isOutbound = message.direction === "outbound";
  const failed = message.status === "failed";

  return (
    <div className={cn("flex animate-fade-in", isOutbound ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[78%] rounded-2xl px-3.5 py-2 shadow-sm",
          isOutbound
            ? "bg-brand-500 text-white rounded-br-md"
            : "bg-white text-slate-900 rounded-bl-md border border-slate-200",
          failed && "ring-2 ring-red-300",
        )}
      >
        {message.is_auto_reply && (
          <div
            className={cn(
              "inline-flex items-center gap-1 text-[10px] font-semibold mb-1 px-1.5 py-0.5 rounded",
              isOutbound
                ? "bg-brand-600 text-brand-50"
                : "bg-emerald-100 text-emerald-700",
            )}
          >
            <Bot className="h-3 w-3" />
            Auto-reply
          </div>
        )}

        {message.body && (
          <p
            className={cn(
              "text-sm whitespace-pre-wrap break-words leading-relaxed",
            )}
          >
            {message.body}
          </p>
        )}

        {message.media_url && (
          <p className="text-xs italic mt-1 opacity-80">
            📎 {message.type} attachment
          </p>
        )}

        <div
          className={cn(
            "flex items-center justify-end gap-1 mt-1",
            isOutbound ? "text-brand-50" : "text-slate-400",
          )}
        >
          <span className="text-[10px]">{formatTime(message.created_at)}</span>
          {isOutbound && <StatusIcon status={message.status} />}
        </div>

        {failed && message.failed_reason && (
          <p className="text-[10px] text-red-200 mt-1 italic">
            {message.failed_reason}
          </p>
        )}
      </div>
    </div>
  );
}
