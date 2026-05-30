"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { NAV_LINKS, SIGNUP_HREF } from "./content";
import { scrollToSection } from "./scroll";

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [active, setActive] = useState("hero");

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 100);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav className="fixed inset-x-0 top-0 z-50 flex justify-center px-4 pt-4 md:pt-6">
      <div
        className={[
          "inline-flex items-center rounded-full border border-slate-200 bg-white/80 px-2 py-2 backdrop-blur-md transition-shadow duration-300",
          scrolled ? "shadow-soft-lg" : "shadow-soft",
        ].join(" ")}
      >
        {/* Logo */}
        <button
          onClick={() => {
            setActive("hero");
            scrollToSection("hero");
          }}
          className="group relative grid h-9 w-9 place-items-center rounded-full transition-transform duration-300 hover:scale-110"
          aria-label="Home"
        >
          <span className="accent-gradient absolute inset-0 rounded-full transition-transform duration-500 group-hover:rotate-180" />
          <span className="absolute inset-[2px] rounded-full bg-white" />
          <span className="relative font-display-serif text-gradient text-[15px] italic">
            W
          </span>
        </button>

        <span className="mx-1 hidden h-5 w-px bg-slate-200 sm:block" />

        <div className="flex items-center">
          {NAV_LINKS.map((link) => {
            const isActive = active === link.section;
            return (
              <button
                key={link.label}
                onClick={() => {
                  setActive(link.section);
                  scrollToSection(link.section);
                }}
                className={[
                  "rounded-full px-3 py-1.5 text-xs transition-colors sm:px-4 sm:py-2 sm:text-sm",
                  isActive
                    ? "bg-brand-50 text-brand-700"
                    : "text-slate-500 hover:bg-slate-100 hover:text-slate-900",
                ].join(" ")}
              >
                {link.label}
              </button>
            );
          })}
        </div>

        <span className="mx-1 hidden h-5 w-px bg-slate-200 sm:block" />

        {/* Start free */}
        <Link href={SIGNUP_HREF} className="group relative inline-flex">
          <span className="accent-gradient relative inline-flex items-center gap-1 rounded-full px-3 py-1.5 text-xs font-semibold text-white transition-transform duration-300 group-hover:scale-[1.04] sm:px-4 sm:py-2 sm:text-sm">
            Start free <span aria-hidden>↗</span>
          </span>
        </Link>
      </div>
    </nav>
  );
}
