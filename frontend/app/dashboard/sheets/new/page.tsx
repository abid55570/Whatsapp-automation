"use client";

import { ArrowLeft, ArrowRight, Check, Copy, Info } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Toggle } from "@/components/ui/Toggle";
import { apiErrorMessage } from "@/lib/api";
import { useCreateSheet } from "@/lib/queries";
import { cn } from "@/lib/utils";
import type { SheetType } from "@/types/api";

interface SampleRow {
  cells: string[];
}

interface TypeSpec {
  value: SheetType;
  emoji: string;
  label: string;
  description: string;
  headers: string[];
  samples: SampleRow[];
}

const TYPES: TypeSpec[] = [
  {
    value: "faqs",
    emoji: "📋",
    label: "FAQs",
    description: "Auto-replies to common questions",
    headers: ["Keywords", "Reply", "Category"],
    samples: [
      { cells: ["price, kitna, rate", "Our prices: ₹300+", "pricing"] },
      { cells: ["timing, hours", "Mon-Sat 10 AM - 9 PM", "info"] },
      { cells: ["address, kaha", "Shop #5, MG Road", "info"] },
    ],
  },
  {
    value: "products",
    emoji: "🛒",
    label: "Products",
    description: "Menu items, retail catalog",
    headers: ["Name", "Price", "SKU", "In Stock"],
    samples: [
      { cells: ["Haircut", "300", "HC01", "yes"] },
      { cells: ["Facial", "800", "FC01", "yes"] },
      { cells: ["Hair Spa", "1250", "HS01", "no"] },
    ],
  },
  {
    value: "services",
    emoji: "💇",
    label: "Services",
    description: "Bookable services & treatments",
    headers: ["Name", "Duration", "Price", "Active"],
    samples: [
      { cells: ["Haircut", "30 min", "300", "yes"] },
      { cells: ["Facial", "60", "800", "yes"] },
      { cells: ["Massage", "45", "1500", "yes"] },
    ],
  },
];

const INTERVAL_OPTIONS = [
  { value: 5, label: "5 min" },
  { value: 15, label: "15 min" },
  { value: 30, label: "30 min" },
  { value: 60, label: "1 hour" },
  { value: 360, label: "6 hours" },
];

