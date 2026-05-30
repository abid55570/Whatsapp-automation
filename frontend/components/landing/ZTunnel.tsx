"use client";

import { useEffect, useRef } from "react";
import type { ReactNode } from "react";

/**
 * "Flythrough" scroller. Panels are stacked in Z-space inside a fixed viewport.
 * Scrolling does NOT move the page down — it drives a forward camera deeper into
 * the screen, so each panel rushes toward you, passes through, and reveals the
 * next one waiting ahead in the distance (like going through a series of doors).
 *
 * A tall empty "driver" element provides the scroll distance; the visible stage
 * is position:fixed and never scrolls.
 */
export default function ZTunnel({ panels }: { panels: ReactNode[] }) {
  const driverRef = useRef<HTMLDivElement>(null);
  const panelRefs = useRef<Array<HTMLDivElement | null>>([]);
  const N = panels.length;

  const STEP = 1100; // px of depth between consecutive panels
  const PERSPECTIVE = 1100;

  useEffect(() => {
    let raf = 0;

    const update = () => {
      raf = 0;
      const driver = driverRef.current;
      if (!driver) return;
      const maxScroll = driver.offsetHeight - window.innerHeight;
      const progress = maxScroll > 0 ? Math.min(Math.max(window.scrollY / maxScroll, 0), 1) : 0;
      const cam = progress * (N - 1); // which panel the camera is currently at

      panelRefs.current.forEach((el, i) => {
        if (!el) return;
        const d = i - cam; // >0 = still ahead (deep in screen), <0 = already passed
        const z = -d * STEP;

        let opacity: number;
        if (d >= 0) {
          opacity = Math.max(0, 1 - d * 0.6); // fade the further-away panels
        } else {
          opacity = Math.max(0, 1 + d * 2.4); // fade fast once it flies past the camera
        }

        el.style.transform = `translate(-50%, -50%) translateZ(${z}px)`;
        el.style.opacity = String(opacity);
        el.style.visibility = opacity <= 0.01 ? "hidden" : "visible";
        el.style.pointerEvents = Math.abs(d) < 0.5 ? "auto" : "none";
        el.style.zIndex = String(Math.round(1000 - Math.abs(d) * 10));
      });
    };

    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(update);
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    update();

    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      cancelAnimationFrame(raf);
    };
  }, [N]);

  return (
    <>
      {/* Scroll driver — provides the scroll distance, renders nothing. */}
      <div ref={driverRef} style={{ height: `${N * 100}vh` }} aria-hidden />

      {/* Fixed stage — the camera viewport. */}
      <div
        className="fixed inset-0 z-0 h-screen overflow-hidden"
        style={{ perspective: `${PERSPECTIVE}px` }}
      >
        <div className="relative h-full w-full" style={{ transformStyle: "preserve-3d" }}>
          {panels.map((panel, i) => (
            <div
              key={i}
              ref={(el) => {
                panelRefs.current[i] = el;
              }}
              className="absolute left-1/2 top-1/2 max-h-screen w-full overflow-hidden"
              style={{
                transform: `translate(-50%, -50%) translateZ(${-i * STEP}px)`,
                opacity: i === 0 ? 1 : 0,
                willChange: "transform, opacity",
              }}
            >
              {panel}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
