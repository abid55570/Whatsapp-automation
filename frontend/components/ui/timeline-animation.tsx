"use client";

import React from "react";
import { motion, useInView, type Variants } from "framer-motion";

interface TimelineContentProps {
  children: React.ReactNode;
  animationNum: number;
  timelineRef: React.RefObject<HTMLElement | null>;
  customVariants?: Variants;
  className?: string;
  as?: keyof typeof motion;
  once?: boolean;
}

/** Reveals children using `customVariants`, triggered when `timelineRef` scrolls
 *  into view. `animationNum` is passed as the motion `custom` (stagger index). */
export const TimelineContent = ({
  children,
  animationNum,
  timelineRef,
  customVariants,
  className,
  as = "div",
  once = true,
}: TimelineContentProps) => {
  const isInView = useInView(timelineRef, { once, margin: "0px 0px -10% 0px" });
  const MotionComp = (motion as unknown as Record<string, typeof motion.div>)[
    as as string
  ] ?? motion.div;

  return (
    <MotionComp
      custom={animationNum}
      initial="hidden"
      animate={isInView ? "visible" : "hidden"}
      variants={customVariants}
      className={className}
    >
      {children}
    </MotionComp>
  );
};

export default TimelineContent;
