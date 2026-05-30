"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import gsap from "gsap";
import { SIGNUP_HREF, SOCIALS } from "./content";

const MARQUEE_TEXT = "AUTOMATE YOUR WHATSAPP • ";

const FOOTER_LINKS = [
  { label: "Pricing", href: "#pricing" },
  { label: "Sign up", href: SIGNUP_HREF },
  { label: "Terms", href: "/terms" },
  { label: "Privacy", href: "/privacy" },
  { label: "Refund", href: "/refund" },
];

export default function ContactFooter() {
  const marqueeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.to(".marquee-track", { xPercent: -50, duration: 40, ease: "none", repeat: -1 });
    }, marqueeRef);
    return () => ctx.revert();
  }, []);

  return (
    <footer
      id="contact"
      className="relative overflow-hidden bg-gradient-to-br from-[#075E54] via-[#128C7E] to-[#25D366] pb-8 pt-16 text-white md:pb-12 md:pt-20"
    >
      {/* Soft texture */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)",
          backgroundSize: "22px 22px",
        }}
      />

      <div className="relative z-10 mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        {/* Marquee */}
        <div ref={marqueeRef} className="overflow-hidden">
          <div className="marquee-track flex whitespace-nowrap">
            {Array.from({ length: 10 }).map((_, i) => (
              <span
                key={i}
                className="font-display-serif text-5xl italic text-white/90 md:text-7xl lg:text-8xl"
              >
                {MARQUEE_TEXT}
              </span>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-16 flex flex-col items-center text-center">
          <p className="mb-6 text-xs uppercase tracking-[0.3em] text-white/70">
            Stop typing the same answers
          </p>
          <Link
            href={SIGNUP_HREF}
            className="rounded-full bg-white px-8 py-4 text-base font-semibold text-[#075E54] shadow-soft-lg transition-transform duration-300 hover:scale-105 md:text-lg"
          >
            Start your 14-day free trial
          </Link>
          <p className="mt-4 text-xs text-white/60">No credit card · Plans from ₹399/mo</p>
        </div>

        {/* Footer bar */}
        <div className="mt-20 flex flex-col items-center justify-between gap-6 border-t border-white/20 pt-8 md:flex-row">
          <div className="flex items-center gap-2 text-sm text-white/80">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-white opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-white" />
            </span>
            Available · 14-day free trial
          </div>

          <div className="flex flex-wrap items-center justify-center gap-5">
            {FOOTER_LINKS.map((l) => (
              <Link
                key={l.label}
                href={l.href}
                className="text-sm text-white/75 transition-colors hover:text-white"
              >
                {l.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-4">
            {SOCIALS.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-white/70 transition-colors hover:text-white"
              >
                {s.label}
              </a>
            ))}
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-white/60">
          © 2026 WhatsApp Auto · Powered by Meta WhatsApp Cloud API
        </p>
      </div>
    </footer>
  );
}
