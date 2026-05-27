"use client";

import { FileText, Filter, Loader2, Plus } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import { useInvoices } from "@/lib/queries";
import { cn } from "@/lib/utils";
import type { InvoiceStatus } from "@/types/api";

const STATUS_TABS: { v: InvoiceStatus | "all"; label: string }[] = [
  { v: "all", label: "All" },
  { v: "issued", label: "Issued" },
  { v: "paid", label: "Paid" },
  { v: "draft", label: "Draft" },
  { v: "cancelled", label: "Cancelled" },
];

const STATUS_CLASS: Record<InvoiceStatus, string> = {
  draft: "bg-slate-100 text-slate-700",
  issued: "bg-blue-100 text-blue-700",
  paid: "bg-green-100 text-green-700",
  cancelled: "bg-red-100 text-red-700",
};

export default function InvoicesPage() {
  const [status, setStatus] = useState<InvoiceStatus | "all">("all");
  const { data, isLoading } = useInvoices(status);

  return (
    <div className="animate-fade-in pb-8">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">Invoices</h1>
        <Link
          href="/dashboard/invoices/new"
          className="inline-flex items-center gap-1.5 bg-brand-600 hover:bg-brand-700 text-white text-sm font-semibold px-3 py-2 rounded-lg transition active:scale-95 min-h-[40px]"
        >
          <Plus className="h-4 w-4" />
          New
        </Link>
      </header>

      <div className="px-4 py-3 flex gap-1.5 overflow-x-auto">
        {STATUS_TABS.map((tab) => (
          <button
            key={tab.v}
            onClick={() => setStatus(tab.v)}
            className={cn(
              "px-3 py-1.5 text-xs font-semibold rounded-full whitespace-nowrap transition min-h-[32px]",
              status === tab.v
                ? "bg-slate-900 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {isLoading || !data ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-slate-500" />
        </div>
      ) : data.items.length === 0 ? (
        <div className="px-4 py-16 text-center">
          <FileText className="h-12 w-12 mx-auto text-slate-300 mb-3" />
          <p className="text-slate-600 mb-4">No invoices yet</p>
          <Link
            href="/dashboard/invoices/new"
            className="inline-flex items-center gap-1.5 bg-brand-600 text-white px-4 py-2 rounded-lg font-semibold"
          >
            <Plus className="h-4 w-4" />
            Create first invoice
          </Link>
        </div>
      ) : (
        <div className="px-4 space-y-2">
          {data.items.map((inv) => {
            const total = (inv.total_paise / 100).toLocaleString("en-IN", {
              maximumFractionDigits: 2,
            });
            return (
              <Link
                key={inv.id}
                href={`/dashboard/invoices/${inv.id}`}
                className="block bg-white border border-slate-200 rounded-xl p-3 hover:border-slate-300 active:scale-[0.99] transition"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-slate-900">
                        {inv.invoice_number}
                      </span>
                      <span
                        className={cn(
                          "px-1.5 py-0.5 text-[10px] font-semibold rounded uppercase",
                          STATUS_CLASS[inv.status],
                        )}
                      >
                        {inv.status}
                      </span>
                    </div>
                    <div className="text-sm text-slate-600 truncate">
                      {inv.cx_name || "Cash Customer"}
                      {inv.cx_gstin && (
                        <span className="text-[10px] font-mono ml-2 text-slate-500">
                          GSTIN
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-slate-500 mt-0.5">
                      {new Date(inv.invoice_date).toLocaleDateString("en-IN", {
                        day: "2-digit",
                        month: "short",
                        year: "numeric",
                      })}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-base font-bold text-slate-900">
                      ₹{total}
                    </div>
                    {inv.cgst_paise + inv.sgst_paise + inv.igst_paise > 0 && (
                      <div className="text-[10px] text-slate-500">
                        incl. GST
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
          <div className="text-xs text-slate-500 text-center pt-2">
            {data.total} total
          </div>
        </div>
      )}
    </div>
  );
}
