"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";

/** Infinite GSAP marquee band. Renders the phrase twice and slides -50% for a
 *  seamless loop. */
export default function Marquee({
  text = "WHATSAPP AUTOMATION",
  repeat = 6,
  duration = 40,
}: {
  text?: string;
  repeat?: number;
  duration?: number;
}) {
  const trackRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.to(trackRef.current, {
        xPercent: -50,
        duration,
        ease: "none",
        repeat: -1,
      });
    });
    return () => ctx.revert();
  }, [duration]);

  const half = Array.from({ length: repeat });
  const Group = () => (
    <>
      {half.map((_, i) => (
        <span
          key={i}
          className="font-display-serif text-3xl italic leading-none text-slate-900 md:text-5xl"
        >
          {text} <span className="px-3 text-[#25d366]">•</span>
        </span>
      ))}
    </>
  );

  return (
    <section className="overflow-hidden border-y border-slate-200 bg-white py-6 md:py-8">
      <div ref={trackRef} className="flex w-max items-center whitespace-nowrap will-change-transform">
        <Group />
        <Group />
      </div>
    </section>
  );
}
