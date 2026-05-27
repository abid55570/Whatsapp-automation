"use client";

import {
  ArrowLeft,
  Clock,
  Loader2,
  MapPin,
  Plus,
  Save,
  Truck,
  X,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { TextArea } from "@/components/ui/TextArea";
import { Toggle } from "@/components/ui/Toggle";
import { apiErrorMessage } from "@/lib/api";
import {
  useFulfillmentConfig,
  useUpdateFulfillmentConfig,
} from "@/lib/queries";
import { cn } from "@/lib/utils";
import type {
  FulfillmentConfigUpdate,
  PickupPrepStrategy,
} from "@/types/api";

const DAYS = [
  { i: 0, label: "Mon" },
  { i: 1, label: "Tue" },
  { i: 2, label: "Wed" },
  { i: 3, label: "Thu" },
  { i: 4, label: "Fri" },
  { i: 5, label: "Sat" },
  { i: 6, label: "Sun" },
];

const STRATEGIES: { value: PickupPrepStrategy; label: string; hint: string }[] =
  [
    {
      value: "fixed",
      label: "Fixed",
      hint: "Same prep time for every order",
    },
    {
      value: "per_item",
      label: "Per item",
      hint: "Scales with item count",
    },
    {
      value: "auto",
      label: "Auto",
      hint: "Smart buckets based on size",
    },
    {
      value: "slots",
      label: "Time slots",
      hint: "Customer picks from your slots",
    },
  ];

export default function FulfillmentSettingsPage() {
  const router = useRouter();
  const { data: config, isLoading } = useFulfillmentConfig();
  const update = useUpdateFulfillmentConfig();

  const [form, setForm] = useState<FulfillmentConfigUpdate>({});
  const [slotInput, setSlotInput] = useState("");

  useEffect(() => {
    if (config && Object.keys(form).length === 0) {
      setForm({
        pickup_enabled: config.pickup_enabled,
        pickup_address: config.pickup_address ?? "",
        pickup_landmark: config.pickup_landmark ?? "",
        pickup_hours_start: config.pickup_hours_start,
        pickup_hours_end: config.pickup_hours_end,
        pickup_closed_days: config.pickup_closed_days,
        pickup_prep_strategy: config.pickup_prep_strategy,
        pickup_fixed_minutes: config.pickup_fixed_minutes,
        pickup_per_item_minutes: config.pickup_per_item_minutes,
        pickup_slots: config.pickup_slots,
        delivery_enabled: config.delivery_enabled,
        delivery_fee_paise: config.delivery_fee_paise,
        delivery_minimum_order_paise: config.delivery_minimum_order_paise,
        delivery_radius_km: config.delivery_radius_km,
        delivery_estimate_minutes: config.delivery_estimate_minutes,
      });
    }
  }, [config, form]);

  function set<K extends keyof FulfillmentConfigUpdate>(
    key: K,
    value: FulfillmentConfigUpdate[K],
  ) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function toggleDay(i: number) {
    const cur = form.pickup_closed_days ?? [];
    set(
      "pickup_closed_days",
      cur.includes(i) ? cur.filter((d) => d !== i) : [...cur, i],
    );
  }

  function addSlot() {
    if (!/^[0-2]\d:[0-5]\d$/.test(slotInput)) {
      toast.error("Use HH:MM format, e.g. 14:00");
      return;
    }
    const cur = form.pickup_slots ?? [];
    if (cur.includes(slotInput)) return;
    set("pickup_slots", [...cur, slotInput].sort());
    setSlotInput("");
  }

  function removeSlot(s: string) {
    set("pickup_slots", (form.pickup_slots ?? []).filter((x) => x !== s));
  }

  async function handleSave() {
    try {
      await update.mutateAsync(form);
      toast.success("Settings saved");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  if (isLoading || !config) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  const strategy = form.pickup_prep_strategy ?? "fixed";

  return (
    <div className="animate-fade-in pb-24">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <h1 className="text-xl font-bold text-slate-900">
            Fulfillment Settings
          </h1>
        </div>
      </header>

      <div className="p-4 space-y-5">
        {/* PICKUP */}
        <section className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-brand-600" />
              <h2 className="font-semibold text-slate-900">Pickup</h2>
            </div>
            <Toggle
              checked={Boolean(form.pickup_enabled)}
              onChange={(v) => set("pickup_enabled", v)}
            />
          </div>

          {form.pickup_enabled && (
            <div className="space-y-3 mt-3">
              <TextArea
                label="Shop address"
                placeholder="Shop #5, MG Road, Indiranagar, Bangalore"
                value={form.pickup_address ?? ""}
                onChange={(e) => set("pickup_address", e.target.value)}
                rows={2}
              />
              <Input
                label="Landmark (optional)"
                placeholder="Near Pizza Hut"
                value={form.pickup_landmark ?? ""}
                onChange={(e) => set("pickup_landmark", e.target.value)}
              />

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Open at"
                  type="time"
                  value={form.pickup_hours_start ?? ""}
                  onChange={(e) =>
                    set("pickup_hours_start", e.target.value)
                  }
                />
                <Input
                  label="Close at"
                  type="time"
                  value={form.pickup_hours_end ?? ""}
                  onChange={(e) => set("pickup_hours_end", e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Closed days
                </label>
                <div className="flex gap-1.5 flex-wrap">
                  {DAYS.map((d) => {
                    const closed = (form.pickup_closed_days ?? []).includes(d.i);
                    return (
                      <button
                        key={d.i}
                        type="button"
                        onClick={() => toggleDay(d.i)}
                        className={cn(
                          "px-2.5 py-1.5 rounded-full text-xs font-semibold transition active:scale-95",
                          closed
                            ? "bg-red-100 text-red-700 line-through"
                            : "bg-slate-100 text-slate-700 hover:bg-slate-200",
                        )}
                      >
                        {d.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  Prep time strategy
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {STRATEGIES.map((s) => {
                    const active = strategy === s.value;
                    return (
                      <button
                        key={s.value}
                        type="button"
                        onClick={() => set("pickup_prep_strategy", s.value)}
                        className={cn(
                          "p-3 rounded-xl text-left transition active:scale-[0.97] border-2",
                          active
                            ? "border-brand-500 bg-brand-50"
                            : "border-slate-200 bg-white hover:border-slate-300",
                        )}
                      >
                        <p
                          className={cn(
                            "font-semibold text-sm",
                            active ? "text-brand-700" : "text-slate-900",
                          )}
                        >
                          {s.label}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {s.hint}
                        </p>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Strategy-specific inputs */}
              {strategy === "fixed" && (
                <Input
                  label="Prep minutes"
                  type="number"
                  min={5}
                  max={480}
                  value={form.pickup_fixed_minutes ?? 30}
                  onChange={(e) =>
                    set("pickup_fixed_minutes", parseInt(e.target.value) || 30)
                  }
                  hint="Time to prep any order"
                />
              )}

              {strategy === "per_item" && (
                <Input
                  label="Minutes per item"
                  type="number"
                  min={1}
                  max={60}
                  value={form.pickup_per_item_minutes ?? 5}
                  onChange={(e) =>
                    set(
                      "pickup_per_item_minutes",
                      parseInt(e.target.value) || 5,
                    )
                  }
                  hint="Total = items × minutes"
                />
              )}

              {strategy === "slots" && (
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5">
                    Pickup time slots
                  </label>
                  <div className="flex flex-wrap gap-1.5 mb-2">
                    {(form.pickup_slots ?? []).map((s) => (
                      <span
                        key={s}
                        className="inline-flex items-center gap-1 bg-brand-100 text-brand-700 px-2 py-1 rounded-full text-xs font-mono"
                      >
                        {s}
                        <button
                          type="button"
                          onClick={() => removeSlot(s)}
                          className="hover:bg-brand-200 rounded-full p-0.5"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="time"
                      value={slotInput}
                      onChange={(e) => setSlotInput(e.target.value)}
                      className="flex-1 px-3 py-2 rounded-lg border border-slate-200 text-sm"
                    />
                    <Button
                      type="button"
                      onClick={addSlot}
                      variant="secondary"
                      size="sm"
                    >
                      <Plus className="h-4 w-4" />
                      Add
                    </Button>
                  </div>
                </div>
              )}

              {strategy === "auto" && (
                <div className="bg-slate-50 rounded-xl p-3 text-xs text-slate-600 space-y-1">
                  <p className="font-semibold text-slate-700">Auto buckets:</p>
                  <p>• 1-3 items → 15 min</p>
                  <p>• 4-10 items → 30 min</p>
                  <p>• 11-20 items → 60 min</p>
                  <p>• 21+ items → 90 min</p>
                </div>
              )}
            </div>
          )}
        </section>

        {/* DELIVERY */}
        <section className="card">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-orange-600" />
              <h2 className="font-semibold text-slate-900">Delivery</h2>
            </div>
            <Toggle
              checked={Boolean(form.delivery_enabled)}
              onChange={(v) => set("delivery_enabled", v)}
            />
          </div>

          {form.delivery_enabled && (
            <div className="space-y-3 mt-3">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Delivery fee (₹)"
                  type="number"
                  min={0}
                  value={(form.delivery_fee_paise ?? 0) / 100}
                  onChange={(e) =>
                    set(
                      "delivery_fee_paise",
                      Math.round((parseFloat(e.target.value) || 0) * 100),
                    )
                  }
                />
                <Input
                  label="Min order (₹)"
                  type="number"
                  min={0}
                  value={(form.delivery_minimum_order_paise ?? 0) / 100}
                  onChange={(e) =>
                    set(
                      "delivery_minimum_order_paise",
                      Math.round((parseFloat(e.target.value) || 0) * 100),
                    )
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Radius (km)"
                  type="number"
                  min={1}
                  max={50}
                  value={form.delivery_radius_km ?? 3}
                  onChange={(e) =>
                    set("delivery_radius_km", parseInt(e.target.value) || 3)
                  }
                />
                <Input
                  label="Estimate (min)"
                  type="number"
                  min={10}
                  max={480}
                  value={form.delivery_estimate_minutes ?? 45}
                  onChange={(e) =>
                    set(
                      "delivery_estimate_minutes",
                      parseInt(e.target.value) || 45,
                    )
                  }
                />
              </div>
            </div>
          )}
        </section>
      </div>

      {/* Sticky save */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 p-4">
        <div className="max-w-md mx-auto">
          <Button
            onClick={handleSave}
            loading={update.isPending}
            fullWidth
            size="lg"
          >
            <Save className="h-5 w-5" />
            Save Settings
          </Button>
        </div>
      </div>
    </div>
  );
}
