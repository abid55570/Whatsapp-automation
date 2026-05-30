"use client";

import { motion } from "framer-motion";
import { GALLERY } from "./content";

const CARDS = [
  { ...GALLERY[0], span: "md:col-span-8" }, // Restaurants
  { ...GALLERY[1], span: "md:col-span-4" }, // Gyms & studios
  { ...GALLERY[3], span: "md:col-span-4" }, // Salons & spas
  { ...GALLERY[2], span: "md:col-span-8" }, // Clinics
  { ...GALLERY[4], span: "md:col-span-6" }, // Kirana stores
  { ...GALLERY[5], span: "md:col-span-6" }, // Boutiques
];

const reveal = {
  initial: { opacity: 0, y: 30 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-100px" },
  transition: { duration: 1, ease: [0.25, 0.1, 0.25, 1] as const },
};

export default function BentoWorks() {
  return (
    <section id="works" className="bg-white py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        {/* Header */}
        <motion.div {...reveal} className="mb-10 md:mb-14">
          <div className="mb-4 flex items-center gap-3">
            <span className="h-px w-8 bg-slate-300" />
            <span className="text-xs uppercase tracking-[0.3em] text-slate-400">
              Built for
            </span>
          </div>
          <div className="flex flex-wrap items-end justify-between gap-6">
            <h2 className="max-w-xl font-display-serif text-4xl leading-[1.05] text-slate-900 md:text-6xl">
              Every kind of{" "}
              <span className="italic text-emerald-600">shop</span>
            </h2>
            <p className="max-w-sm text-sm leading-relaxed text-slate-500 md:text-base">
              From kirana counters to clinics — Whatly handles the chat so you can
              run the shop.
            </p>
          </div>
        </motion.div>

        {/* Bento grid */}
        <div className="grid auto-rows-[240px] grid-cols-1 gap-5 md:auto-rows-[340px] md:grid-cols-12 md:gap-6">
          {CARDS.map((card, i) => (
            <motion.div
              key={card.title}
              {...reveal}
              transition={{ ...reveal.transition, delay: i * 0.08 }}
              className={`group relative h-full overflow-hidden rounded-3xl border border-slate-200 bg-white ${card.span}`}
            >
              <div className="relative h-full w-full overflow-hidden">
                <img
                  src={card.image}
                  alt={card.title}
                  className="h-full w-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
                />
                {/* halftone dots */}
                <div
                  aria-hidden
                  className="pointer-events-none absolute inset-0 opacity-20 mix-blend-multiply"
                  style={{
                    backgroundImage:
                      "radial-gradient(circle, #000 1px, transparent 1px)",
                    backgroundSize: "4px 4px",
                  }}
                />
                {/* gradient scrim for label legibility */}
                <div
                  aria-hidden
                  className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-black/55 to-transparent"
                />
                {/* persistent type label */}
                <span className="absolute bottom-4 left-4 inline-flex items-center gap-1.5 rounded-full bg-white/90 px-3.5 py-1.5 text-sm font-semibold text-slate-900 shadow-sm backdrop-blur-sm transition-transform duration-500 group-hover:-translate-y-0.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-[#25d366]" />
                  {card.title}
                </span>

                {/* hover veil */}
                <div className="absolute inset-0 flex items-center justify-center bg-white/70 opacity-0 backdrop-blur-md transition-opacity duration-500 group-hover:opacity-100">
                  <span className="accent-gradient-animated rounded-full p-[1.5px]">
                    <span className="inline-flex items-center gap-1 rounded-full bg-white px-4 py-2 text-sm text-slate-900">
                      View —{" "}
                      <span className="font-display-serif italic">{card.title}</span>
                    </span>
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