export default function NewSheetPage() {
  const router = useRouter();
  const [sheetType, setSheetType] = useState<SheetType>("faqs");
  const [sheetUrl, setSheetUrl] = useState("");
  const [tabName, setTabName] = useState("Sheet1");
  const [autoSync, setAutoSync] = useState(true);
  const [intervalMin, setIntervalMin] = useState(15);

  const create = useCreateSheet();
  const currentSpec = TYPES.find((t) => t.value === sheetType)!;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!sheetUrl.trim()) {
      toast.error("Paste your Google Sheets URL");
      return;
    }
    try {
      await create.mutateAsync({
        sheet_type: sheetType,
        sheet_url: sheetUrl.trim(),
        sheet_tab_name: tabName.trim() || "Sheet1",
        auto_sync: autoSync,
        sync_interval_minutes: intervalMin,
      });
      toast.success("Sheet connected — syncing now");
      router.replace("/dashboard/sheets");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <div className="animate-fade-in">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-900">
              Connect a Sheet
            </h1>
            <p className="text-xs text-slate-500">
              Pick the type and paste your URL
            </p>
          </div>
        </div>
      </header>

      <form onSubmit={handleSubmit} className="p-4 space-y-5">
        {/* Type picker */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            What's in this sheet?
          </label>
          <div className="grid grid-cols-3 gap-2">
            {TYPES.map((t) => {
              const active = sheetType === t.value;
              return (
                <button
                  key={t.value}
                  type="button"
                  onClick={() => setSheetType(t.value)}
                  className={cn(
                    "relative flex flex-col items-center gap-1.5 rounded-xl p-3 border-2 transition active:scale-[0.97]",
                    active
                      ? "border-brand-500 bg-brand-50 ring-2 ring-brand-500/20"
                      : "border-slate-200 bg-white hover:border-slate-300",
                  )}
                >
                  <span className="text-3xl">{t.emoji}</span>
                  <span
                    className={cn(
                      "text-xs font-semibold",
                      active ? "text-brand-700" : "text-slate-700",
                    )}
                  >
                    {t.label}
                  </span>
                  {active && (
                    <div className="absolute top-1 right-1 w-5 h-5 bg-brand-500 rounded-full flex items-center justify-center">
                      <Check
                        className="h-3 w-3 text-white"
                        strokeWidth={3}
                      />
                    </div>
                  )}
                </button>
              );
            })}
          </div>
          <p className="text-xs text-slate-500 mt-2">
            {currentSpec.description}
          </p>
        </div>

        {/* Sample table */}
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="bg-slate-50 px-3 py-2 border-b border-slate-200 flex items-center gap-1.5">
            <Info className="h-3.5 w-3.5 text-slate-500" />
            <p className="text-xs font-semibold text-slate-700">
              Your sheet should look like this:
            </p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className="bg-slate-100 text-slate-700">
                <tr>
                  {currentSpec.headers.map((h) => (
                    <th
                      key={h}
                      className="text-left px-3 py-2 font-semibold whitespace-nowrap"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {currentSpec.samples.map((row, i) => (
                  <tr
                    key={i}
                    className="border-t border-slate-100 odd:bg-slate-50/30"
                  >
                    {row.cells.map((cell, j) => (
                      <td
                        key={j}
                        className="px-3 py-1.5 text-slate-700 whitespace-nowrap"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Service account info */}
        <ServiceAccountCallout />

        {/* URL input */}
        <Input
          label="Sheet URL"
          type="url"
          placeholder="https://docs.google.com/spreadsheets/d/..."
          value={sheetUrl}
          onChange={(e) => setSheetUrl(e.target.value)}
          hint="Copy from your browser address bar"
          required
        />

        {/* Tab name */}
        <Input
          label="Tab name"
          placeholder="Sheet1"
          value={tabName}
          onChange={(e) => setTabName(e.target.value)}
          hint="The bottom tab name in your sheet"
        />

        {/* Auto-sync settings */}
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="font-semibold text-slate-900 text-sm">
                Auto-sync
              </p>
              <p className="text-xs text-slate-500">
                Pull new rows automatically
              </p>
            </div>
            <Toggle checked={autoSync} onChange={setAutoSync} />
          </div>

          {autoSync && (
            <div>
              <p className="text-xs text-slate-600 mb-1.5">
                Sync every
              </p>
              <div className="flex flex-wrap gap-1.5">
                {INTERVAL_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setIntervalMin(opt.value)}
                    className={cn(
                      "px-3 py-1.5 rounded-full text-xs font-medium transition active:scale-95",
                      intervalMin === opt.value
                        ? "bg-brand-500 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200",
                    )}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <Button
          type="submit"
          loading={create.isPending}
          fullWidth
          size="lg"
          disabled={!sheetUrl.trim()}
        >
          Connect Sheet
          <ArrowRight className="h-5 w-5" />
        </Button>
      </form>
    </div>
  );
}

function ServiceAccountCallout() {
  // In production, this would come from settings
  const serviceAccount = "wa-saas@your-project.iam.gserviceaccount.com";
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard.writeText(serviceAccount);
    setCopied(true);
    toast.success("Copied!");
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs">
      <p className="font-semibold text-amber-900 mb-1">
        ⚠️ One-time setup
      </p>
      <p className="text-amber-800 mb-2">
        First, share your sheet with our service account (Viewer access):
      </p>
      <div className="flex items-center gap-1.5">
        <code className="flex-1 bg-white px-2 py-1.5 rounded border border-amber-300 text-[11px] font-mono truncate text-slate-700">
          {serviceAccount}
        </code>
        <button
          type="button"
          onClick={copy}
          className="px-2 py-1.5 bg-white border border-amber-300 rounded text-amber-700 hover:bg-amber-100 active:scale-95 transition"
        >
          {copied ? (
            <Check className="h-3.5 w-3.5" />
          ) : (
            <Copy className="h-3.5 w-3.5" />
          )}
        </button>
      </div>
    </div>
  );
}
