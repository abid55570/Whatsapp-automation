"use client";

import { motion } from "framer-motion";
import React from "react";

interface AnimatedGradientBackgroundProps {
  startingGap?: number;
  Breathing?: boolean;
  gradientColors?: string[];
  gradientStops?: number[];
  animationSpeed?: number;
  breathingRange?: number;
  containerStyle?: React.CSSProperties;
  containerClassName?: string;
  topOffset?: number;
}

/**
 * AnimatedGradientBackground — customizable animated radial gradient with a
 * subtle breathing effect. Entrance animation via framer-motion; the live
 * gradient is driven by raw CSS in a rAF loop.
 */
const AnimatedGradientBackground: React.FC<AnimatedGradientBackgroundProps> = ({
  startingGap = 125,
  Breathing = false,
  gradientColors = [
    "#0A0A0A",
    "#2979FF",
    "#FF80AB",
    "#FF6D00",
    "#FFD600",
    "#00E676",
    "#3D5AFE",
  ],
  gradientStops = [35, 50, 60, 70, 80, 90, 100],
  animationSpeed = 0.02,
  breathingRange = 5,
  containerStyle = {},
  topOffset = 0,
  containerClassName = "",
}) => {
  if (gradientColors.length !== gradientStops.length) {
    throw new Error(
      `GradientColors and GradientStops must have the same length.
     Received gradientColors length: ${gradientColors.length},
     gradientStops length: ${gradientStops.length}`
    );
  }

  // The gradient is painted ONCE (no per-frame repaint). The subtle "breathing"
  // is done with a GPU-composited transform animation instead — same look, but
  // it no longer forces a full-screen repaint every frame.
  const gradientStopsString = gradientStops
    .map((stop, index) => `${gradientColors[index]} ${stop}%`)
    .join(", ");
  const gradient = `radial-gradient(${startingGap}% ${startingGap + topOffset}% at 50% 20%, ${gradientStopsString})`;

  return (
    <motion.div
      key="animated-gradient-background"
      initial={{ opacity: 0, scale: 1.5 }}
      animate={{
        opacity: 1,
        scale: 1,
        transition: { duration: 2, ease: [0.25, 0.1, 0.25, 1] },
      }}
      className={`absolute inset-0 overflow-hidden ${containerClassName}`}
    >
      <div
        style={{ background: gradient, ...containerStyle }}
        className={`absolute inset-0 ${Breathing ? "animate-bg-breathe" : ""}`}
      />
    </motion.div>
  );
};

export default AnimatedGradientBackground;
