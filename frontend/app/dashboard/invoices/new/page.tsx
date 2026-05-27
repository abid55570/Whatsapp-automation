"use client";

import { ArrowLeft, Loader2, Plus, Sparkles, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { suggestHsn, useCreateInvoice, type HsnSuggestion } from "@/lib/queries";

interface Line {
  description: string;
  hsn_code: string;
  quantity: string;
  unit: string;
  rate_rupees: string;
  gst_rate: number;
}

const EMPTY_LINE: Line = {
  description: "",
  hsn_code: "",
  quantity: "1",
  unit: "pc",
  rate_rupees: "",
  gst_rate: 0,
};

const GST_RATES = [0, 5, 12, 18, 28];

export default function NewInvoicePage() {
  const router = useRouter();
  const create = useCreateInvoice();

  const [cxName, setCxName] = useState("");
  const [cxPhone, setCxPhone] = useState("");
  const [cxGstin, setCxGstin] = useState("");
  const [cxStateCode, setCxStateCode] = useState("");
  const [notes, setNotes] = useState("");
  const [lines, setLines] = useState<Line[]>([{ ...EMPTY_LINE }]);

  const subtotal = lines.reduce((sum, l) => {
    const qty = parseFloat(l.quantity) || 0;
    const rate = parseFloat(l.rate_rupees) || 0;
    return sum + qty * rate;
  }, 0);

  function update(i: number, patch: Partial<Line>) {
    setLines((cur) => cur.map((l, idx) => (idx === i ? { ...l, ...patch } : l)));
  }

  function addLine() {
    setLines((cur) => [...cur, { ...EMPTY_LINE }]);
  }

  function removeLine(i: number) {
    setLines((cur) => cur.filter((_, idx) => idx !== i));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (lines.length === 0 || lines.every((l) => !l.description.trim())) {
      toast.error("Add at least one item");
      return;
    }
    try {
      const created = await create.mutateAsync({
        cx_name: cxName.trim() || undefined,
        cx_phone: cxPhone.trim() || undefined,
        cx_gstin: cxGstin.trim().toUpperCase() || undefined,
        cx_state_code: cxStateCode.trim() || undefined,
        notes: notes.trim() || undefined,
        issue_now: true,
        lines: lines
          .filter((l) => l.description.trim())
          .map((l) => ({
            description: l.description.trim(),
            hsn_code: l.hsn_code.trim() || null,
            quantity: l.quantity || "1",
            unit: l.unit || "pc",
            rate_paise: Math.round((parseFloat(l.rate_rupees) || 0) * 100),
            gst_rate: l.gst_rate,
          })),
      });
      toast.success(`Invoice ${created.invoice_number} created`);
      router.replace(`/dashboard/invoices/${created.id}`);
    } catch (e) {
      toast.error("Create failed: " + (e as Error).message);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="animate-fade-in pb-32">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4 flex items-center gap-3">
        <Link
          href="/dashboard/invoices"
          aria-label="Back"
          className="p-2 -m-2 hover:bg-slate-100 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5 text-slate-700" />
        </Link>
        <h1 className="text-base font-bold text-slate-900">New Invoice</h1>
      </header>

      <div className="p-4 space-y-4">
        <section className="card space-y-3">
          <div className="text-xs uppercase text-slate-500 font-semibold">
            Customer
          </div>
          <input
            value={cxName}
            onChange={(e) => setCxName(e.target.value)}
            placeholder="Name (optional)"
            className="input w-full"
            maxLength={200}
          />
          <input
            value={cxPhone}
            onChange={(e) => setCxPhone(e.target.value)}
            placeholder="WhatsApp number (optional)"
            type="tel"
            inputMode="numeric"
            className="input w-full"
            maxLength={20}
          />
          <input
            value={cxGstin}
            onChange={(e) => setCxGstin(e.target.value.toUpperCase())}
            placeholder="GSTIN (if B2B)"
            className="input w-full font-mono"
            maxLength={15}
          />
          <input
            value={cxStateCode}
            onChange={(e) => setCxStateCode(e.target.value)}
            placeholder="State code (e.g. 27 for Maharashtra)"
            className="input w-full"
            maxLength={2}
            inputMode="numeric"
          />
        </section>

        <section className="space-y-2">
          <div className="text-xs uppercase text-slate-500 font-semibold px-1">
            Items
          </div>
          {lines.map((line, i) => (
            <div key={i} className="card space-y-2">
              <div className="flex items-start gap-2">
                <div className="flex-1 relative">
                  <input
                    value={line.description}
                    onChange={(e) => update(i, { description: e.target.value })}
                    onBlur={async () => {
                      // Auto-suggest HSN + GST rate when description changes
                      // and no HSN is already set.
                      if (!line.description.trim() || line.hsn_code) return;
                      try {
                        const suggestions = await suggestHsn(line.description, 1);
                        if (suggestions.length > 0 && suggestions[0].score >= 80) {
                          const s = suggestions[0];
                          update(i, {
                            hsn_code: s.code,
                            gst_rate: s.rate,
                            unit: line.unit === "pc" ? s.unit : line.unit,
                          });
                          toast.success(
                            `HSN ${s.code} (${s.rate}% GST) auto-filled for "${line.description}"`,
                            { duration: 2000 },
                          );
                        }
                      } catch {
                        /* silent — typing user shouldn't see network errors */
                      }
                    }}
                    placeholder={`Item ${i + 1} name *`}
                    className="input w-full"
                    required
                    maxLength={500}
                  />
                  {line.description && line.hsn_code && (
                    <Sparkles className="absolute right-2 top-2.5 h-4 w-4 text-amber-400" />
                  )}
                </div>
                {lines.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeLine(i)}
                    aria-label="Remove item"
                    className="p-2 hover:bg-red-50 rounded-lg text-red-500"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
              <div className="grid grid-cols-3 gap-2">
                <input
                  value={line.quantity}
                  onChange={(e) => update(i, { quantity: e.target.value })}
                  placeholder="Qty"
                  type="number"
                  step="0.001"
                  min="0"
                  inputMode="decimal"
                  className="input"
                />
                <input
                  value={line.unit}
                  onChange={(e) => update(i, { unit: e.target.value })}
                  placeholder="Unit"
                  className="input"
                  maxLength={10}
                />
                <input
                  value={line.rate_rupees}
                  onChange={(e) => update(i, { rate_rupees: e.target.value })}
                  placeholder="₹ Rate"
                  type="number"
                  step="0.01"
                  min="0"
                  inputMode="decimal"
                  className="input"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <input
                  value={line.hsn_code}
                  onChange={(e) => update(i, { hsn_code: e.target.value })}
                  placeholder="HSN code (optional)"
                  className="input"
                  maxLength={8}
                  inputMode="numeric"
                />
                <select
                  value={line.gst_rate}
                  onChange={(e) =>
                    update(i, { gst_rate: parseInt(e.target.value) })
                  }
                  className="input"
                >
                  {GST_RATES.map((r) => (
                    <option key={r} value={r}>
                      GST {r}%
                    </option>
                  ))}
                </select>
              </div>
            </div>
          ))}
          <button
            type="button"
            onClick={addLine}
            className="w-full flex items-center justify-center gap-2 border-2 border-dashed border-slate-300 hover:border-brand-500 hover:text-brand-600 text-slate-600 font-semibold py-3 rounded-xl transition min-h-[44px]"
          >
            <Plus className="h-4 w-4" />
            Add item
          </button>
        </section>

        <section className="card">
          <div className="text-xs uppercase text-slate-500 font-semibold mb-2">
            Notes (optional)
          </div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            dir="auto"
            rows={2}
            placeholder="e.g. Thank you for your business!"
            className="input w-full resize-none"
            maxLength={500}
          />
        </section>

        <section className="card">
          <div className="flex justify-between text-base">
            <span className="text-slate-600">Estimated subtotal</span>
            <span className="font-bold text-slate-900">
              ₹{subtotal.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </span>
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Tax + round-off computed after issue.
          </div>
        </section>
      </div>

      <div className="fixed bottom-[calc(64px+env(safe-area-inset-bottom))] left-0 right-0 bg-white border-t border-slate-200 p-3 z-20 max-w-md mx-auto">
        <button
          type="submit"
          disabled={create.isPending}
          className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-bold text-base py-3.5 rounded-xl transition active:scale-95 disabled:opacity-50 min-h-[48px]"
        >
          {create.isPending && <Loader2 className="h-5 w-5 animate-spin" />}
          Issue Invoice
        </button>
      </div>
    </form>
  );
}
