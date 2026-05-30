"use client";
import React, { useState, useEffect, useRef } from "react";

interface SpotlightBackgroundProps {
  /** Spotlight color as an rgba/hex string. */
  color?: string;
  /** Idle (expanded) diameter in px. */
  idleSize?: number;
  /** Moving (shrunk) diameter in px. */
  movingSize?: number;
  className?: string;
}

const SpotlightBackground = ({
  color = "rgba(37,211,102,0.45)",
  idleSize = 300,
  movingSize = 230,
  className = "",
}: SpotlightBackgroundProps) => {
  const [mouse, setMouse] = useState({ x: -1000, y: -1000 });
  const [isMoving, setIsMoving] = useState(false);
  const moveTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMouse({ x: e.clientX, y: e.clientY });
      setIsMoving(true);

      if (moveTimeout.current) clearTimeout(moveTimeout.current);
      moveTimeout.current = setTimeout(() => setIsMoving(false), 150);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      if (moveTimeout.current) clearTimeout(moveTimeout.current);
    };
  }, []);

  return (
    <div className={`pointer-events-none absolute inset-0 h-full w-full overflow-hidden ${className}`}>
      <div
        className="absolute rounded-full pointer-events-none transition-all duration-300 ease-out"
        style={{
          left: mouse.x,
          top: mouse.y,
          width: isMoving ? movingSize : idleSize,
          height: isMoving ? movingSize : idleSize,
          transform: "translate(-50%, -50%)",
          background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
        }}
      />
    </div>
  );
};

export default SpotlightBackground;
