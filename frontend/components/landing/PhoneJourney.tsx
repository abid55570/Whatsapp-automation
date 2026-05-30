"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import AnimatedGradientBackground from "@/components/ui/animated-gradient-background";
import SpotlightBackground from "@/components/ui/spotlight-background";
import { SHOWCASE, SIGNUP_HREF } from "./content";

// R3F Canvas must never be server-rendered (it crashes in SSR).
const Phone3D = dynamic(() => import("./Phone3D"), { ssr: false });

const SERIF = "'Instrument Serif', serif";

/**
 * Hero + use-case story driven by ONE real iPhone 17 (Three.js) that moves in
 * 3D. The section is pinned; scroll progress drives the phone (zoom -> 360 spin
 * -> settle -> alternating sides) and swaps the card + chat content per step.
 */
export default function PhoneJourney() {
  const rootRef = useRef<HTMLDivElement>(null);
  const pinRef = useRef<HTMLDivElement>(null);
  const heroRef = useRef<HTMLDivElement>(null);
  const progressRef = useRef(0);
  const N = SHOWCASE.length;
  const [step, setStep] = useState(0); // 0 = hero, 1..N = use-cases

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const st = ScrollTrigger.create({
      trigger: rootRef.current,
      start: "top top",
      end: "bottom bottom",
      pin: pinRef.current,
      anticipatePin: 1,
      onUpdate: (self) => {
        const p = self.progress;
        progressRef.current = p;
        // Card appears when the phone arrives on a side (0.14) and swaps during
        // each glide-across (mid-transition), so phone + card stay in sync.
        const s = p < 0.07 ? 0 : p < 0.3 ? 1 : p < 0.55 ? 2 : p < 0.8 ? 3 : 4;
        setStep((prev) => (prev === s ? prev : s));
        // Fade the hero copy out as the phone rises to its closest point (~0.07).
        if (heroRef.current) {
          const o = Math.min(1, Math.max(0, 1 - (p - 0.01) / 0.06));
          heroRef.current.style.opacity = String(o);
          heroRef.current.style.visibility = o < 0.02 ? "hidden" : "visible";
        }
      },
    });
    return () => st.kill();
  }, []);

  const isHero = step === 0;
  const uc = SHOWCASE[Math.max(0, step - 1)];
  const phoneRight = step === 0 || step % 2 === 1;
  const cardOnLeft = phoneRight;

  return (
    <div ref={rootRef} id="features" style={{ height: `${(N + 2) * 100}vh` }}>
      <div ref={pinRef} className="relative h-screen w-full overflow-hidden bg-white">
        {/* White → green radial glow base (subtle breathing) */}
        <AnimatedGradientBackground
          Breathing
          startingGap={125}
          breathingRange={6}
          animationSpeed={0.02}
          gradientColors={[
            "#ffffff",
            "#f5fdf9",
            "#e6faef",
            "#cdf3df",
            "#a6e9c6",
            "#5fd29a",
            "#1faa59",
          ]}
          gradientStops={[35, 50, 60, 70, 80, 90, 100]}
        />

        {/* Spotlight glow that follows the cursor */}
        <SpotlightBackground color="rgba(37,211,102,0.4)" idleSize={320} movingSize={240} />


        {/* Stage — the floating Navbar1 (in Landing) overlays the top */}
        <div id="hero" className="relative h-screen">
          {/* The single 3D iPhone (fills the stage; moves within it) */}
          <Phone3D progressRef={progressRef} uc={isHero ? SHOWCASE[1] : uc} />

          {/* Hero copy — fades out as the phone rises to its closest point */}
          <div
            ref={heroRef}
            className="pointer-events-none absolute left-1/2 top-[10%] z-20 w-[92%] max-w-2xl -translate-x-1/2 text-center"
          >
            <span className="mb-6 inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs uppercase tracking-[0.25em] text-slate-500">
              For Indian SMBs
            </span>
            <h1
              className="mb-6 text-5xl italic leading-[0.95] tracking-tight text-slate-900 md:text-6xl lg:text-7xl"
              style={{ fontFamily: SERIF }}
            >
              Where <em className="not-italic text-emerald-500">replies</em> flow{" "}
              <em className="not-italic text-slate-400">through the silence.</em>
            </h1>
            <p className="mx-auto mb-8 max-w-md text-base leading-relaxed text-slate-600">
              WhatsApp automation for ambitious shop owners — auto-replies, orders
              and pickups across six languages.
            </p>
            <Link
              href={SIGNUP_HREF}
              className="pointer-events-auto accent-gradient inline-block rounded-full px-7 py-3.5 text-sm font-semibold text-white shadow-soft-lg transition-transform duration-300 hover:scale-105"
            >
              Start 14-day free trial
            </Link>
            <div className="mt-10 text-xs uppercase tracking-[0.3em] text-slate-400">
              Scroll to begin ↓
            </div>
          </div>

          {/* Use-case card (steps 1..N) — light text over the dark backdrop */}
          <div
            className={`pointer-events-none absolute left-1/2 top-[14%] z-20 w-[90%] max-w-md -translate-x-1/2 text-center transition-opacity duration-150 md:top-1/2 md:w-[44%] md:max-w-[640px] md:-translate-x-0 md:-translate-y-1/2 md:text-left ${
              isHero ? "opacity-0" : "opacity-100"
            } ${cardOnLeft ? "md:left-16 md:right-auto" : "md:left-auto md:right-16"}`}
          >
            <motion.div
              key={uc.key}
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            >
                {/* Emoji chip with soft green glow */}
                <div className="mb-4 inline-flex h-14 w-14 items-center justify-center rounded-[1.4rem] border border-slate-200 bg-white text-[1.6rem] shadow-[0_10px_40px_-8px_rgba(37,211,102,0.35)] md:mb-7 md:h-[72px] md:w-[72px] md:text-[2rem]">
                  {uc.emoji}
                </div>

                {/* Eyebrow with accent line + green index */}
                <div className="mb-3 flex items-center justify-center gap-3 md:mb-5 md:justify-start">
                  <span className="h-px w-10 bg-gradient-to-r from-[#25d366] to-transparent" />
                  <span className="text-[0.7rem] font-semibold uppercase tracking-[0.4em] text-slate-400">
                    Use case{" "}
                    <span className="text-[#1faa59]">{String(step).padStart(2, "0")}</span>
                    <span className="text-slate-300"> / {String(N).padStart(2, "0")}</span>
                  </span>
                </div>

                {/* Title */}
                <h2 className="mb-3 font-display-serif text-4xl italic leading-[0.92] tracking-tight text-slate-900 sm:text-5xl md:mb-6 md:text-7xl lg:text-[5.25rem]">
                  {uc.title}
                </h2>

                {/* Blurb — trimmed on mobile so the card stays in the top half */}
                <p className="mx-auto line-clamp-3 max-w-lg text-sm leading-relaxed text-slate-600 md:mx-0 md:line-clamp-none md:text-lg">
                  {uc.blurb}
                </p>

                {/* Feature pointers */}
                <ul className="mx-auto mt-4 grid max-w-lg gap-x-6 gap-y-2 text-left sm:grid-cols-2 md:mx-0 md:mt-7 md:gap-y-3">
                  {uc.points.map((pt) => (
                    <li key={pt} className="flex items-start gap-2.5">
                      <span className="mt-0.5 flex h-5 w-5 flex-none items-center justify-center rounded-full bg-[#25d366]/15 text-[0.7rem] text-[#1faa59]">
                        ✓
                      </span>
                      <span className="text-sm leading-snug text-slate-600">{pt}</span>
                    </li>
                  ))}
                </ul>
            </motion.div>

            {/* Progress dots */}
            <div className="mt-5 flex justify-center gap-2.5 md:mt-10 md:justify-start">
              {SHOWCASE.map((s, i) => (
                <span
                  key={s.key}
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    i === step - 1 ? "w-10 accent-gradient" : "w-2 bg-slate-300"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
