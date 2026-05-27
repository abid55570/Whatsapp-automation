"use client";

import {
  AlertCircle,
  CheckCircle2,
  Clock,
  ExternalLink,
  Loader2,
  RefreshCw,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { apiErrorMessage } from "@/lib/api";
import {
  useDeleteSheet,
  useTriggerSheetSync,
  useUpdateSheet,
} from "@/lib/queries";
import { cn } from "@/lib/utils";
import type { SheetSync } from "@/types/api";

import { Toggle } from "./ui/Toggle";

const TYPE_INFO: Record<string, { emoji: string; label: string; color: string }> = {
  faqs: { emoji: "📋", label: "FAQs", color: "bg-amber-100 text-amber-700" },
  products: { emoji: "🛒", label: "Products", color: "bg-blue-100 text-blue-700" },
  services: { emoji: "💇", label: "Services", color: "bg-pink-100 text-pink-700" },
  customers: { emoji: "👥", label: "Customers", color: "bg-indigo-100 text-indigo-700" },
};

function formatRelative(iso: string | null): string {
  if (!iso) return "never";
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  const m = Math.floor(diff / 60_000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const days = Math.floor(h / 24);
  return `${days}d ago`;
}

export function SheetCard({ sheet }: { sheet: SheetSync }) {
  const triggerSync = useTriggerSheetSync();
  const updateSheet = useUpdateSheet();
  const deleteSheet = useDeleteSheet();
  const [confirmDelete, setConfirmDelete] = useState(false);

  const info = TYPE_INFO[sheet.sheet_type] ?? {
    emoji: "📊",
    label: "Sheet",
    color: "bg-slate-100 text-slate-700",
  };

  const status = sheet.last_sync_status;

  async function handleSyncNow() {
    try {
      await triggerSync.mutateAsync(sheet.id);
      toast.success("Sync queued");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  async function handleDelete() {
    if (!confirmDelete) {
      setConfirmDelete(true);
      setTimeout(() => setConfirmDelete(false), 3000);
      return;
    }
    try {
      await deleteSheet.mutateAsync(sheet.id);
      toast.success("Sheet removed");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  async function handleToggleAuto(next: boolean) {
    try {
      await updateSheet.mutateAsync({
        id: sheet.id,
        data: { auto_sync: next },
      });
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <div className="card">
      <div className="flex items-start gap-3">
        <div
          className={cn(
            "w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0",
            info.color,
          )}
        >
          {info.emoji}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold text-slate-900">{info.label}</h3>
            <StatusBadge status={status} />
          </div>
          <p className="text-xs text-slate-500 truncate mt-0.5 font-mono">
            {sheet.sheet_tab_name} · {sheet.sheet_id.slice(0, 12)}...
          </p>
          <div className="flex items-center gap-3 mt-1.5 text-xs text-slate-600">
            <span>
              <span className="font-semibold">{sheet.rows_synced}</span> rows
            </span>
            <span className="text-slate-300">·</span>
            <span>Last sync: {formatRelative(sheet.last_synced_at)}</span>
          </div>
        </div>
      </div>

      {sheet.last_sync_error && (
        <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
          <AlertCircle className="h-3.5 w-3.5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-red-700 break-words">
            {sheet.last_sync_error}
          </p>
        </div>
      )}

      <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100">
        <div className="flex items-center gap-2 text-xs text-slate-600">
          <Toggle
            checked={sheet.auto_sync}
            onChange={handleToggleAuto}
          />
          <span>Auto-sync ({sheet.sync_interval_minutes}m)</span>
        </div>
      </div>

      <div className="flex gap-1.5 mt-2">
        <button
          onClick={handleSyncNow}
          disabled={triggerSync.isPending}
          className="flex-1 inline-flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium bg-brand-50 text-brand-700 hover:bg-brand-100 active:scale-[0.97] transition disabled:opacity-50"
        >
          {triggerSync.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <RefreshCw className="h-3.5 w-3.5" />
          )}
          Sync now
        </button>
        <a
          href={sheet.sheet_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium bg-slate-100 text-slate-700 hover:bg-slate-200 active:scale-[0.97] transition"
        >
          <ExternalLink className="h-3.5 w-3.5" />
          Open
        </a>
        <button
          onClick={handleDelete}
          disabled={deleteSheet.isPending}
          className={cn(
            "inline-flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium transition active:scale-[0.97]",
            confirmDelete
              ? "bg-red-500 text-white hover:bg-red-600"
              : "bg-slate-100 text-slate-600 hover:bg-red-50 hover:text-red-600",
          )}
        >
          <Trash2 className="h-3.5 w-3.5" />
          {confirmDelete && "Sure?"}
        </button>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string | null }) {
  if (status === "ok") {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-emerald-100 text-emerald-700 text-[10px] font-semibold">
        <CheckCircle2 className="h-2.5 w-2.5" />
        Synced
      </span>
    );
  }
  if (status === "error") {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-semibold">
        <AlertCircle className="h-2.5 w-2.5" />
        Error
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-semibold">
      <Clock className="h-2.5 w-2.5" />
      Pending
    </span>
  );
}
