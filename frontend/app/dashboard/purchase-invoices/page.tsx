"use client";

import {
  ArrowLeft,
  Loader2,
  Plus,
  Receipt,
  Trash2,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";

import {
  useCreatePurchaseInvoice,
  useDeletePurchaseInvoice,
  usePurchaseInvoices,
} from "@/lib/queries";

function fmt(paise: number) {
  return (paise / 100).toLocaleString("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export default function PurchaseInvoicesPage() {
  const { data, isLoading } = usePurchaseInvoices();
  const create = useCreatePurchaseInvoice();
  const del = useDeletePurchaseInvoice();
  const [showForm, setShowForm] = useState(false);

  // Form state
  const today = new Date().toISOString().slice(0, 10);
  const [form, setForm] = useState({
    supplier_name: "",
    supplier_gstin: "",
    bill_number: "",
    bill_date: today,
    taxable: "",
    cgst: "",
    sgst: "",
    igst: "",
    total: "",
    is_capital_goods: false,
    is_itc_eligible: true,
    category: "",
  });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await create.mutateAsync({
        supplier_name: form.supplier_name.trim(),
        supplier_gstin: form.supplier_gstin.trim().toUpperCase() || undefined,
        bill_number: form.bill_number.trim(),
        bill_date: form.bill_date,
        taxable_paise: Math.round(parseFloat(form.taxable || "0") * 100),
        cgst_paise: Math.round(parseFloat(form.cgst || "0") * 100),
        sgst_paise: Math.round(parseFloat(form.sgst || "0") * 100),
        igst_paise: Math.round(parseFloat(form.igst || "0") * 100),
        total_paise: Math.round(parseFloat(form.total || "0") * 100),
        category: form.category.trim() || undefined,
        is_capital_goods: form.is_capital_goods,
        is_itc_eligible: form.is_itc_eligible,
      });
      toast.success("Purchase bill added");
      setShowForm(false);
      setForm({
        supplier_name: "",
        supplier_gstin: "",
        bill_number: "",
        bill_date: today,
        taxable: "",
        cgst: "",
        sgst: "",
        igst: "",
        total: "",
        is_capital_goods: false,
        is_itc_eligible: true,
        category: "",
      });
    } catch (e) {
      toast.error("Save failed: " + (e as Error).message);
    }
  }

  async function handleDelete(id: string, bill: string) {
    toast(`Delete bill ${bill}?`, {
      duration: 8000,
      action: {
        label: "Delete",
        onClick: async () => {
          try {
            await del.mutateAsync(id);
            toast.success("Bill deleted");
          } catch (e) {
            toast.error("Delete failed");
          }
        },
      },
      cancel: { label: "Keep", onClick: () => {} },
    });
  }

  return (
    <div className="animate-fade-in pb-8">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4 flex items-center gap-3">
        <Link
          href="/dashboard/reports"
          aria-label="Back"
          className="p-2 -m-2 hover:bg-slate-100 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5 text-slate-700" />
        </Link>
        <h1 className="text-base font-bold text-slate-900 flex-1">
          Supplier Bills
        </h1>
        <button
          onClick={() => setShowForm((s) => !s)}
          className="inline-flex items-center gap-1 bg-brand-600 text-white text-sm font-semibold px-3 py-1.5 rounded-lg min-h-[36px]"
        >
          <Plus className="h-4 w-4" />
          {showForm ? "Cancel" : "Add bill"}
        </button>
      </header>

      {showForm && (
        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          <div className="card space-y-3">
            <input
              required
              value={form.supplier_name}
              onChange={(e) =>
                setForm({ ...form, supplier_name: e.target.value })
              }
              placeholder="Supplier name *"
              className="input w-full"
              maxLength={200}
            />
            <input
              value={form.supplier_gstin}
              onChange={(e) =>
                setForm({ ...form, supplier_gstin: e.target.value.toUpperCase() })
              }
              placeholder="Supplier GSTIN (optional)"
              className="input w-full font-mono"
              maxLength={15}
            />
            <div className="grid grid-cols-2 gap-2">
              <input
                required
                value={form.bill_number}
                onChange={(e) =>
                  setForm({ ...form, bill_number: e.target.value })
                }
                placeholder="Bill no. *"
                className="input"
                maxLength={50}
              />
              <input
                type="date"
                required
                value={form.bill_date}
                onChange={(e) =>
                  setForm({ ...form, bill_date: e.target.value })
                }
                className="input"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <input
                required
                type="number"
                step="0.01"
                inputMode="decimal"
                value={form.taxable}
                onChange={(e) => setForm({ ...form, taxable: e.target.value })}
                placeholder="Taxable ₹ *"
                className="input"
              />
              <input
                required
                type="number"
                step="0.01"
                inputMode="decimal"
                value={form.total}
                onChange={(e) => setForm({ ...form, total: e.target.value })}
                placeholder="Total ₹ *"
                className="input"
              />
            </div>
            <div className="grid grid-cols-3 gap-2">
              <input
                type="number"
                step="0.01"
                inputMode="decimal"
                value={form.cgst}
                onChange={(e) => setForm({ ...form, cgst: e.target.value })}
                placeholder="CGST"
                className="input"
              />
              <input
                type="number"
                step="0.01"
                inputMode="decimal"
                value={form.sgst}
                onChange={(e) => setForm({ ...form, sgst: e.target.value })}
                placeholder="SGST"
                className="input"
              />
              <input
                type="number"
                step="0.01"
                inputMode="decimal"
                value={form.igst}
                onChange={(e) => setForm({ ...form, igst: e.target.value })}
                placeholder="IGST"
                className="input"
              />
            </div>
            <input
              value={form.category}
              onChange={(e) => setForm({ ...form, category: e.target.value })}
              placeholder="Category (e.g. raw_materials, office, freight)"
              className="input w-full"
              maxLength={100}
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_capital_goods}
                onChange={(e) =>
                  setForm({ ...form, is_capital_goods: e.target.checked })
                }
              />
              Capital goods (machinery, equipment)
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={form.is_itc_eligible}
                onChange={(e) =>
                  setForm({ ...form, is_itc_eligible: e.target.checked })
                }
              />
              ITC eligible
            </label>
            <button
              type="submit"
              disabled={create.isPending}
              className="w-full bg-brand-600 hover:bg-brand-700 text-white font-bold py-3 rounded-xl disabled:opacity-50 min-h-[44px]"
            >
              {create.isPending ? "Saving…" : "Save bill"}
            </button>
          </div>
        </form>
      )}

      {/* List */}
      <div className="px-4 pt-3">
        {isLoading || !data ? (
          <div className="flex justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-slate-500" />
          </div>
        ) : data.items.length === 0 ? (
          <div className="text-center py-16">
            <Receipt className="h-12 w-12 mx-auto text-slate-300 mb-3" />
            <p className="text-slate-600 mb-4">
              No supplier bills yet
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-1.5 bg-brand-600 text-white px-4 py-2 rounded-lg font-semibold"
            >
              <Plus className="h-4 w-4" />
              Add first bill
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {data.items.map((p) => (
              <div
                key={p.id}
                className="bg-white border border-slate-200 rounded-xl p-3 flex items-start gap-3"
              >
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-slate-900 truncate">
                    {p.supplier_name}
                  </div>
                  <div className="text-xs text-slate-500 truncate">
                    Bill #{p.bill_number} ·{" "}
                    {new Date(p.bill_date).toLocaleDateString("en-IN", {
                      day: "2-digit",
                      month: "short",
                      year: "numeric",
                    })}
                  </div>
                  {p.supplier_gstin && (
                    <div className="text-[10px] font-mono text-slate-500">
                      {p.supplier_gstin}
                    </div>
                  )}
                </div>
                <div className="text-right">
                  <div className="font-bold text-slate-900">
                    ₹{fmt(p.total_paise)}
                  </div>
                  {p.is_itc_eligible && (
                    <div className="text-[10px] text-emerald-600">
                      ITC ₹
                      {fmt(
                        p.cgst_paise + p.sgst_paise + p.igst_paise + p.cess_paise,
                      )}
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleDelete(p.id, p.bill_number)}
                  aria-label="Delete"
                  className="p-2 -mr-1 hover:bg-red-50 rounded-lg text-red-500 flex-shrink-0"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))}
            <div className="text-xs text-slate-500 text-center pt-2">
              {data.total} total bills
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
