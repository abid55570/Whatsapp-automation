"use client";

import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface MouseFollowingEyesProps {
  /** Diameter of each eye in px. @default 44 */
  size?: number;
  /** Gap between the two eyes in px. @default 8 */
  gap?: number;
  className?: string;
}

/**
 * Two googly eyes whose pupils track the cursor anywhere on the page.
 * Adapted from the full-screen original to a compact, brand-green badge that
 * works as a logo / accent. Listens on `window` so it follows the global mouse.
 */
const MouseFollowingEyes: React.FC<MouseFollowingEyesProps> = ({
  size = 44,
  gap = 8,
  className,
}) => {
  const [mouse, setMouse] = useState({ x: -9999, y: -9999 });

  useEffect(() => {
    const onMove = (e: MouseEvent) => setMouse({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);

  return (
    <div className={cn("inline-flex items-center", className)} style={{ gap }}>
      <Eye mouseX={mouse.x} mouseY={mouse.y} size={size} />
      <Eye mouseX={mouse.x} mouseY={mouse.y} size={size} />
    </div>
  );
};

interface EyeProps {
  mouseX: number;
  mouseY: number;
  size: number;
}

const Eye: React.FC<EyeProps> = ({ mouseX, mouseY, size }) => {
  const eyeRef = useRef<HTMLDivElement>(null);
  const pupilRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = eyeRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const angle = Math.atan2(mouseY - cy, mouseX - cx);
    const maxMove = size * 0.16;
    const px = Math.cos(angle) * maxMove;
    const py = Math.sin(angle) * maxMove;
    if (pupilRef.current) {
      pupilRef.current.style.transform = `translate(${px}px, ${py}px)`;
    }
  }, [mouseX, mouseY, size]);

  const pupil = Math.round(size * 0.42);

  return (
    <div
      ref={eyeRef}
      className="relative flex items-center justify-center rounded-full border-[3px] border-[#1faa59] bg-white shadow-sm"
      style={{ height: size, width: size }}
    >
      <div
        ref={pupilRef}
        className="absolute rounded-full bg-[#0b3b27] transition-transform duration-75 ease-out"
        style={{ height: pupil, width: pupil }}
      >
        <div className="absolute bottom-[3px] right-[3px] h-1.5 w-1.5 rounded-full bg-white" />
      </div>
    </div>
  );
};

export { MouseFollowingEyes };
