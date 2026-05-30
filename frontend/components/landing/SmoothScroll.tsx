"use client";

import { useEffect } from "react";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

/**
 * Global momentum smooth-scroll (Lenis) wired into the GSAP ticker so every
 * pinned/scrubbed ScrollTrigger on the page stays perfectly in sync. Gives the
 * whole site that weighted, premium "glide" instead of stepped wheel scroll.
 */
export default function SmoothScroll() {
  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);

    const lenis = new Lenis({
      duration: 1.15, // weight of the glide (higher = more float)
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // expo-out
      smoothWheel: true,
      wheelMultiplier: 1,
      touchMultiplier: 1.6,
      autoRaf: false, // we drive raf from gsap.ticker below
    });

    // Expose so nav / CTA buttons can request smooth anchor scrolls.
    const w = window as unknown as { lenis?: Lenis };
    w.lenis = lenis;

    // Keep ScrollTrigger updated on every Lenis scroll frame.
    lenis.on("scroll", ScrollTrigger.update);

    const onTick = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(onTick);
    gsap.ticker.lagSmoothing(0);

    return () => {
      gsap.ticker.remove(onTick);
      lenis.destroy();
      delete w.lenis;
    };
  }, []);

  return null;
}
