"use client";
import React, { useEffect, useRef } from "react";

interface SpotlightBackgroundProps {
  /** Spotlight color as an rgba/hex string. */
  color?: string;
  /** Idle (expanded) diameter in px. */
  idleSize?: number;
  /** Moving (shrunk) diameter in px. */
  movingSize?: number;
  className?: string;
}

/**
 * Cursor spotlight. Position + size are driven entirely through a single
 * GPU-composited `transform` (translate3d + scale) updated in one rAF loop —
 * no React re-renders per mousemove and no layout-triggering width/left
 * animation, so it stays glassy-smooth.
 */
const SpotlightBackground = ({
  color = "rgba(37,211,102,0.45)",
  idleSize = 300,
  movingSize = 230,
  className = "",
}: SpotlightBackgroundProps) => {
  const dotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = dotRef.current;
    if (el === null) return;

    let x = -1000;
    let y = -1000;
    let tx = -1000;
    let ty = -1000;
    let s = 1;
    const movingScale = movingSize / idleSize;
    let ts = 1;
    let moving = false;
    let moveTimeout: ReturnType<typeof setTimeout> | null = null;
    let raf = 0;
    let running = false;

    const render = () => {
      el.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%) scale(${s})`;
    };

    const tick = () => {
      // ease position + size toward their targets
      x += (tx - x) * 0.2;
      y += (ty - y) * 0.2;
      ts = moving ? movingScale : 1;
      s += (ts - s) * 0.18;
      render();
      // pause the loop once it has visually settled; it restarts on next move
      if (Math.abs(tx - x) < 0.3 && Math.abs(ty - y) < 0.3 && Math.abs(ts - s) < 0.003) {
        running = false;
        return;
      }
      raf = requestAnimationFrame(tick);
    };

    const kick = () => {
      if (!running) {
        running = true;
        raf = requestAnimationFrame(tick);
      }
    };

    const onMove = (e: MouseEvent) => {
      tx = e.clientX;
      ty = e.clientY;
      el.style.opacity = "1";
      moving = true;
      if (moveTimeout) clearTimeout(moveTimeout);
      moveTimeout = setTimeout(() => {
        moving = false;
        kick();
      }, 150);
      kick();
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    return () => {
      window.removeEventListener("mousemove", onMove);
      if (moveTimeout) clearTimeout(moveTimeout);
      cancelAnimationFrame(raf);
    };
  }, [idleSize, movingSize]);

  return (
    <div className={`pointer-events-none absolute inset-0 h-full w-full overflow-hidden ${className}`}>
      <div
        ref={dotRef}
        className="pointer-events-none absolute left-0 top-0 rounded-full opacity-0 will-change-transform"
        style={{
          width: idleSize,
          height: idleSize,
          background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
        }}
      />
    </div>
  );
};

export default SpotlightBackground;
