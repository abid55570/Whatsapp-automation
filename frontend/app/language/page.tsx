"use client";

import { ArrowRight, Check } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import AuroraBackground from "@/components/ui/aurora-background";
import { Component as MagicCursor } from "@/components/ui/magic-cursor";
import { MouseFollowingEyes } from "@/components/ui/mouse-following-eyes";
import { LOCALE_META, LOCALES, type Locale } from "@/i18n/config";
import { apiErrorMessage, api } from "@/lib/api";
import { setLocaleCookie } from "@/lib/locale";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

const SERIF = "'Instrument Serif', serif";

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
        } catch {
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
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-white p-4">
      {/* Flowing green aurora + sparkle cursor */}
      <AuroraBackground />
      <MagicCursor colors={["252 254 255", "37 211 102", "52 217 124"]} />

      {/* Home / logo top-left */}
      <Link
        href="/"
        aria-label="Back to home"
        className="group absolute left-5 top-5 z-20 flex items-center gap-2.5"
      >
        <span
          className="inline-block h-8 w-8 rounded-full transition-transform duration-300 group-hover:rotate-12"
          style={{ background: "linear-gradient(135deg,#25d366,#128c7e)" }}
        />
        <span
          className="text-2xl leading-none tracking-tight text-slate-900"
          style={{ fontFamily: SERIF }}
        >
          Whatly
        </span>
      </Link>

      {/* Glass card */}
      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md rounded-3xl border border-white/50 bg-white/55 p-6 shadow-[0_30px_90px_-28px_rgba(16,140,126,0.4)] backdrop-blur-2xl sm:p-8"
      >
        <div className="mb-7 text-center">
          <div className="mb-5 flex justify-center">
            <MouseFollowingEyes size={48} />
          </div>
          <h1 className="text-3xl italic text-slate-900" style={{ fontFamily: SERIF }}>
            {t("title")}
          </h1>
          <p className="mt-1 text-sm text-slate-500">{t("subtitle")}</p>
        </div>

        <div className="mb-6 space-y-2.5">
          {LOCALES.map((code, i) => {
            const meta = LOCALE_META[code];
            const active = selected === code;
            return (
              <motion.button
                key={code}
                type="button"
                onClick={() => setSelected(code)}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.18 + i * 0.05, duration: 0.4 }}
                className={cn(
                  "flex w-full items-center gap-3 rounded-2xl border-2 p-3.5 text-left transition-all duration-300 active:scale-[0.99]",
                  active
                    ? "border-[#25d366] bg-[#25d366]/10 shadow-[0_12px_34px_-12px_rgba(37,211,102,0.65)]"
                    : "border-transparent bg-white/80 hover:-translate-y-0.5 hover:border-[#25d366]/40 hover:bg-white",
                )}
              >
                <span className="flex h-9 w-9 flex-none items-center justify-center rounded-xl bg-white text-lg shadow-sm ring-1 ring-slate-200/70">
                  {meta.emoji}
                </span>
                <span
                  className={cn(
                    "flex-1 font-semibold",
                    active ? "text-[#1faa59]" : "text-slate-900",
                  )}
                >
                  {meta.native}
                </span>
                {active && (
                  <span
                    className="flex h-6 w-6 items-center justify-center rounded-full"
                    style={{ background: "linear-gradient(135deg,#25d366,#128c7e)" }}
                  >
                    <Check className="h-3.5 w-3.5 text-white" strokeWidth={3} />
                  </span>
                )}
              </motion.button>
            );
          })}
        </div>

        <Button onClick={handleContinue} loading={pending} fullWidth size="lg">
          {t("continue")}
          <ArrowRight className="h-5 w-5" />
        </Button>
      </motion.div>
    </main>
  );
}
