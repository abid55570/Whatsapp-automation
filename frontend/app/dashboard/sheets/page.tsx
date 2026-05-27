"use client";

import { ArrowLeft, FileSpreadsheet, Loader2, Plus } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { SheetCard } from "@/components/SheetCard";
import { useSheets } from "@/lib/queries";

export default function SheetsListPage() {
  const router = useRouter();
  const { data: sheets, isLoading } = useSheets();

  const items = sheets ?? [];

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3 mb-2">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-slate-900">
              Google Sheets
            </h1>
            <p className="text-xs text-slate-500">
              Edit a sheet → bot updates instantly
            </p>
          </div>
          <Link
            href="/dashboard/sheets/new"
            className="inline-flex items-center gap-1.5 bg-brand-500 hover:bg-brand-600 text-white text-sm font-semibold px-3 py-2 rounded-xl transition active:scale-95"
          >
            <Plus className="h-4 w-4" />
            Add
          </Link>
        </div>
      </header>

      <div className="p-4">
        {/* How-it-works card */}
        {items.length === 0 && !isLoading && (
          <div className="card bg-gradient-to-br from-brand-50 to-emerald-50 border border-brand-200 mb-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">💡</span>
              <div className="text-sm">
                <h3 className="font-semibold text-slate-900 mb-2">
                  How it works
                </h3>
                <ol className="list-decimal list-inside space-y-1 text-slate-700 text-xs">
                  <li>
                    Create a Google Sheet with FAQs / menu / services
                  </li>
                  <li>
                    Share it with our service account (view access)
                  </li>
                  <li>Paste the sheet URL here</li>
                  <li>
                    Edit your sheet anytime — auto-syncs every 15 min
                  </li>
                </ol>
              </div>
            </div>
          </div>
        )}

        {/* List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
          </div>
        ) : items.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-3">
            {items.map((s) => (
              <SheetCard key={s.id} sheet={s} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="text-center py-12">
      <div className="inline-flex w-16 h-16 rounded-2xl bg-slate-100 items-center justify-center mb-4">
        <FileSpreadsheet className="h-7 w-7 text-slate-400" />
      </div>
      <h2 className="font-semibold text-slate-900 mb-1">
        No sheets connected yet
      </h2>
      <p className="text-sm text-slate-500 mb-6 max-w-xs mx-auto">
        Connect a Google Sheet to auto-sync your FAQs, menu, or services.
      </p>
      <Link
        href="/dashboard/sheets/new"
        className="inline-flex items-center gap-1.5 bg-brand-500 hover:bg-brand-600 text-white font-semibold px-5 py-2.5 rounded-xl transition active:scale-95"
      >
        <Plus className="h-4 w-4" />
        Add your first sheet
      </Link>
    </div>
  );
}
