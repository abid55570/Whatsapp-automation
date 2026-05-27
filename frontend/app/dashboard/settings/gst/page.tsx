"use client";

import { ArrowLeft, Loader2, Save } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { useGstSettings, useUpdateGstSettings } from "@/lib/queries";
import type { GstScheme } from "@/types/api";

const SCHEMES: { v: GstScheme; label: string; hint: string }[] = [
  {
    v: "unregistered",
    label: "Unregistered",
    hint: "Turnover under ₹20L · no GSTIN",
  },
  {
    v: "regular",
    label: "Regular",
    hint: "Standard GST · collects CGST/SGST/IGST",
  },
  {
    v: "composition",
    label: "Composition",
    hint: "Flat 1/5/6% · Bill of Supply format",
  },
];

export default function GstSettingsPage() {
  const { data: settings, isLoading } = useGstSettings();
  const update = useUpdateGstSettings();

  const [scheme, setScheme] = useState<GstScheme>("unregistered");
  const [gstin, setGstin] = useState("");
  const [legalName, setLegalName] = useState("");
  const [pan, setPan] = useState("");
  const [addr1, setAddr1] = useState("");
  const [addr2, setAddr2] = useState("");
  const [city, setCity] = useState("");
  const [state, setState] = useState("");
  const [pincode, setPincode] = useState("");
  const [prefix, setPrefix] = useState("INV");
  const [compositionRate, setCompositionRate] = useState<number | "">("");

  useEffect(() => {
    if (settings) {
      setScheme(settings.gst_scheme);
      setGstin(settings.gstin || "");
      setLegalName(settings.legal_name || "");
      setPan(settings.pan || "");
      setAddr1(settings.business_address_line1 || "");
      setAddr2(settings.business_address_line2 || "");
      setCity(settings.business_city || "");
      setState(settings.business_state || "");
      setPincode(settings.business_pincode || "");
      setPrefix(settings.invoice_prefix);
      setCompositionRate(settings.gst_composition_rate || "");
    }
  }, [settings]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    try {
      await update.mutateAsync({
        gst_scheme: scheme,
        gstin: gstin.trim() || null,
        legal_name: legalName.trim() || null,
        pan: pan.trim().toUpperCase() || null,
        business_address_line1: addr1.trim() || null,
        business_address_line2: addr2.trim() || null,
        business_city: city.trim() || null,
        business_state: state.trim() || null,
        business_pincode: pincode.trim() || null,
        invoice_prefix: prefix.trim().toUpperCase() || "INV",
        gst_composition_rate:
          scheme === "composition" && compositionRate
            ? Number(compositionRate)
            : null,
      });
      toast.success("GST settings saved");
    } catch (e) {
      toast.error("Save failed: " + (e as Error).message);
    }
  }

  if (isLoading || !settings) {
    return (
      <div className="flex justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
      </div>
    );
  }

  return (
    <form onSubmit={handleSave} className="animate-fade-in pb-24">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4 flex items-center gap-3">
        <Link
          href="/dashboard/settings"
          aria-label="Back"
          className="p-2 -m-2 hover:bg-slate-100 rounded-lg"
        >
          <ArrowLeft className="h-5 w-5 text-slate-700" />
        </Link>
        <h1 className="text-base font-bold text-slate-900">GST Settings</h1>
      </header>

      <div className="p-4 space-y-4">
        <section className="card space-y-3">
          <div className="text-xs uppercase text-slate-500 font-semibold">
            GST scheme
          </div>
          <div className="space-y-2">
            {SCHEMES.map((s) => (
              <label
                key={s.v}
                className="flex items-start gap-3 p-2 rounded-lg cursor-pointer hover:bg-slate-50"
              >
                <input
                  type="radio"
                  name="scheme"
                  value={s.v}
                  checked={scheme === s.v}
                  onChange={() => setScheme(s.v)}
                  className="mt-1"
                />
                <div className="flex-1">
                  <div className="font-semibold text-slate-900">{s.label}</div>
                  <div className="text-xs text-slate-500">{s.hint}</div>
                </div>
              </label>
            ))}
          </div>

          {scheme === "composition" && (
            <select
              value={compositionRate}
              onChange={(e) =>
                setCompositionRate(
                  e.target.value ? parseInt(e.target.value) : "",
                )
              }
              className="input w-full"
            >
              <option value="">Pick composition rate</option>
              <option value={1}>1% — Traders</option>
              <option value={5}>5% — Restaurants</option>
              <option value={6}>6% — Services</option>
            </select>
          )}
        </section>

        {scheme !== "unregistered" && (
          <>
            <section className="card space-y-3">
              <div className="text-xs uppercase text-slate-500 font-semibold">
                GST identifiers
              </div>
              <input
                value={gstin}
                onChange={(e) => setGstin(e.target.value.toUpperCase())}
                placeholder="GSTIN (15 chars)"
                className="input w-full font-mono"
                maxLength={15}
                required
              />
              <input
                value={pan}
                onChange={(e) => setPan(e.target.value.toUpperCase())}
                placeholder="PAN (10 chars)"
                className="input w-full font-mono"
                maxLength={10}
              />
              <input
                value={legalName}
                onChange={(e) => setLegalName(e.target.value)}
                placeholder="Legal name (if different from display)"
                className="input w-full"
                maxLength={200}
              />
            </section>

            <section className="card space-y-3">
              <div className="text-xs uppercase text-slate-500 font-semibold">
                Business address
              </div>
              <input
                value={addr1}
                onChange={(e) => setAddr1(e.target.value)}
                placeholder="Address line 1"
                className="input w-full"
              />
              <input
                value={addr2}
                onChange={(e) => setAddr2(e.target.value)}
                placeholder="Address line 2 (optional)"
                className="input w-full"
              />
              <div className="grid grid-cols-2 gap-2">
                <input
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  placeholder="City"
                  className="input"
                />
                <input
                  value={pincode}
                  onChange={(e) => setPincode(e.target.value)}
                  placeholder="Pincode"
                  className="input"
                  maxLength={6}
                  inputMode="numeric"
                />
              </div>
              <input
                value={state}
                onChange={(e) => setState(e.target.value)}
                placeholder="State"
                className="input w-full"
              />
            </section>
          </>
        )}

        <section className="card space-y-3">
          <div className="text-xs uppercase text-slate-500 font-semibold">
            Invoice numbering
          </div>
          <input
            value={prefix}
            onChange={(e) => setPrefix(e.target.value.toUpperCase())}
            placeholder="Prefix (e.g. INV, SHM)"
            className="input w-full"
            maxLength={6}
          />
          <div className="text-xs text-slate-500">
            Sample: {prefix || "INV"}-{(settings.current_invoice_fy || "26-27").slice(0, 2)}
            -{String((settings.invoice_seq || 0) + 1).padStart(4, "0")}
          </div>
        </section>
      </div>

      <div className="fixed bottom-[calc(64px+env(safe-area-inset-bottom))] left-0 right-0 bg-white border-t border-slate-200 p-3 z-20 max-w-md mx-auto">
        <button
          type="submit"
          disabled={update.isPending}
          className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-bold py-3.5 rounded-xl transition active:scale-95 disabled:opacity-50 min-h-[48px]"
        >
          {update.isPending ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Save className="h-5 w-5" />
          )}
          Save settings
        </button>
      </div>
    </form>
  );
}
