"use client";

import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { GALLERY, type GalleryItem, SIGNUP_HREF } from "./content";

export default function Explorations() {
  const sectionRef = useRef<HTMLElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState<GalleryItem | null>(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        trigger: sectionRef.current,
        start: "top top",
        end: "bottom bottom",
        pin: contentRef.current,
        pinSpacing: false,
      });

      gsap.to(".gal-col-0", {
        yPercent: -12,
        ease: "none",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top bottom",
          end: "bottom top",
          scrub: 1,
        },
      });
      gsap.to(".gal-col-1", {
        yPercent: 12,
        ease: "none",
        scrollTrigger: {
          trigger: sectionRef.current,
          start: "top bottom",
          end: "bottom top",
          scrub: 1,
        },
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  const columns: [GalleryItem[], GalleryItem[]] = [
    GALLERY.filter((g) => g.column === 0),
    GALLERY.filter((g) => g.column === 1),
  ];

  return (
    <section id="gallery" ref={sectionRef} className="relative min-h-[300vh] bg-white">
      {/* Pinned center */}
      <div
        ref={contentRef}
        className="z-10 flex h-screen flex-col items-center justify-center px-6 text-center"
      >
        <div className="mb-4 flex items-center gap-3">
          <span className="h-px w-8 bg-slate-300" />
          <span className="text-xs uppercase tracking-[0.3em] text-slate-400">In the wild</span>
          <span className="h-px w-8 bg-slate-300" />
        </div>
        <h2 className="mb-4 text-4xl tracking-tight text-slate-900 md:text-6xl lg:text-7xl">
          Shops across <span className="font-display-serif italic text-gradient">India</span>
        </h2>
        <p className="mb-8 max-w-md text-sm text-slate-500 md:text-base">
          From a Mumbai kirana to a Kochi clinic — thousands of owners let the
          bot answer first.
        </p>
        <Link
          href={SIGNUP_HREF}
          className="accent-gradient inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold text-white shadow-soft-lg transition-transform duration-300 hover:scale-105"
        >
          Join them free <span aria-hidden>↗</span>
        </Link>
      </div>

      {/* Parallax columns */}
      <div className="pointer-events-none absolute inset-0 z-20 flex justify-center px-6">
        <div className="grid w-full max-w-[1400px] grid-cols-2 gap-12 md:gap-40">
          {columns.map((col, colIndex) => (
            <div
              key={colIndex}
              className={`gal-col-${colIndex} flex flex-col gap-[40vh] ${
                colIndex === 1 ? "mt-[30vh]" : "mt-[10vh]"
              }`}
            >
              {col.map((item) => (
                <button
                  key={item.title}
                  onClick={() => setActive(item)}
                  style={{ transform: `rotate(${item.rotation}deg)` }}
                  className="group pointer-events-auto mx-auto w-full max-w-[320px] overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-soft-lg transition-transform duration-500 hover:scale-[1.03] hover:!rotate-0"
                >
                  <div className="aspect-square overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={item.image}
                      alt={item.title}
                      loading="lazy"
                      className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                    />
                  </div>
                  <span className="block px-4 py-3 text-left text-xs uppercase tracking-[0.15em] text-slate-500">
                    {item.title}
                  </span>
                </button>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Lightbox */}
      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setActive(null)}
            className="fixed inset-0 z-[200] flex items-center justify-center bg-black/85 p-6 backdrop-blur-md"
          >
            <motion.img
              key={active.image}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              src={active.image.replace(/w=\d+/, "w=1400")}
              alt={active.title}
              className="max-h-[85vh] max-w-[85vw] rounded-2xl border border-white/10 object-contain"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
