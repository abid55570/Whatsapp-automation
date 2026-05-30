"use client";

import type { CSSProperties } from "react";
import { motion } from "framer-motion";
import SectionHeader from "./SectionHeader";
import { scrollToSection } from "./scroll";
import { USE_CASES } from "./content";

const HALFTONE: CSSProperties = {
  backgroundImage: "radial-gradient(circle, #000 1px, transparent 1px)",
  backgroundSize: "4px 4px",
};

export default function UseCasesBento() {
  return (
    <section id="features" className="bg-white py-12 md:py-16">
      <div className="mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        <SectionHeader
          eyebrow="Built for every shop"
          heading="One bot, every *business*"
          subtext="Kirana, restaurant, salon, clinic — each shop uses only what it needs."
          cta={{ label: "See it live", onClick: () => scrollToSection("gallery") }}
        />

        <div className="mt-10 grid grid-cols-1 gap-5 md:grid-cols-12 md:gap-6">
          {USE_CASES.map((uc, i) => (
            <motion.article
              key={uc.title}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1], delay: (i % 2) * 0.1 }}
              viewport={{ once: true, margin: "-80px" }}
              className={`group relative aspect-[16/11] overflow-hidden rounded-3xl border border-slate-200 bg-slate-100 shadow-soft ${
                uc.span === 7 ? "md:col-span-7" : "md:col-span-5"
              }`}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={uc.image}
                alt={uc.title}
                loading="lazy"
                className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute inset-0 opacity-20 mix-blend-multiply" style={HALFTONE} />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />

              {/* Resting caption */}
              <div className="absolute inset-x-0 bottom-0 z-10 p-6 transition-opacity duration-300 group-hover:opacity-0">
                <h3 className="font-display-serif text-3xl italic text-white">{uc.title}</h3>
                <p className="mt-1 max-w-sm text-sm text-white/70">{uc.blurb}</p>
              </div>

              {/* Hover veil + label */}
              <div className="absolute inset-0 bg-black/70 opacity-0 backdrop-blur-md transition-opacity duration-500 group-hover:opacity-100" />
              <div className="absolute inset-0 z-10 flex items-center justify-center opacity-0 transition-opacity duration-500 group-hover:opacity-100">
                <span className="relative inline-flex">
                  <span
                    aria-hidden
                    style={{ inset: "-2px" }}
                    className="accent-gradient-animated absolute rounded-full"
                  />
                  <span className="relative inline-flex items-center gap-1.5 rounded-full bg-white px-5 py-2.5 text-sm text-black">
                    Explore — <span className="font-display-serif italic">{uc.title}</span>
                  </span>
                </span>
              </div>
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}
