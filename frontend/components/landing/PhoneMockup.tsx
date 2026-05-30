"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { ChatMsg } from "./content";

interface PhoneMockupProps {
  name: string;
  messages: ChatMsg[];
  /** Changing this key crossfades the chat content. */
  chatKey: string;
  className?: string;
}

const W = 300; // px width
const H = 620; // px height
const T = 18; // px thickness (depth)

/** A genuinely 3D WhatsApp phone: front screen, iPhone-16-style back case and
 *  titanium edge faces, all in a preserve-3d box so rotation shows real depth. */
export default function PhoneMockup({ name, messages, chatKey, className = "" }: PhoneMockupProps) {
  return (
    <div
      className={`relative ${className}`}
      style={{ width: W, height: H, transformStyle: "preserve-3d" }}
    >
      {/* FRONT — screen */}
      <div
        className="absolute inset-0 rounded-[2.6rem] border border-slate-800 bg-slate-900 p-3"
        style={{ transform: `translateZ(${T / 2}px)`, backfaceVisibility: "hidden" }}
      >
        {/* Notch */}
        <div className="absolute left-1/2 top-3 z-20 h-6 w-28 -translate-x-1/2 rounded-full bg-slate-900" />
        <div className="flex h-full w-full flex-col overflow-hidden rounded-[2rem] bg-[#ECE5DD]">
          <div className="flex items-center gap-3 bg-[#075E54] px-4 pb-3 pt-7 text-white">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-sm font-bold text-[#075E54]">
              {name.charAt(0)}
            </div>
            <div className="leading-tight">
              <div className="text-sm font-semibold">{name}</div>
              <div className="text-[10px] text-green-200">online</div>
            </div>
          </div>
          <div className="relative flex-1 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={chatKey}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.35 }}
                className="flex flex-col gap-2 p-3"
              >
                {messages.map((m, i) => (
                  <div key={i} className={m.side === "out" ? "flex justify-end" : "flex"}>
                    <div
                      className={`max-w-[80%] rounded-lg px-3 py-1.5 text-[13px] leading-snug text-slate-800 shadow-sm ${
                        m.side === "out" ? "bg-[#DCF8C6]" : "bg-white"
                      }`}
                    >
                      {m.bot && (
                        <div className="mb-0.5 text-[9px] font-semibold uppercase tracking-wide text-emerald-600">
                          🤖 Auto-reply
                        </div>
                      )}
                      {m.text}
                    </div>
                  </div>
                ))}
              </motion.div>
            </AnimatePresence>
          </div>
          <div className="flex items-center gap-2 bg-[#ECE5DD] px-3 pb-3">
            <div className="flex-1 rounded-full bg-white px-4 py-2 text-xs text-slate-400">
              Type a message
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#075E54] text-white">
              ➤
            </div>
          </div>
        </div>
      </div>

      {/* BACK — iPhone 16 case */}
      <div
        className="absolute inset-0 overflow-hidden rounded-[2.6rem]"
        style={{
          transform: `rotateY(180deg) translateZ(${T / 2}px)`,
          backfaceVisibility: "hidden",
          background:
            "linear-gradient(150deg, #2b2b2f 0%, #1a1a1d 45%, #0f0f11 100%)",
          boxShadow: "inset 0 0 0 2px rgba(255,255,255,0.04)",
        }}
      >
        {/* glossy sheen */}
        <div
          aria-hidden
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(115deg, rgba(255,255,255,0.10) 0%, transparent 30%, transparent 70%, rgba(255,255,255,0.06) 100%)",
          }}
        />
        {/* Camera island (vertical pill, 2 lenses) */}
        <div
          className="absolute left-5 top-5 flex flex-col items-center gap-3 rounded-[1.6rem] p-2.5"
          style={{
            background: "linear-gradient(160deg, #3a3a3e, #18181a)",
            boxShadow: "inset 0 1px 2px rgba(255,255,255,0.10), 0 2px 6px rgba(0,0,0,0.5)",
          }}
        >
          {[0, 1].map((k) => (
            <div
              key={k}
              className="flex h-11 w-11 items-center justify-center rounded-full"
              style={{
                background: "radial-gradient(circle at 35% 30%, #4b4b52, #0a0a0c 70%)",
                boxShadow: "inset 0 0 0 2px #2a2a2e, 0 1px 2px rgba(0,0,0,0.6)",
              }}
            >
              <div
                className="h-4 w-4 rounded-full"
                style={{ background: "radial-gradient(circle at 40% 35%, #6f7bdc55, #0a0a0c)" }}
              />
            </div>
          ))}
        </div>
        {/* Flash + mic */}
        <div className="absolute left-[88px] top-7 h-4 w-4 rounded-full bg-[#d9d4c2] shadow-inner" />
        {/* Apple logo */}
        <svg
          viewBox="0 0 24 24"
          className="absolute left-1/2 top-[44%] h-12 w-12 -translate-x-1/2 -translate-y-1/2"
          style={{ fill: "rgba(255,255,255,0.85)" }}
        >
          <path d="M16.365 1.43c0 1.14-.42 2.2-1.12 3.01-.85.99-2.24 1.76-3.4 1.67-.14-1.12.42-2.3 1.07-3.04.74-.85 2.06-1.49 3.18-1.55.02.31.27-.09.27-.09zM20.5 17.06c-.55 1.27-.82 1.84-1.53 2.96-.99 1.57-2.39 3.52-4.12 3.53-1.54.01-1.93-1-4.02-.99-2.09.01-2.52.99-4.06.97-1.73-.02-3.06-1.79-4.05-3.36C-.07 16.07-.36 11.2 1.5 8.6c1.06-1.49 2.74-2.36 4.32-2.36 1.61 0 2.62 1.06 3.95 1.06 1.29 0 2.07-1.06 3.93-1.06 1.41 0 2.91.77 3.97 2.1-3.49 1.91-2.92 6.9.83 8.62z" />
        </svg>
        {/* iPhone wordmark */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-[11px] font-medium tracking-wide text-white/30">
          iPhone
        </div>
      </div>

      {/* EDGES — titanium frame for real thickness */}
      <Edge style={{ width: T, height: H, left: "50%", top: 0, transform: `translateX(-50%) translateX(${W / 2}px) rotateY(90deg)` }} />
      <Edge style={{ width: T, height: H, left: "50%", top: 0, transform: `translateX(-50%) translateX(${-W / 2}px) rotateY(-90deg)` }} />
      <Edge style={{ width: W, height: T, left: 0, top: "50%", transform: `translateY(-50%) translateY(${-H / 2}px) rotateX(90deg)` }} />
      <Edge style={{ width: W, height: T, left: 0, top: "50%", transform: `translateY(-50%) translateY(${H / 2}px) rotateX(-90deg)` }} />
    </div>
  );
}

function Edge({ style }: { style: React.CSSProperties }) {
  return (
    <div
      aria-hidden
      className="absolute"
      style={{
        background: "linear-gradient(90deg, #1b1b1d, #4a4a50 50%, #1b1b1d)",
        ...style,
      }}
    />
  );
}
