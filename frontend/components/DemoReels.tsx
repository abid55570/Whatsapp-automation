"use client";

import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { useTranslations } from "next-intl";
import { useCallback, useEffect, useRef, useState } from "react";

import { cn } from "@/lib/utils";

// ============================================================
// Demo scenarios — chat reels.
// STRUCTURE (emoji / colors / order) lives here; all visible TEXT
// comes from the "reels" message namespace so it follows the locale.
// ============================================================

interface ScenarioMeta {
  id: string;
  emoji: string;
  accent: string; // tailwind text-* class (the "Auto-reply" tag color)
  pill: string;   // tailwind bg-* class for the badge chip
}

const SCENARIOS: ScenarioMeta[] = [
  { id: "kirana", emoji: "🛒", accent: "text-emerald-600", pill: "bg-emerald-100 text-emerald-700" },
  { id: "restaurant", emoji: "🍕", accent: "text-orange-600", pill: "bg-orange-100 text-orange-700" },
  { id: "salon", emoji: "💇", accent: "text-pink-600", pill: "bg-pink-100 text-pink-700" },
  { id: "gym", emoji: "💪", accent: "text-blue-600", pill: "bg-blue-100 text-blue-700" },
  { id: "coaching", emoji: "📚", accent: "text-violet-600", pill: "bg-violet-100 text-violet-700" },
  { id: "clinic", emoji: "🩺", accent: "text-teal-600", pill: "bg-teal-100 text-teal-700" },
];

// Every scenario has the same 6-bubble rhythm: customer → bot → … The two
// middle bot replies carry the "Auto-reply" tag; the last one doesn't.
const BUBBLE_FROM = ["cx", "bot", "cx", "bot", "cx", "bot"] as const;
const BUBBLE_TAGGED = [false, true, false, true, false, false];

const ROTATE_MS = 6000;
const TYPING_MS = 600;

// ============================================================
// Component
// ============================================================

