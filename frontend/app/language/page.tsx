"use client";

import { ArrowRight, Check } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { LOCALE_META, LOCALES, type Locale } from "@/i18n/config";
import { apiErrorMessage, api } from "@/lib/api";
import { setLocaleCookie } from "@/lib/locale";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

export default function LanguagePickerPage() {
  const router = useRouter();
  const params = useSearchParams();
  const next = params.get("next") ?? "/signup";
  const t = useTranslations("lang_picker");

  const [selected, setSelected] = useState<Locale>("en");
  const [pending, setPending] = useState(false);

  const isAuthed = useAuthStore((s) => s.isAuthenticated());

  async function handleContinue() {
    setPending(true);
    try {
      // Set cookie so SSR picks it up on next request
      await setLocaleCookie(selected);
      // If logged in, persist to backend
      if (isAuthed) {
        try {
          await api.patch("/api/v1/auth/me", {
            preferred_language: selected,
          });
        } catch (err) {
          // non-fatal — locale cookie still set
        }
      }
      router.replace(next);
      // Force full reload so layout re-reads cookie
      window.location.href = next;
    } catch (err) {
      toast.error(apiErrorMessage(err));
      setPending(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-accent-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-sm animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-brand-500 text-white text-3xl items-center justify-center mb-4 shadow-soft">
            💬
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{t("title")}</h1>
          <p className="text-sm text-slate-500 mt-1">{t("subtitle")}</p>
        </div>

        <div className="space-y-2 mb-6">
          {LOCALES.map((code) => {
            const meta = LOCALE_META[code];
            const active = selected === code;
            return (
              <button
                key={code}
                type="button"
                onClick={() => setSelected(code)}
                className={cn(
                  "w-full flex items-center gap-3 p-3.5 rounded-xl border-2 transition active:scale-[0.99]",
                  active
                    ? "border-brand-500 bg-brand-50 ring-2 ring-brand-500/20"
                    : "border-slate-200 bg-white hover:border-slate-300",
                )}
              >
                <span className="text-2xl">{meta.emoji}</span>
                <span
                  className={cn(
                    "flex-1 text-left font-semibold",
                    active ? "text-brand-700" : "text-slate-900",
                  )}
                >
                  {meta.native}
                </span>
                {active && (
                  <div className="w-6 h-6 bg-brand-500 rounded-full flex items-center justify-center">
                    <Check className="h-3.5 w-3.5 text-white" strokeWidth={3} />
                  </div>
                )}
              </button>
            );
          })}
        </div>

        <Button
          onClick={handleContinue}
          loading={pending}
          fullWidth
          size="lg"
        >
          {t("continue")}
          <ArrowRight className="h-5 w-5" />
        </Button>
      </div>
    </main>
  );
}
