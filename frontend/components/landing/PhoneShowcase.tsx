"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import PhoneMockup from "./PhoneMockup";
import { SHOWCASE } from "./content";

export default function PhoneShowcase() {
  const sectionRef = useRef<HTMLElement>(null);
  const [step, setStep] = useState(0);
  const [isDesktop, setIsDesktop] = useState(true);
  const N = SHOWCASE.length;

  // Track viewport so the 3D slide/rotate only runs on larger screens.
  useEffect(() => {
    const mq = window.matchMedia("(min-width: 768px)");
    const apply = () => setIsDesktop(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, []);

  // Derive the active step from scroll progress through the pinned section.
  useEffect(() => {
    let raf = 0;
    const update = () => {
      raf = 0;
      const sec = sectionRef.current;
      if (!sec) return;
      const total = sec.offsetHeight - window.innerHeight;
      const scrolled = Math.min(Math.max(-sec.getBoundingClientRect().top, 0), total);
      const progress = total > 0 ? scrolled / total : 0;
      const s = Math.min(N - 1, Math.floor(progress * N));
      setStep((prev) => (prev === s ? prev : s));
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    update();
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      cancelAnimationFrame(raf);
    };
  }, [N]);

  const uc = SHOWCASE[step];
  const phoneRight = step % 2 === 0; // alternate sides each step

  const phoneTransform = isDesktop
    ? `translate(-50%, -50%) translateX(${phoneRight ? "25vw" : "-25vw"}) rotateY(${
        phoneRight ? -17 : 17
      }deg) scale(0.92)`
    : "translate(-50%, -50%) scale(0.82)";

  return (
    <section ref={sectionRef} id="features" className="relative bg-white" style={{ height: `${(N + 1) * 100}vh` }}>
      <div className="sticky top-0 h-screen overflow-hidden">
        {/* soft brand glow */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(50% 50% at 50% 50%, rgba(37,211,102,0.07), transparent 70%)",
          }}
        />

        <div
          className="relative mx-auto h-full max-w-[1180px] px-6 md:px-10"
          style={{ perspective: "1400px" }}
        >
          {/* CARD */}
          <div
            className={`absolute top-1/2 z-10 w-[88%] -translate-y-1/2 md:w-[40%] ${
              isDesktop ? (phoneRight ? "left-6 md:left-10" : "right-6 md:right-10") : "left-1/2 -translate-x-1/2 text-center"
            }`}
            style={!isDesktop ? { top: "16%" } : undefined}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={uc.key}
                initial={{ opacity: 0, x: isDesktop ? (phoneRight ? -40 : 40) : 0, y: isDesktop ? 0 : 20 }}
                animate={{ opacity: 1, x: 0, y: 0 }}
                exit={{ opacity: 0, x: isDesktop ? (phoneRight ? 40 : -40) : 0, y: isDesktop ? 0 : -20 }}
                transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              >
                <div className="mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200 bg-white text-2xl shadow-soft">
                  {uc.emoji}
                </div>
                <div className="mb-3 text-xs uppercase tracking-[0.3em] text-slate-400">
                  Use case {String(step + 1).padStart(2, "0")} / {String(N).padStart(2, "0")}
                </div>
                <h2 className="mb-4 font-display-serif text-5xl italic leading-[0.95] text-slate-900 md:text-6xl">
                  {uc.title}
                </h2>
                <p className="max-w-md text-base leading-relaxed text-slate-500">{uc.blurb}</p>
              </motion.div>
            </AnimatePresence>

            {/* progress dots */}
            <div
              className={`mt-8 flex gap-2 ${
                isDesktop ? "" : "justify-center"
              }`}
            >
              {SHOWCASE.map((s, i) => (
                <span
                  key={s.key}
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    i === step ? "w-8 accent-gradient" : "w-1.5 bg-slate-300"
                  }`}
                />
              ))}
            </div>
          </div>

          {/* PHONE */}
          <div
            className="absolute left-1/2 top-1/2"
            style={{
              transform: phoneTransform,
              transition: "transform 0.85s cubic-bezier(0.22, 1, 0.36, 1)",
              transformStyle: "preserve-3d",
            }}
          >
            <PhoneMockup name={uc.phoneName} messages={uc.chat} chatKey={uc.key} />
          </div>
        </div>
      </div>
    </section>
  );
}