export function DemoReels() {
  const t = useTranslations("reels");
  const tLanding = useTranslations("landing");
  const [idx, setIdx] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [visibleCount, setVisibleCount] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const touchStartX = useRef<number | null>(null);

  const meta = SCENARIOS[idx];
  // raw() returns the structured object (business/tag/badge/lines[]).
  const scn = t.raw(meta.id) as {
    business: string;
    tag: string;
    badge: string;
    lines: string[];
  };
  const total = scn.lines.length;

  // Reveal bubbles one by one when the scenario (idx) changes.
  useEffect(() => {
    setVisibleCount(0);
    let i = 0;
    const tick = () => {
      i += 1;
      setVisibleCount(i);
      if (i < total) {
        const delay = BUBBLE_FROM[i] === "bot" ? TYPING_MS : 350;
        setTimeout(tick, delay);
      }
    };
    setVisibleCount(1);
    if (total > 1) setTimeout(tick, 450);
    // Depend on idx only — BUBBLE_FROM/total are stable, and text swapping
    // on a locale change should not restart the animation.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idx]);

  // Auto-advance
  useEffect(() => {
    if (!playing) return;
    intervalRef.current = setInterval(() => {
      setIdx((cur) => (cur + 1) % SCENARIOS.length);
    }, ROTATE_MS);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [playing]);

  const next = useCallback(
    () => setIdx((cur) => (cur + 1) % SCENARIOS.length),
    [],
  );
  const prev = useCallback(
    () => setIdx((cur) => (cur - 1 + SCENARIOS.length) % SCENARIOS.length),
    [],
  );

  // Touch / swipe handling
  function handleTouchStart(e: React.TouchEvent) {
    touchStartX.current = e.touches[0].clientX;
  }
  function handleTouchEnd(e: React.TouchEvent) {
    if (touchStartX.current === null) return;
    const dx = e.changedTouches[0].clientX - touchStartX.current;
    if (Math.abs(dx) > 50) {
      dx < 0 ? next() : prev();
      setPlaying(false); // pause autoplay once user interacts
    }
    touchStartX.current = null;
  }

  // Keyboard navigation
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "ArrowRight") next();
      else if (e.key === "ArrowLeft") prev();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [next, prev]);

  return (
    <div className="w-full max-w-md mx-auto" ref={containerRef}>
      {/* Industry pills (tap to jump) */}
      <div className="flex gap-1.5 mb-3 overflow-x-auto px-1 pb-2 no-scrollbar">
        {SCENARIOS.map((s, i) => (
          <button
            key={s.id}
            onClick={() => {
              setIdx(i);
              setPlaying(false);
            }}
            className={cn(
              "flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition min-h-[32px]",
              i === idx
                ? "bg-slate-900 text-white shadow"
                : "bg-white border border-slate-200 text-slate-600 active:scale-95",
            )}
          >
            {s.emoji} {t(`${s.id}.tag`).split(" / ")[0]}
          </button>
        ))}
      </div>

      {/* Chat card */}
      <div
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
        className="relative bg-[#075E54] rounded-2xl shadow-soft-lg overflow-hidden touch-pan-y"
      >
        {/* Header */}
        <div className="px-3 sm:px-4 py-3 flex items-center gap-3 bg-[#075E54]">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-lg shadow-sm flex-shrink-0">
            {meta.emoji}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-sm text-white truncate">
              {scn.business}
            </div>
            <div className="text-[10px] text-green-200 truncate">
              ● {t("online")} · {scn.tag}
            </div>
          </div>
          <span
            className={cn(
              "text-[10px] font-semibold px-2 py-0.5 rounded-full whitespace-nowrap",
              meta.pill,
            )}
          >
            {scn.badge}
          </span>
        </div>

        {/* Chat body */}
        <div className="bg-[#ECE5DD] p-2.5 sm:p-3 space-y-2 min-h-[340px] sm:min-h-[360px]">
          {scn.lines.slice(0, visibleCount).map((text, i) => {
            const from = BUBBLE_FROM[i];
            return (
              <div
                key={`${meta.id}-${i}`}
                className={cn(
                  "flex animate-bubble-in",
                  from === "cx" ? "justify-end" : "justify-start",
                )}
              >
                <div
                  className={cn(
                    "rounded-lg px-3 py-1.5 text-sm text-slate-800 max-w-[78%] sm:max-w-[75%] whitespace-pre-line shadow-sm",
                    from === "cx" ? "bg-[#DCF8C6]" : "bg-white",
                  )}
                >
                  {BUBBLE_TAGGED[i] && (
                    <div className={cn("text-[10px] font-semibold mb-0.5", meta.accent)}>
                      🤖 {t("auto_reply")}
                    </div>
                  )}
                  {text}
                </div>
              </div>
            );
          })}
          {visibleCount < total && (
            <div className="flex">
              <div className="bg-white rounded-lg px-3 py-2 inline-flex gap-1 items-center shadow-sm">
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
              </div>
            </div>
          )}
        </div>

        {/* Side arrow controls (desktop only) */}
        <button
          onClick={() => {
            prev();
            setPlaying(false);
          }}
          aria-label="Previous scenario"
          className="hidden sm:flex absolute left-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white/95 text-slate-900 items-center justify-center shadow active:scale-95"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <button
          onClick={() => {
            next();
            setPlaying(false);
          }}
          aria-label="Next scenario"
          className="hidden sm:flex absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-white/95 text-slate-900 items-center justify-center shadow active:scale-95"
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>

      {/* Progress dots + play toggle */}
      <div className="flex items-center justify-center gap-2 mt-3">
        <button
          onClick={() => setPlaying((p) => !p)}
          aria-label={playing ? "Pause" : "Play"}
          className="w-8 h-8 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-600 active:scale-95"
        >
          {playing ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
        </button>
        <div className="flex gap-1.5">
          {SCENARIOS.map((s, i) => (
            <button
              key={s.id}
              onClick={() => {
                setIdx(i);
                setPlaying(false);
              }}
              aria-label={`Go to scenario ${i + 1}`}
              className={cn(
                "h-1.5 rounded-full transition-all",
                i === idx ? "w-6 bg-slate-900" : "w-1.5 bg-slate-300",
              )}
            />
          ))}
        </div>
      </div>

      <p className="text-center text-xs text-slate-500 mt-3 px-4">
        {tLanding("reels_helper")}
      </p>
    </div>
  );
}
