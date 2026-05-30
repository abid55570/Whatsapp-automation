"use client";

import { cn } from "@/lib/utils";
import React from "react";

interface GridVignetteBackgroundProps {
  size?: number;
  x?: number;
  y?: number;
  horizontalVignetteSize?: number;
  verticalVignetteSize?: number;
  intensity?: number;
  /** Grid line color. */
  lineColor?: string;
}

export function GridVignetteBackground({
  className,
  size = 48,
  x = 50,
  y = 50,
  horizontalVignetteSize = 100,
  verticalVignetteSize = 100,
  intensity = 0,
  lineColor = "#1faa59",
  ...props
}: React.ComponentProps<"div"> & GridVignetteBackgroundProps) {
  const mask = `radial-gradient(ellipse ${horizontalVignetteSize}% ${verticalVignetteSize}% at ${x}% ${y}%, black ${
    100 - intensity
  }%, transparent 100%)`;

  return (
    <div
      className={cn("absolute inset-0", className)}
      style={{
        backgroundImage: `linear-gradient(to right, ${lineColor}, transparent 1px), linear-gradient(to bottom, ${lineColor}, transparent 1px)`,
        backgroundSize: `${size}px ${size}px`,
        maskImage: mask,
        WebkitMaskImage: mask,
      }}
      {...props}
    />
  );
}

export default GridVignetteBackground;
