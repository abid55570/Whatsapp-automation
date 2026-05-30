"use client";

import { motion } from "framer-motion";

interface SectionHeaderProps {
  eyebrow: string;
  /** Heading text; the word wrapped in *asterisks* renders in display serif italic. */
  heading: string;
  subtext: string;
  cta?: { label: string; onClick: () => void };
}

function renderHeading(heading: string) {
  const parts = heading.split(/\*(.+?)\*/);
  return parts.map((part, i) =>
    i % 2 === 1 ? (
      <span key={i} className="font-display-serif italic text-gradient">
        {part}
      </span>
    ) : (
      <span key={i}>{part}</span>
    ),
  );
}

export default function SectionHeader({
  eyebrow,
  heading,
  subtext,
  cta,
}: SectionHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, ease: [0.25, 0.1, 0.25, 1] }}
      viewport={{ once: true, margin: "-100px" }}
      className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between"
    >
      <div className="max-w-xl">
        <div className="mb-4 flex items-center gap-3">
          <span className="h-px w-8 bg-slate-300" />
          <span className="text-xs uppercase tracking-[0.3em] text-slate-400">
            {eyebrow}
          </span>
        </div>
        <h2 className="mb-3 text-4xl tracking-tight text-slate-900 md:text-5xl lg:text-6xl">
          {renderHeading(heading)}
        </h2>
        <p className="text-sm text-slate-500 md:text-base">{subtext}</p>
      </div>

      {cta && (
        <button
          onClick={cta.onClick}
          className="hidden items-center gap-2 whitespace-nowrap rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-900 shadow-soft transition-colors duration-300 hover:border-brand-300 hover:text-brand-700 md:inline-flex"
        >
          {cta.label} <span aria-hidden>→</span>
        </button>
      )}
    </motion.div>
  );
}
