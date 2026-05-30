"use client";

import { motion } from "framer-motion";
import SectionHeader from "./SectionHeader";
import { scrollToSection } from "./scroll";
import { STEPS } from "./content";

export default function HowItWorks() {
  return (
    <section id="how" className="bg-[#f5faf6] py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        <SectionHeader
          eyebrow="How it works"
          heading="Live in *ten minutes*"
          subtext="From signup to first auto-reply. No tech skills, no migration."
          cta={{ label: "Start now", onClick: () => scrollToSection("pricing") }}
        />

        <div className="mt-10 flex flex-col gap-4">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1], delay: i * 0.05 }}
              viewport={{ once: true, margin: "-60px" }}
              className="group flex items-center gap-6 rounded-[40px] border border-slate-200 bg-white p-4 shadow-soft transition-shadow duration-300 hover:shadow-soft-lg sm:rounded-full"
            >
              <span className="relative grid h-14 w-14 shrink-0 place-items-center rounded-full sm:h-16 sm:w-16">
                <span className="accent-gradient absolute inset-0 rounded-full" />
                <span className="absolute inset-[2px] rounded-full bg-white" />
                <span className="relative font-display-serif text-gradient text-2xl italic">
                  {s.n}
                </span>
              </span>

              <div className="min-w-0 flex-1">
                <h3 className="text-lg text-slate-900 md:text-xl">{s.title}</h3>
                <p className="text-sm text-slate-500">{s.body}</p>
              </div>

              <span className="hidden h-9 w-9 shrink-0 place-items-center rounded-full border border-slate-200 text-slate-400 transition-colors duration-300 group-hover:bg-brand-50 group-hover:text-brand-600 sm:grid">
                →
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
