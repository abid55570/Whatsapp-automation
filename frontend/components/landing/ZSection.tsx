"use client";

import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

/**
 * Wraps a section in a 3D perspective and drives it along the Z axis as it
 * scrolls into view — it starts pushed back + small + faded and "approaches"
 * the viewer to its resting state. Perspective lives on this wrapper (not a
 * global ancestor) so it never breaks position:fixed pinning elsewhere.
 */
export default function ZSection({ children }: { children: ReactNode }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    const ctx = gsap.context(() => {
      gsap.fromTo(
        innerRef.current,
        { z: -750, scale: 0.84, opacity: 0, rotateX: 7 },
        {
          z: 0,
          scale: 1,
          opacity: 1,
          rotateX: 0,
          ease: "power2.out",
          scrollTrigger: {
            trigger: wrapRef.current,
            start: "top 90%",
            end: "top 45%",
            scrub: 0.6,
          },
        },
      );
    }, wrapRef);
    return () => ctx.revert();
  }, []);

  return (
    <div ref={wrapRef} style={{ perspective: "1200px" }}>
      <div
        ref={innerRef}
        style={{ transformStyle: "preserve-3d", willChange: "transform, opacity" }}
      >
        {children}
      </div>
    </div>
  );
}
