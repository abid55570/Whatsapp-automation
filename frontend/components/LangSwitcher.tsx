"use client";

import { Check, Globe } from "lucide-react";
import { useLocale } from "next-intl";
import { useState } from "react";

import { LOCALE_META, LOCALES, type Locale } from "@/i18n/config";
import { api } from "@/lib/api";
import { setLocaleCookie } from "@/lib/locale";
import { cn } from "@/lib/utils";

interface Props {
  variant?: "compact" | "full";
}

export function LangSwitcher({ variant = "full" }: Props) {
  const currentLocale = useLocale() as Locale;
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState<Locale | null>(null);

  async function selectLocale(code: Locale) {
    if (code === currentLocale) {
      setOpen(false);
      return;
    }
    setPending(code);
    try {
      await setLocaleCookie(code);
      try {
        await api.patch("/api/v1/auth/me", { preferred_language: code });
      } catch {
        // non-fatal
      }
      window.location.reload();
    } catch {
      setPending(null);
    }
  }

  const currentMeta = LOCALE_META[currentLocale];

  if (variant === "compact") {
    return (
      <div className="relative">
        <button
          onClick={() => setOpen(!open)}
          className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 active:scale-95 transition"
        >
          <Globe className="h-3.5 w-3.5" />
          <span>{currentMeta.native}</span>
        </button>
        {open && (
          <>
            <div
              className="fixed inset-0 z-30"
              onClick={() => setOpen(false)}
            />
            <div className="absolute right-0 mt-1 w-44 bg-white rounded-xl shadow-soft-lg border border-slate-200 overflow-hidden z-40">
              {LOCALES.map((code) => {
                const meta = LOCALE_META[code];
                const active = code === currentLocale;
                const loading = pending === code;
                return (
                  <button
                    key={code}
                    onClick={() => selectLocale(code)}
                    disabled={loading}
                    className={cn(
                      "w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-slate-50 active:bg-slate-100 transition disabled:opacity-50",
                      active && "bg-brand-50 text-brand-700",
                    )}
                  >
                    <span>{meta.emoji}</span>
                    <span className="flex-1 text-left">{meta.native}</span>
                    {active && <Check className="h-3.5 w-3.5" />}
                  </button>
                );
              })}
            </div>
          </>
        )}
      </div>
    );
  }

  // Full variant — for settings page
  return (
    <div className="space-y-2">
      {LOCALES.map((code) => {
        const meta = LOCALE_META[code];
        const active = code === currentLocale;
        const loading = pending === code;
        return (
          <button
            key={code}
            onClick={() => selectLocale(code)}
            disabled={loading}
            className={cn(
              "w-full flex items-center gap-3 p-3 rounded-xl border-2 transition active:scale-[0.99] disabled:opacity-50",
              active
                ? "border-brand-500 bg-brand-50"
                : "border-slate-200 bg-white hover:border-slate-300",
            )}
          >
            <span className="text-xl">{meta.emoji}</span>
            <span className="flex-1 text-left font-medium text-slate-900">
              {meta.native}
            </span>
            {active && (
              <Check
                className="h-4 w-4 text-brand-600"
                strokeWidth={3}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}
