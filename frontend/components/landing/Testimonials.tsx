"use client";

import { useEffect, useMemo, useRef } from "react";
import type { CSSProperties } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CircularTestimonials } from "@/components/ui/circular-testimonials";
import { TESTIMONIALS, type Testimonial } from "./content";

export default function Testimonials() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const centerRef = useRef<HTMLDivElement>(null);
  const col0Ref = useRef<HTMLDivElement>(null);
  const col1Ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const ctx = gsap.context(() => {
      // Pin + parallax only run on the desktop two-column layout. On phones the
      // section is the circular carousel below, so skip GSAP entirely.
      const mm = gsap.matchMedia();
      mm.add("(min-width: 768px)", () => {
        ScrollTrigger.create({
          trigger: sectionRef.current,
          start: "top top",
          end: "bottom bottom",
          pin: centerRef.current,
          pinSpacing: false,
        });
        const scrub = {
          trigger: sectionRef.current,
          start: "top bottom",
          end: "bottom top",
          scrub: true,
        };
        gsap.fromTo(col0Ref.current, { yPercent: 6 }, { yPercent: -10, ease: "none", scrollTrigger: scrub });
        gsap.fromTo(col1Ref.current, { yPercent: -12 }, { yPercent: 8, ease: "none", scrollTrigger: scrub });
      });
    }, sectionRef);
    return () => ctx.revert();
  }, []);

  const col0 = TESTIMONIALS.filter((t) => t.column === 0);
  const col1 = TESTIMONIALS.filter((t) => t.column === 1);

  // Mobile carousel data — flat list with portraits.
  const carousel = useMemo(
    () =>
      TESTIMONIALS.map((t) => ({
        quote: t.quote,
        name: t.name,
        designation: `${t.business} · ${t.location}`,
        src: t.image,
      })),
    []
  );

  const Heading = () => (
    <div className="mx-auto max-w-md text-center">
      <div className="mb-4 flex items-center justify-center gap-3">
        <span className="h-px w-8 bg-slate-300" />
        <span className="text-xs uppercase tracking-[0.3em] text-slate-400">Loved by shops</span>
        <span className="h-px w-8 bg-slate-300" />
      </div>
      <h2 className="font-display-serif text-4xl leading-[1.02] text-slate-900 sm:text-5xl md:text-7xl">
        What owners <span className="italic text-emerald-600">say</span>
      </h2>
      <p className="mx-auto mt-5 max-w-sm text-sm leading-relaxed text-slate-500 md:text-base">
        Kiranas, cafés, salons and clinics across India — closing more orders
        on WhatsApp with Whatly.
      </p>
    </div>
  );

  const Card = ({ t }: { t: Testimonial }) => (
    <figure
      style={{ "--rot": `${t.rotation}deg` } as CSSProperties}
      className="mx-auto w-full max-w-[460px] rounded-[1.75rem] border border-slate-200 bg-white p-8 shadow-[0_18px_50px_-20px_rgba(15,23,42,0.28)] transition-transform duration-500 [transform:rotate(var(--rot))] hover:scale-[1.02] hover:![transform:rotate(0deg)_scale(1.02)]"
    >
      <div className="mb-4 flex items-center justify-between">
        <span className="rounded-full border border-[#25d366]/30 bg-[#25d366]/10 px-3 py-1 text-xs font-semibold text-[#1faa59]">
          {t.type}
        </span>
        <span className="text-lg text-[#25d366]" aria-hidden>
          ★★★★★
        </span>
      </div>
      <blockquote className="text-lg leading-relaxed text-slate-700 md:text-xl">
        “{t.quote}”
      </blockquote>
      <figcaption className="mt-7 flex items-center gap-3.5">
        <span
          className="flex h-12 w-12 flex-none items-center justify-center rounded-full text-base font-semibold text-white"
          style={{ background: "linear-gradient(135deg,#25d366,#128c7e)" }}
        >
          {t.initials}
        </span>
        <span className="leading-tight">
          <span className="block text-sm font-semibold text-slate-900">{t.name}</span>
          <span className="block text-xs text-slate-500">
            {t.business} · {t.location}
          </span>
        </span>
      </figcaption>
    </figure>
  );

  return (
    <section id="testimonials" className="relative bg-white">
      {/* ---------- MOBILE: circular carousel ---------- */}
      <div className="px-5 py-16 md:hidden">
        <Heading />
        <div className="mt-10">
          <CircularTestimonials
            testimonials={carousel}
            autoplay
            fontSizes={{ name: "1.2rem", designation: "0.85rem", quote: "1rem" }}
          />
        </div>
      </div>

      {/* ---------- DESKTOP: pinned parallax columns ---------- */}
      <div ref={sectionRef} className="relative hidden md:block md:min-h-[165vh]">
        <div
          ref={centerRef}
          className="pointer-events-none relative z-10 flex h-screen items-center justify-center"
        >
          <div className="pointer-events-auto">
            <Heading />
          </div>
        </div>

        <div className="absolute inset-0 z-20 mx-auto grid max-w-[1500px] grid-cols-2 gap-28 px-10">
          <div ref={col0Ref} className="flex flex-col gap-16 pt-[12vh]">
            {col0.map((t) => (
              <Card key={t.name} t={t} />
            ))}
          </div>
          <div ref={col1Ref} className="flex flex-col gap-16 pt-[32vh]">
            {col1.map((t) => (
              <Card key={t.name} t={t} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
