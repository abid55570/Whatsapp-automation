"use client";

import {
  AlertCircle,
  ArrowLeft,
  Download,
  FileJson,
  FileSpreadsheet,
  Info,
  Loader2,
  Receipt,
  TrendingUp,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import {
  downloadGstr1,
  downloadGstr3b,
  downloadItr4,
  downloadPurchaseRegister,
  downloadSalesRegister,
  useGstSettings,
  useReportsOverview,
} from "@/lib/queries";

function fmt(paise: number) {
  return (paise / 100).toLocaleString("en-IN", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
}

function computeCurrentFy(): string {
  const now = new Date();
  const year = now.getMonth() >= 3 ? now.getFullYear() : now.getFullYear() - 1;
  const next = (year + 1) % 100;
  return `${year}-${String(next).padStart(2, "0")}`;
}

function monthOptions(count = 12): { v: string; label: string }[] {
  const now = new Date();
  const out: { v: string; label: string }[] = [];
  for (let i = 0; i < count; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const v = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    const label = d.toLocaleDateString("en-IN", {
      month: "long",
      year: "numeric",
    });
    out.push({ v, label });
  }
  return out;
}

interface DownloadCardProps {
  icon: React.ComponentType<{ className?: string }>;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  onDownload: () => Promise<void>;
  disabled?: boolean;
}

function DownloadCard({
  icon: Icon,
  iconBg,
  iconColor,
  title,
  description,
  onDownload,
  disabled,
}: DownloadCardProps) {
  const [loading, setLoading] = useState(false);
  async function handle() {
    if (disabled || loading) return;
    try {
      setLoading(true);
      await onDownload();
      toast.success(`${title} downloaded`);
    } catch (e) {
      toast.error(`Failed: ${(e as Error).message}`);
    } finally {
      setLoading(false);
    }
  }
  return (
    <button
      onClick={handle}
      disabled={disabled || loading}
      className="w-full text-left bg-white border border-slate-200 hover:border-brand-500 active:scale-[0.99] rounded-xl p-4 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
    >
      <div
        className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${iconBg}`}
      >
        <Icon className={`h-5 w-5 ${iconColor}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-slate-900 truncate">{title}</div>
        <div className="text-xs text-slate-500 truncate">{description}</div>
      </div>
      {loading ? (
        <Loader2 className="h-5 w-5 animate-spin text-slate-500" />
      ) : (
        <Download className="h-5 w-5 text-slate-500" />
      )}
    </button>
  );
}

export default function ReportsPage() {
  const months = monthOptions();
  const [selectedMonth, setSelectedMonth] = useState(months[0].v);
  const { data: gst } = useGstSettings();
  const { data, isLoading } = useReportsOverview(selectedMonth);

  const taxPackEnabled = gst?.tax_pack_enabled ?? false;
  const gstinSet = gst?.gstin || false;

  return (
    <div className="animate-fade-in pb-8">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4 flex items-center gap-3">
        <Link
          href="/dashboard/settings"
          aria-label="Back"
          className="p-2 -m-2 hover:bg-slate-100 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5 text-slate-700" />
        </Link>
        <h1 className="text-base font-bold text-slate-900 flex-1">
          Tax Filing Center
        </h1>
        <select
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(e.target.value)}
          className="text-xs border border-slate-300 rounded-lg px-2 py-1"
        >
          {months.map((m) => (
            <option key={m.v} value={m.v}>
              {m.label}
            </option>
          ))}
        </select>
      </header>

      <div className="p-4 space-y-4">
        {!taxPackEnabled && (
          <Link
            href="/dashboard/settings/billing"
            className="block bg-gradient-to-br from-brand-50 to-emerald-50 border border-brand-200 rounded-xl p-4"
          >
            <div className="flex items-start gap-3">
              <Receipt className="h-6 w-6 text-brand-600 flex-shrink-0 mt-0.5" />
              <div>
                <div className="font-bold text-slate-900">
                  Unlock GSTR + ITR exports
                </div>
                <div className="text-sm text-slate-600 mt-0.5">
                  Tax Pack — ₹299/mo. Download GSTR-1 JSON, GSTR-3B summary,
                  sales register, ITR P&L. Cancel anytime.
                </div>
                <div className="text-sm font-semibold text-brand-700 mt-2">
                  Enable Tax Pack →
                </div>
              </div>
            </div>
          </Link>
        )}

        {!gstinSet && (
          <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl p-3">
            <AlertCircle className="h-5 w-5 text-amber-600 flex-shrink-0" />
            <div className="text-sm">
              <span className="font-semibold text-amber-900">
                GSTIN not set.
              </span>{" "}
              <Link
                href="/dashboard/settings/gst"
                className="text-amber-700 underline"
              >
                Configure GST settings
              </Link>{" "}
              to enable GSTR-1 export.
            </div>
          </div>
        )}

        {/* Period KPIs */}
        {isLoading || !data ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-slate-500" />
          </div>
        ) : (
          <>
            <section className="card">
              <div className="text-xs uppercase text-slate-500 font-semibold mb-3">
                {data.period.label}
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-slate-500 text-xs">Sales invoices</div>
                  <div className="text-2xl font-bold text-slate-900">
                    {data.sales.invoices}
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-xs">Sales total</div>
                  <div className="text-2xl font-bold text-slate-900">
                    ₹{fmt(data.sales.total_paise)}
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-xs">GST collected</div>
                  <div className="text-xl font-bold text-blue-700">
                    ₹{fmt(
                      data.sales.cgst_paise +
                      data.sales.sgst_paise +
                      data.sales.igst_paise,
                    )}
                  </div>
                </div>
                <div>
                  <div className="text-slate-500 text-xs">ITC available</div>
                  <div className="text-xl font-bold text-emerald-700">
                    ₹{fmt(data.purchases.itc_available_paise)}
                  </div>
                </div>
              </div>
              <div className="border-t border-slate-200 mt-3 pt-3 flex justify-between items-baseline">
                <span className="text-sm text-slate-600">Tax to pay (net)</span>
                <span className="text-2xl font-bold text-slate-900">
                  ₹{fmt(data.tax_to_pay_paise)}
                </span>
              </div>
            </section>

            {/* Monthly filing */}
            <section className="space-y-2">
              <div className="text-xs uppercase text-slate-500 font-semibold px-1">
                Monthly filing — {data.period.label}
              </div>
              <DownloadCard
                icon={FileJson}
                iconBg="bg-violet-100"
                iconColor="text-violet-700"
                title="GSTR-1 JSON"
                description="Outward supplies · upload on gst.gov.in"
                onDownload={() => downloadGstr1(selectedMonth)}
                disabled={!gstinSet || !taxPackEnabled}
              />
              <DownloadCard
                icon={FileSpreadsheet}
                iconBg="bg-blue-100"
                iconColor="text-blue-700"
                title="GSTR-3B Summary"
                description="Pre-filled monthly summary · xlsx"
                onDownload={() => downloadGstr3b(selectedMonth)}
                disabled={!taxPackEnabled}
              />
              <DownloadCard
                icon={FileSpreadsheet}
                iconBg="bg-green-100"
                iconColor="text-green-700"
                title="Sales Register"
                description="Every invoice + line + HSN · xlsx"
                onDownload={() =>
                  downloadSalesRegister(data.period.from, data.period.to)
                }
              />
              <DownloadCard
                icon={FileSpreadsheet}
                iconBg="bg-orange-100"
                iconColor="text-orange-700"
                title="Purchase Register"
                description="Supplier bills + ITC · xlsx"
                onDownload={() =>
                  downloadPurchaseRegister(data.period.from, data.period.to)
                }
              />
            </section>

            {/* Annual filing — ITR */}
            <section className="space-y-2">
              <div className="text-xs uppercase text-slate-500 font-semibold px-1 pt-2">
                Annual filing
              </div>
              <DownloadCard
                icon={FileSpreadsheet}
                iconBg="bg-indigo-100"
                iconColor="text-indigo-700"
                title={`ITR-4 P&L · FY ${computeCurrentFy()}`}
                description="Presumptive scheme P&L for income-tax return"
                onDownload={() => downloadItr4(computeCurrentFy())}
                disabled={!taxPackEnabled}
              />
            </section>

            {/* Purchase invoices CTA */}
            <Link
              href="/dashboard/purchase-invoices"
              className="block bg-white border border-slate-200 rounded-xl p-4 hover:border-slate-300"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-amber-700" />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-slate-900">
                    Add supplier bills
                  </div>
                  <div className="text-xs text-slate-500">
                    {data.purchases.bills} bills this month · enter more for
                    accurate ITC
                  </div>
                </div>
              </div>
            </Link>
          </>
        )}

        <div className="flex items-start gap-2 bg-slate-50 border border-slate-200 rounded-xl p-3 mt-4">
          <Info className="h-4 w-4 text-slate-500 flex-shrink-0 mt-0.5" />
          <div className="text-xs text-slate-600">
            <span className="font-semibold">Disclaimer:</span> Verify all
            figures with your CA before filing. Whatly auto-computes from
            issued invoices and recorded purchases — it is not a substitute for
            professional tax advice.
          </div>
        </div>
      </div>
    </div>
  );
}
