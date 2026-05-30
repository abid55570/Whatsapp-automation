"use client";

import {
  AlertCircle,
  CheckCircle2,
  Clock,
  Frown,
  Moon,
  Smile,
  Sparkles,
  TrendingDown,
  TrendingUp,
  X,
  Zap,
} from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { cn } from "@/lib/utils";

// ============================================================
// "Without Whatly vs With Whatly" — pain→gain hook reel.
// STRUCTURE (emoji / colors / stat icons + values) lives here; all
// visible TEXT comes from the "hook" message namespace → follows locale.
// ============================================================

type IconT = React.ComponentType<{ className?: string }>;

interface VariantMeta {
  emoji: string;
  badgeColor: string;
  statIcons: IconT[];   // 3 icons
  statValues: string[]; // 3 values (numeric-ish, locale-neutral)
}

const RED = "bg-red-100 text-red-700 border-red-200";
const GREEN = "bg-emerald-100 text-emerald-700 border-emerald-200";

const HOOK_SCENES: Record<string, { without: VariantMeta; with: VariantMeta }> = {
  kirana: {
    without: { emoji: "😩", badgeColor: RED, statIcons: [TrendingDown, Frown, Clock], statValues: ["₹4,800", "8", "0"] },
    with: { emoji: "😎", badgeColor: GREEN, statIcons: [TrendingUp, Smile, Zap], statValues: ["₹4,800", "8/8", "<1 sec"] },
  },
  salon: {
    without: { emoji: "💇‍♀️", badgeColor: RED, statIcons: [TrendingDown, Frown, Clock], statValues: ["₹12,000", "8", "0"] },
    with: { emoji: "✨", badgeColor: GREEN, statIcons: [TrendingUp, CheckCircle2, Sparkles], statValues: ["₹12,000", "8/8", "0"] },
  },
  restaurant: {
    without: { emoji: "🍕", badgeColor: RED, statIcons: [TrendingDown, Frown, Clock], statValues: ["25%", "12", "60 min"] },
    with: { emoji: "🔥", badgeColor: GREEN, statIcons: [TrendingUp, CheckCircle2, Zap], statValues: ["0%", "12/12", "<2 sec"] },
  },
};

const SCENE_KEYS = Object.keys(HOOK_SCENES);

interface VariantText {
  badge: string;
  headline: string;
  subhead: string;
  chats: string[];
  stat_labels: string[];
}

// ============================================================
// Component
// ============================================================

