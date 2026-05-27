"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";
import type { BusinessType } from "@/types/api";

export const BUSINESS_TYPES: { value: BusinessType; emoji: string; label: string }[] = [
  { value: "restaurant", emoji: "🍕", label: "Restaurant" },
  { value: "salon", emoji: "💇", label: "Salon" },
  { value: "clinic", emoji: "🏥", label: "Clinic" },
  { value: "shop", emoji: "🛒", label: "Shop" },
  { value: "gym", emoji: "💪", label: "Gym" },
  { value: "coaching", emoji: "📚", label: "Coaching" },
  { value: "agency", emoji: "💼", label: "Agency" },
  { value: "d2c", emoji: "📦", label: "D2C Brand" },
  { value: "home_business", emoji: "🏠", label: "Home Business" },
  { value: "custom", emoji: "✨", label: "Other" },
];

interface Props {
  selected: BusinessType | null;
  onChange: (type: BusinessType) => void;
}

export function BusinessTypeGrid({ selected, onChange }: Props) {
  return (
    <div className="grid grid-cols-3 gap-2.5">
      {BUSINESS_TYPES.map((t) => {
        const active = selected === t.value;
        return (
          <button
            key={t.value}
            type="button"
            onClick={() => onChange(t.value)}
            className={cn(
              "relative flex flex-col items-center justify-center gap-1.5 rounded-xl p-3 transition active:scale-[0.97]",
              "border-2",
              active
                ? "border-brand-500 bg-brand-50 ring-2 ring-brand-500/20"
                : "border-slate-200 bg-white hover:border-slate-300",
            )}
          >
            <span className="text-3xl">{t.emoji}</span>
            <span
              className={cn(
                "text-xs font-medium text-center",
                active ? "text-brand-700" : "text-slate-700",
              )}
            >
              {t.label}
            </span>
            {active && (
              <div className="absolute top-1 right-1 w-5 h-5 bg-brand-500 rounded-full flex items-center justify-center">
                <Check className="h-3 w-3 text-white" strokeWidth={3} />
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}
