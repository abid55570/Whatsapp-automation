"use client";

import { motion } from "framer-motion";
import { STATS } from "./content";

export default function Stats() {
  return (
    <section className="bg-[#f5faf6] py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        <div className="grid grid-cols-2 gap-10 sm:grid-cols-4 sm:gap-6">
          {STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1], delay: i * 0.08 }}
              viewport={{ once: true, margin: "-80px" }}
              className="flex flex-col items-center text-center sm:items-start sm:text-left"
            >
              <span className="text-gradient font-sans text-5xl font-extrabold leading-none tracking-tight md:text-6xl lg:text-7xl">
                {stat.value}
              </span>
              <span className="mt-3 text-xs uppercase tracking-[0.2em] text-slate-500">
                {stat.label}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
