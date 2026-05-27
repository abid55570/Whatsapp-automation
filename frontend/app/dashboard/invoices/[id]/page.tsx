"use client";

import {
  ArrowLeft,
  Ban,
  CheckCircle2,
  Download,
  FileCheck,
  Loader2,
  Share2,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import {
  downloadInvoicePdf,
  useCancelInvoice,
  useGenerateEInvoiceIrn,
  useInvoice,
  useShareInvoice,
} from "@/lib/queries";
import { cn } from "@/lib/utils";

function fmt(paise: number) {
  return (paise / 100).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export default function InvoiceDetailPage() {
  const params = useParams();
  const invoiceId = params.id as string;
  const { data: inv, isLoading } = useInvoice(invoiceId);
  const cancel = useCancelInvoice(invoiceId);
  const share = useShareInvoice(invoiceId);
  const generateIrn = useGenerateEInvoiceIrn(invoiceId);
  const [downloading, setDownloading] = useState(false);
  const [showCancelForm, setShowCancelForm] = useState(false);
  const [cancelReason, setCancelReason] = useState("");

  if (isLoading || !inv) {
    return (
      <div className="flex justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-slate-500" />
      </div>
    );
  }

  const intraState = inv.cgst_paise > 0 || inv.sgst_paise > 0;
  const totalTax = inv.cgst_paise + inv.sgst_paise + inv.igst_paise;

  async function handleDownload() {
    if (!inv) return;
    try {
      setDownloading(true);
      await downloadInvoicePdf(inv.id, inv.invoice_number);
    } catch (e) {
      toast.error("Download failed: " + (e as Error).message);
    } finally {
      setDownloading(false);
    }
  }

  async function handleShare() {
    try {
      const result = await share.mutateAsync({});
      toast.success(
        result.sent ? "Invoice sent on WhatsApp" : "Customer not on WhatsApp",
      );
    } catch (e) {
      toast.error("Share failed: " + (e as Error).message);
    }
  }

  async function submitCancel() {
    const trimmed = cancelReason.trim();
    if (!trimmed) {
      toast.error("Please enter a reason");
      return;
    }
    try {
      await cancel.mutateAsync({ reason: trimmed });
      toast.success("Invoice cancelled");
      setShowCancelForm(false);
      setCancelReason("");
    } catch (e) {
      toast.error("Cancel failed: " + (e as Error).message);
    }
  }

  const isCancelled = inv.status === "cancelled";
  const eligibleForIrn =
    !isCancelled &&
    !inv.irn &&
    (inv.invoice_type === "b2b" || inv.invoice_type === "export");

  async function handleGenerateIrn() {
    try {
      const result = await generateIrn.mutateAsync();
      toast.success(
        result.idempotent
          ? "Invoice already has an IRN"
          : `IRN generated: ${result.irn.slice(0, 12)}…`,
      );
    } catch (e) {
      toast.error("IRN generation failed: " + (e as Error).message);
    }
  }

  return (
    <div className="animate-fade-in pb-8">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4 flex items-center gap-3">
        <Link
          href="/dashboard/invoices"
          aria-label="Back"
          className="p-2 -m-2 hover:bg-slate-100 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5 text-slate-700" />
        </Link>
        <h1 className="text-base font-bold text-slate-900 flex-1">
          {inv.invoice_number}
        </h1>
        <span
          className={cn(
            "px-2 py-0.5 text-[10px] font-semibold rounded uppercase",
            inv.status === "paid"
              ? "bg-green-100 text-green-700"
              : inv.status === "issued"
              ? "bg-blue-100 text-blue-700"
              : inv.status === "cancelled"
              ? "bg-red-100 text-red-700"
              : "bg-slate-100 text-slate-700",
          )}
        >
          {inv.status}
        </span>
      </header>

      <div className="p-4 space-y-4">
        {/* Action buttons */}
        {!isCancelled && (
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="flex items-center justify-center gap-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold py-3 rounded-xl transition active:scale-95 disabled:opacity-50 min-h-[44px]"
            >
              {downloading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              Download PDF
            </button>
            <button
              onClick={handleShare}
              disabled={share.isPending}
              className="flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold py-3 rounded-xl transition active:scale-95 disabled:opacity-50 min-h-[44px]"
            >
              {share.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Share2 className="h-4 w-4" />
              )}
              Send WhatsApp
            </button>
          </div>
        )}

        {/* e-invoice IRN */}
        {inv.irn && (
          <section className="bg-emerald-50 border border-emerald-200 rounded-xl p-3">
            <div className="flex items-start gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-semibold text-emerald-900">
                  e-Invoice (IRN) registered
                </div>
                <div className="text-[11px] font-mono text-emerald-700 break-all mt-0.5">
                  {inv.irn}
                </div>
              </div>
            </div>
          </section>
        )}
        {eligibleForIrn && (
          <button
            onClick={handleGenerateIrn}
            disabled={generateIrn.isPending}
            className="w-full flex items-center justify-center gap-2 border border-indigo-300 text-indigo-700 hover:bg-indigo-50 font-semibold py-3 rounded-xl transition disabled:opacity-50 min-h-[44px]"
          >
            {generateIrn.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileCheck className="h-4 w-4" />
            )}
            Generate e-Invoice IRN
          </button>
        )}

        {/* Customer block */}
        <section className="card">
          <div className="text-xs uppercase text-slate-500 font-semibold mb-1">
            Customer
          </div>
          <div className="font-semibold text-slate-900">
            {inv.cx_name || "Cash Customer"}
          </div>
          {inv.cx_phone && (
            <div className="text-sm text-slate-600">{inv.cx_phone}</div>
          )}
          {inv.cx_gstin && (
            <div className="text-sm text-slate-600 font-mono">
              GSTIN: {inv.cx_gstin}
            </div>
          )}
          {inv.cx_address && (
            <div className="text-sm text-slate-600">{inv.cx_address}</div>
          )}
          {inv.place_of_supply && (
            <div className="text-xs text-slate-500 mt-1">
              Place of supply: {inv.place_of_supply}
            </div>
          )}
        </section>

        {/* Lines */}
        <section className="card">
          <div className="text-xs uppercase text-slate-500 font-semibold mb-2">
            Items ({inv.lines.length})
          </div>
          <div className="space-y-2">
            {inv.lines.map((line) => (
              <div
                key={line.id}
                className="flex justify-between text-sm border-b border-slate-100 pb-2 last:border-0 last:pb-0"
              >
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-slate-900">
                    {line.description}
                  </div>
                  <div className="text-xs text-slate-500">
                    {line.quantity} {line.unit} × ₹{fmt(line.rate_paise)}
                    {line.gst_rate > 0 && (
                      <span className="ml-2 px-1 py-0.5 bg-slate-100 rounded text-[10px]">
                        GST {line.gst_rate}%
                      </span>
                    )}
                    {line.hsn_code && (
                      <span className="ml-2 text-[10px] text-slate-500">
                        HSN {line.hsn_code}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right font-semibold text-slate-900">
                  ₹{fmt(line.total_paise)}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Totals */}
        <section className="card">
          <table className="w-full text-sm">
            <tbody>
              <tr>
                <td className="text-slate-600 py-1">Subtotal</td>
                <td className="text-right">₹{fmt(inv.subtotal_paise)}</td>
              </tr>
              {inv.discount_paise > 0 && (
                <tr>
                  <td className="text-slate-600 py-1">Discount</td>
                  <td className="text-right">− ₹{fmt(inv.discount_paise)}</td>
                </tr>
              )}
              <tr>
                <td className="text-slate-600 py-1">Taxable</td>
                <td className="text-right">₹{fmt(inv.taxable_paise)}</td>
              </tr>
              {intraState ? (
                <>
                  <tr>
                    <td className="text-slate-600 py-1">CGST</td>
                    <td className="text-right">₹{fmt(inv.cgst_paise)}</td>
                  </tr>
                  <tr>
                    <td className="text-slate-600 py-1">SGST</td>
                    <td className="text-right">₹{fmt(inv.sgst_paise)}</td>
                  </tr>
                </>
              ) : inv.igst_paise > 0 ? (
                <tr>
                  <td className="text-slate-600 py-1">IGST</td>
                  <td className="text-right">₹{fmt(inv.igst_paise)}</td>
                </tr>
              ) : null}
              {inv.cess_paise > 0 && (
                <tr>
                  <td className="text-slate-600 py-1">Cess</td>
                  <td className="text-right">₹{fmt(inv.cess_paise)}</td>
                </tr>
              )}
              {inv.round_off_paise !== 0 && (
                <tr>
                  <td className="text-slate-600 py-1">Round off</td>
                  <td className="text-right">₹{fmt(inv.round_off_paise)}</td>
                </tr>
              )}
              <tr className="border-t-2 border-slate-900">
                <td className="font-bold text-slate-900 py-2 text-base">
                  Total
                </td>
                <td className="text-right font-bold text-slate-900 py-2 text-base">
                  ₹{fmt(inv.total_paise)}
                </td>
              </tr>
            </tbody>
          </table>
        </section>

        {/* Notes / cancellation */}
        {inv.notes && (
          <section className="card">
            <div className="text-xs uppercase text-slate-500 font-semibold mb-1">
              Notes
            </div>
            <p className="text-sm text-slate-700">{inv.notes}</p>
          </section>
        )}

        {isCancelled && (
          <section className="bg-red-50 border border-red-200 rounded-xl p-4">
            <div className="text-sm font-semibold text-red-700">
              This invoice has been cancelled
            </div>
            {inv.cancellation_reason && (
              <div className="text-sm text-red-600 mt-1">
                Reason: {inv.cancellation_reason}
              </div>
            )}
          </section>
        )}

        {/* Cancel button + inline form */}
        {!isCancelled && !showCancelForm && (
          <button
            onClick={() => setShowCancelForm(true)}
            disabled={cancel.isPending}
            className="w-full flex items-center justify-center gap-2 border border-red-300 text-red-700 hover:bg-red-50 font-semibold py-3 rounded-xl transition disabled:opacity-50 min-h-[44px]"
          >
            <Ban className="h-4 w-4" />
            Cancel invoice
          </button>
        )}
        {!isCancelled && showCancelForm && (
          <div className="card border-red-200 bg-red-50 space-y-2">
            <label className="text-sm font-semibold text-red-900 block">
              Reason for cancellation
            </label>
            <textarea
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              dir="auto"
              rows={2}
              maxLength={500}
              placeholder="e.g. Wrong customer / order changed"
              className="input w-full resize-none"
              autoFocus
            />
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => {
                  setShowCancelForm(false);
                  setCancelReason("");
                }}
                className="border border-slate-300 text-slate-700 font-semibold py-2.5 rounded-lg min-h-[44px]"
              >
                Keep invoice
              </button>
              <button
                onClick={submitCancel}
                disabled={cancel.isPending}
                className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2.5 rounded-lg disabled:opacity-50 min-h-[44px]"
              >
                {cancel.isPending ? "Cancelling…" : "Yes, cancel"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
