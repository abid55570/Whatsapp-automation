"use client";

import type { CSSProperties } from "react";

/**
 * Soft flowing "aurora" — a light base with a few large blurred green blobs
 * drifting on GPU transforms. Center stays light so foreground content reads.
 */
export default function AuroraBackground() {
  const blob = (
    color: string,
    style: CSSProperties,
    anim: string,
    duration: number,
    opacity = 0.55
  ): CSSProperties => ({
    background: `radial-gradient(circle at center, ${color}, transparent 62%)`,
    animation: `${anim} ${duration}s ease-in-out infinite`,
    opacity,
    ...style,
  });

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* light base */}
      <div className="absolute inset-0 bg-gradient-to-b from-white via-[#f4fdf9] to-[#e9faf0]" />

      <div className="aurora-blob" style={blob("#34d97c", { top: "-18%", left: "-12%", width: "62vw", height: "62vw" }, "aurora-a", 20)} />
      <div className="aurora-blob" style={blob("#128c7e", { bottom: "-22%", right: "-14%", width: "58vw", height: "58vw" }, "aurora-b", 24, 0.5)} />
      <div className="aurora-blob" style={blob("#5fd29a", { top: "20%", right: "-6%", width: "44vw", height: "44vw" }, "aurora-c", 26, 0.5)} />
      <div className="aurora-blob" style={blob("#a6e9c6", { bottom: "-10%", left: "8%", width: "46vw", height: "46vw" }, "aurora-c", 22, 0.55)} />

      {/* keep the very center light for readability */}
      <div
        className="absolute inset-0"
        style={{ background: "radial-gradient(60% 55% at 50% 48%, rgba(255,255,255,0.85), transparent 70%)" }}
      />
    </div>
  );
}
