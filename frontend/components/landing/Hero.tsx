"use client";

import Link from "next/link";
import { scrollToSection } from "./scroll";
import PhoneMockup from "./PhoneMockup";
import { NAV_LINKS, SHOWCASE, SIGNUP_HREF } from "./content";

const SERIF = "'Instrument Serif', serif";

export default function Hero() {
  return (
    <section
      id="hero"
      className="relative min-h-screen overflow-hidden"
      style={{ backgroundColor: "hsl(201 100% 13%)" }}
    >
      {/* Background glow + faint starfield */}
      <div
        aria-hidden
        className="absolute inset-0 z-0"
        style={{
          background:
            "radial-gradient(70% 55% at 30% 15%, rgba(37,211,102,0.18), transparent 60%), radial-gradient(60% 50% at 90% 90%, rgba(18,140,126,0.20), transparent 60%), linear-gradient(180deg, hsl(201 100% 16%) 0%, hsl(201 100% 9%) 100%)",
        }}
      />
      <div
        aria-hidden
        className="absolute inset-0 z-0 opacity-30"
        style={{
          backgroundImage: "radial-gradient(rgba(255,255,255,0.5) 1px, transparent 1px)",
          backgroundSize: "32px 32px",
          maskImage: "radial-gradient(circle at 30% 30%, black, transparent 75%)",
          WebkitMaskImage: "radial-gradient(circle at 30% 30%, black, transparent 75%)",
        }}
      />

      {/* Nav */}
      <nav className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-8 py-6">
        <button
          onClick={() => scrollToSection("hero")}
          className="text-3xl tracking-tight text-white"
          style={{ fontFamily: SERIF }}
          aria-label="Home"
        >
          Whatly<sup className="text-xs">®</sup>
        </button>
        <div className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link, i) => (
            <button
              key={link.label}
              onClick={() => scrollToSection(link.section)}
              className={`text-sm transition-colors ${
                i === 0 ? "text-white" : "text-zinc-400 hover:text-white"
              }`}
            >
              {link.label}
            </button>
          ))}
        </div>
        <Link
          href={SIGNUP_HREF}
          className="liquid-glass rounded-full px-6 py-2.5 text-sm text-white transition-transform duration-300 hover:scale-[1.03]"
        >
          Begin Journey
        </Link>
      </nav>

      {/* Content */}
      <div className="relative z-10 mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-8 pb-20 pt-10 md:grid-cols-2 md:pt-16">
        {/* Left: copy */}
        <div className="text-center md:text-left">
          <span className="animate-fade-rise mb-6 inline-flex items-center gap-1.5 rounded-full border border-white/15 bg-white/[0.06] px-3 py-1 text-xs uppercase tracking-[0.25em] text-white/70">
            For Indian SMBs
          </span>
          <h1
            className="animate-fade-rise mb-6 text-5xl italic leading-[0.95] tracking-tight text-white md:text-6xl lg:text-7xl"
            style={{ fontFamily: SERIF }}
          >
            Where <em className="not-italic text-zinc-400">replies</em> flow{" "}
            <em className="not-italic text-zinc-400">through the silence.</em>
          </h1>
          <p className="animate-fade-rise-delay mx-auto mb-10 max-w-md text-base leading-relaxed text-zinc-300 md:mx-0">
            WhatsApp automation for ambitious shop owners — auto-replies, orders and
            pickups across six languages, answered instantly while you focus on the
            work that matters.
          </p>
          <div className="animate-fade-rise-delay-2 flex flex-wrap justify-center gap-3 md:justify-start">
            <Link
              href={SIGNUP_HREF}
              className="accent-gradient rounded-full px-7 py-3.5 text-sm font-semibold text-white shadow-soft-lg transition-transform duration-300 hover:scale-105"
            >
              Start 14-day free trial
            </Link>
            <button
              onClick={() => scrollToSection("features")}
              className="liquid-glass rounded-full px-7 py-3.5 text-sm text-white transition-transform duration-300 hover:scale-[1.03]"
            >
              See how it works
            </button>
          </div>
        </div>

        {/* Right: phone */}
        <div
          className="animate-fade-rise-delay flex justify-center md:justify-end"
          style={{ perspective: "1400px" }}
        >
          <div style={{ transform: "rotateY(-16deg) rotateX(2deg)", transformStyle: "preserve-3d" }}>
            <PhoneMockup
              name={SHOWCASE[1].phoneName}
              messages={SHOWCASE[1].chat}
              chatKey="hero"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