export function HookReel() {
  const t = useTranslations("hook");
  const [sceneKey, setSceneKey] = useState<string>(SCENE_KEYS[0]);
  const [variant, setVariant] = useState<"without" | "with">("without");

  // Toggle without ↔ with every 3.5s, advance scene every 7s
  useEffect(() => {
    const flipTimer = setInterval(() => {
      setVariant((v) => (v === "without" ? "with" : "without"));
    }, 3500);
    return () => clearInterval(flipTimer);
  }, []);

  useEffect(() => {
    const sceneTimer = setInterval(() => {
      setSceneKey((cur) => {
        const i = SCENE_KEYS.indexOf(cur);
        return SCENE_KEYS[(i + 1) % SCENE_KEYS.length];
      });
      setVariant("without");
    }, 7000);
    return () => clearInterval(sceneTimer);
  }, []);

  const meta = HOOK_SCENES[sceneKey][variant];
  const txt = t.raw(`${sceneKey}.${variant}`) as VariantText;
  const isWith = variant === "with";

  return (
    <section className="bg-gradient-to-b from-white to-slate-50 px-4 py-10 sm:py-16">
      <div className="max-w-4xl mx-auto">
        {/* Section heading */}
        <div className="text-center mb-6 sm:mb-10">
          <div className="inline-flex items-center gap-1.5 bg-red-100 text-red-700 text-xs font-semibold px-3 py-1 rounded-full mb-3">
            <AlertCircle className="h-3 w-3" />
            {t("badge")}
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-slate-900 mb-2 inline-flex items-center gap-2 flex-wrap justify-center">
            <span>{t("title_a")}</span>
            <Moon className="inline h-6 w-6 sm:h-8 sm:w-8 text-slate-700" />
          </h2>
          <p className="text-slate-600 text-sm sm:text-base">{t("subtitle")}</p>
        </div>

        {/* Scene toggles */}
        <div className="flex gap-1.5 mb-4 justify-center overflow-x-auto px-1 pb-2 no-scrollbar">
          {SCENE_KEYS.map((k) => (
            <button
              key={k}
              onClick={() => {
                setSceneKey(k);
                setVariant("without");
              }}
              className={cn(
                "flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition min-h-[32px]",
                k === sceneKey
                  ? "bg-slate-900 text-white shadow"
                  : "bg-white border border-slate-200 text-slate-600 active:scale-95",
              )}
            >
              {t(`${k}.name`)}
            </button>
          ))}
        </div>

        {/* Hook card */}
        <div
          className={cn(
            "relative rounded-3xl border-2 p-4 sm:p-6 shadow-soft-lg transition-all duration-500",
            isWith
              ? "bg-gradient-to-br from-emerald-50 to-brand-50 border-emerald-300"
              : "bg-gradient-to-br from-red-50 to-orange-50 border-red-200",
          )}
          key={`${sceneKey}-${variant}`}
        >
          {/* Variant badge */}
          <div className="flex items-center justify-between gap-2 mb-4">
            <span
              className={cn(
                "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border",
                meta.badgeColor,
              )}
            >
              <span className="text-base leading-none">{meta.emoji}</span>
              {isWith ? t("with_label") : t("without_label")}
            </span>
            <span className={cn("text-[10px] font-mono px-2 py-0.5 rounded border", meta.badgeColor)}>
              {txt.badge}
            </span>
          </div>

          {/* Headline */}
          <h3
            className={cn(
              "text-xl sm:text-3xl font-extrabold leading-tight mb-2 animate-fade-in",
              isWith ? "text-emerald-900" : "text-red-900",
            )}
          >
            {txt.headline}
          </h3>
          <p
            className={cn(
              "text-sm sm:text-base mb-5 animate-fade-in",
              isWith ? "text-emerald-700" : "text-red-700",
            )}
          >
            {txt.subhead}
          </p>

          {/* Chat preview */}
          <div className="bg-white/80 backdrop-blur rounded-2xl p-3 sm:p-4 mb-4 space-y-2 max-h-72 overflow-hidden">
            {txt.chats.map((msg, i) => (
              <div
                key={`${sceneKey}-${variant}-${i}`}
                className="flex items-start gap-2 animate-bubble-in"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <div className="flex-1 min-w-0">
                  <div className="bg-[#DCF8C6] rounded-lg px-3 py-1.5 text-sm text-slate-800 inline-block max-w-full">
                    {msg}
                  </div>
                </div>
                {isWith ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                ) : (
                  <X className="h-5 w-5 text-red-400 flex-shrink-0 mt-0.5" />
                )}
              </div>
            ))}
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-2 sm:gap-3">
            {meta.statValues.map((value, i) => {
              const Icon = meta.statIcons[i];
              return (
                <div
                  key={i}
                  className={cn(
                    "rounded-xl p-2.5 sm:p-3 text-center animate-fade-in bg-white/70 border",
                    isWith ? "border-emerald-100" : "border-red-100",
                  )}
                  style={{ animationDelay: `${(i + 4) * 80}ms` }}
                >
                  <Icon
                    className={cn(
                      "h-4 w-4 sm:h-5 sm:w-5 mx-auto mb-1",
                      isWith ? "text-emerald-500" : "text-red-500",
                    )}
                  />
                  <div
                    className={cn(
                      "font-extrabold text-base sm:text-xl tabular-nums",
                      isWith ? "text-emerald-900" : "text-red-900",
                    )}
                  >
                    {value}
                  </div>
                  <div className="text-[10px] sm:text-xs text-slate-600 mt-0.5">
                    {txt.stat_labels[i]}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Toggle hint */}
          <div className="flex items-center justify-center gap-3 mt-5 text-xs text-slate-600">
            <button
              onClick={() => setVariant("without")}
              className={cn(
                "px-3 py-1.5 rounded-full font-semibold transition",
                !isWith ? "bg-red-600 text-white" : "bg-white border border-slate-200",
              )}
            >
              {t("toggle_without")}
            </button>
            <div className="flex gap-1">
              <span className={cn("w-2 h-2 rounded-full", !isWith ? "bg-red-500" : "bg-slate-300")} />
              <span className={cn("w-2 h-2 rounded-full", isWith ? "bg-emerald-500" : "bg-slate-300")} />
            </div>
            <button
              onClick={() => setVariant("with")}
              className={cn(
                "px-3 py-1.5 rounded-full font-semibold transition",
                isWith ? "bg-emerald-600 text-white" : "bg-white border border-slate-200",
              )}
            >
              {t("toggle_with")}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
