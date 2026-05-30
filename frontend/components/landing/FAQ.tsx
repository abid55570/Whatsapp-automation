"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import SectionHeader from "./SectionHeader";
import { FAQS } from "./content";

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="bg-[#f5faf6] py-16 md:py-24">
      <div className="mx-auto max-w-[900px] px-6 md:px-10 lg:px-16">
        <SectionHeader
          eyebrow="FAQ"
          heading="Common *questions*"
          subtext="Everything owners ask before they switch. Still unsure? Just message us."
        />

        <div className="mt-10 flex flex-col gap-3">
          {FAQS.map((item, i) => {
            const isOpen = open === i;
            return (
              <motion.div
                key={item.q}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: i * 0.04 }}
                viewport={{ once: true, margin: "-40px" }}
                className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft"
              >
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="flex w-full items-center justify-between gap-3 p-5 text-left"
                >
                  <span className="text-sm font-medium text-slate-900 md:text-base">{item.q}</span>
                  <span
                    className={`text-xl leading-none text-brand-500 transition-transform duration-300 ${
                      isOpen ? "rotate-45" : ""
                    }`}
                  >
                    +
                  </span>
                </button>
                <div
                  className="grid transition-all duration-300 ease-out"
                  style={{ gridTemplateRows: isOpen ? "1fr" : "0fr" }}
                >
                  <div className="overflow-hidden">
                    <p className="px-5 pb-5 text-sm leading-relaxed text-slate-500">{item.a}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
