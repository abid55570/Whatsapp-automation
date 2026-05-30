"use client";

import Link from "next/link";
import { GALLERY, SIGNUP_HREF } from "./content";

/** Compact, viewport-fitting gallery used as a flythrough panel. */
export default function GalleryPanel() {
  return (
    <section id="gallery" className="bg-white py-12">
      <div className="mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 flex items-center gap-3">
            <span className="h-px w-8 bg-slate-300" />
            <span className="text-xs uppercase tracking-[0.3em] text-slate-400">In the wild</span>
            <span className="h-px w-8 bg-slate-300" />
          </div>
          <h2 className="mb-3 text-4xl tracking-tight text-slate-900 md:text-5xl">
            Shops across <span className="font-display-serif italic text-gradient">India</span>
          </h2>
          <p className="mb-6 max-w-md text-sm text-slate-500 md:text-base">
            From a Mumbai kirana to a Kochi clinic — thousands of owners let the bot answer first.
          </p>
          <Link
            href={SIGNUP_HREF}
            className="accent-gradient inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold text-white shadow-soft-lg transition-transform duration-300 hover:scale-105"
          >
            Join them free <span aria-hidden>↗</span>
          </Link>
        </div>

        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          {GALLERY.map((item) => (
            <div
              key={item.title}
              className="group relative aspect-square overflow-hidden rounded-2xl border border-slate-200 bg-slate-100 shadow-soft"
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={item.image}
                alt={item.title}
                loading="lazy"
                className="absolute inset-0 h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
              <span className="absolute bottom-3 left-4 text-xs uppercase tracking-[0.15em] text-white">
                {item.title}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
