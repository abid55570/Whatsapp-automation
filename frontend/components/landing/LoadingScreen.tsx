"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LOADING_WORDS } from "./content";

interface LoadingScreenProps {
  onComplete: () => void;
}

const DURATION = 2700;

export default function LoadingScreen({ onComplete }: LoadingScreenProps) {
  const [count, setCount] = useState(0);
  const [wordIndex, setWordIndex] = useState(0);
  const completedRef = useRef(false);

  useEffect(() => {
    let raf = 0;
    let start: number | null = null;

    const tick = (now: number) => {
      if (start === null) start = now;
      const progress = Math.min((now - start) / DURATION, 1);
      setCount(Math.round(progress * 100));
      if (progress < 1) {
        raf = requestAnimationFrame(tick);
      } else if (!completedRef.current) {
        completedRef.current = true;
        window.setTimeout(onComplete, 400);
      }
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [onComplete]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      setWordIndex((i) => (i + 1) % LOADING_WORDS.length);
    }, 900);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      className="fixed inset-0 z-[9999] bg-white"
      exit={{ opacity: 0 }}
      transition={{ duration: 0.6, ease: "easeInOut" }}
    >
      <motion.span
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="absolute left-6 top-6 text-xs uppercase tracking-[0.3em] text-slate-400 md:left-10 md:top-10"
      >
        WhatsApp Auto
      </motion.span>

      <div className="flex h-full items-center justify-center">
        <AnimatePresence mode="wait">
          <motion.h2
            key={wordIndex}
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: -20, opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            className="font-display-serif text-4xl italic text-slate-800 md:text-6xl lg:text-7xl"
          >
            {LOADING_WORDS[wordIndex]}
          </motion.h2>
        </AnimatePresence>
      </div>

      <div className="absolute bottom-8 right-6 md:bottom-12 md:right-10">
        <span
          className="font-display-serif text-gradient text-6xl md:text-8xl lg:text-9xl"
          style={{ fontVariantNumeric: "tabular-nums" }}
        >
          {String(count).padStart(3, "0")}
        </span>
      </div>

      <div className="absolute inset-x-0 bottom-0 h-[3px] bg-slate-100">
        <div
          className="accent-gradient h-full origin-left"
          style={{
            transform: `scaleX(${count / 100})`,
            boxShadow: "0 0 8px rgba(74, 222, 128, 0.4)",
          }}
        />
      </div>
    </motion.div>
  );
}
