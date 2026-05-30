"use client";

import { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";
import { NAV_LINKS, SIGNUP_HREF } from "@/components/landing/content";
import { scrollToSection } from "@/components/landing/scroll";
import { LangSwitcher } from "@/components/LangSwitcher";

const SERIF = "'Instrument Serif', serif";

export function Navbar1() {
  const [isOpen, setIsOpen] = useState(false);
  const toggleMenu = () => setIsOpen((v) => !v);

  return (
    <div className="pointer-events-none fixed inset-x-0 top-0 z-[100] flex w-full justify-center px-4 py-5">
      <div className="pointer-events-auto relative z-10 flex w-full max-w-5xl items-center justify-between rounded-full bg-white/30 px-6 py-2.5 shadow-lg shadow-black/[0.05] ring-1 ring-white/40 backdrop-blur-xl backdrop-saturate-150">
        {/* Logo */}
        <button
          onClick={() => scrollToSection("hero")}
          className="flex items-center gap-2.5"
          aria-label="Home"
        >
          <motion.span
            aria-hidden
            className="inline-block h-8 w-8 rounded-full"
            style={{ background: "linear-gradient(135deg,#25d366,#128c7e)" }}
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            whileHover={{ rotate: 12 }}
            transition={{ duration: 0.3 }}
          />
          <span className="text-2xl leading-none tracking-tight text-slate-900" style={{ fontFamily: SERIF }}>
            Whatly
          </span>
        </button>

        {/* Desktop Navigation */}
        <nav className="hidden items-center space-x-8 md:flex">
          {NAV_LINKS.map((link) =>
            link.href ? (
              <motion.div
                key={link.label}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                whileHover={{ scale: 1.05 }}
              >
                <Link
                  href={link.href}
                  className="text-sm font-medium text-slate-700 transition-colors hover:text-slate-900"
                >
                  {link.label}
                </Link>
              </motion.div>
            ) : (
              <motion.button
                key={link.label}
                onClick={() => scrollToSection(link.section!)}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                whileHover={{ scale: 1.05 }}
                className="text-sm font-medium text-slate-700 transition-colors hover:text-slate-900"
              >
                {link.label}
              </motion.button>
            )
          )}
        </nav>

        {/* Desktop language switcher + CTA */}
        <motion.div
          className="hidden items-center gap-3 md:flex"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
        >
          <LangSwitcher variant="compact" />
          <motion.div whileHover={{ scale: 1.05 }}>
            <Link
              href={SIGNUP_HREF}
              className="accent-gradient inline-flex items-center justify-center rounded-full px-5 py-2 text-sm font-semibold text-white"
            >
              Begin Journey
            </Link>
          </motion.div>
        </motion.div>

        {/* Mobile Menu Button */}
        <motion.button
          className="flex items-center md:hidden"
          onClick={toggleMenu}
          whileTap={{ scale: 0.9 }}
          aria-label="Open menu"
        >
          <Menu className="h-6 w-6 text-slate-900" />
        </motion.button>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="pointer-events-auto fixed inset-0 z-50 bg-white px-6 pt-24 md:hidden"
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
            <motion.button
              className="absolute right-6 top-6 p-2"
              onClick={toggleMenu}
              whileTap={{ scale: 0.9 }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              aria-label="Close menu"
            >
              <X className="h-6 w-6 text-slate-900" />
            </motion.button>
            <div className="flex flex-col space-y-6">
              {NAV_LINKS.map((link, i) =>
                link.href ? (
                  <motion.div
                    key={link.label}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 + 0.1 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <Link
                      href={link.href}
                      onClick={toggleMenu}
                      className="block text-left text-base font-medium text-slate-900"
                    >
                      {link.label}
                    </Link>
                  </motion.div>
                ) : (
                  <motion.button
                    key={link.label}
                    onClick={() => {
                      scrollToSection(link.section!);
                      toggleMenu();
                    }}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 + 0.1 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="text-left text-base font-medium text-slate-900"
                  >
                    {link.label}
                  </motion.button>
                )
              )}

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.45 }}
                exit={{ opacity: 0, y: 20 }}
                className="pt-4"
              >
                <LangSwitcher variant="compact" />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                exit={{ opacity: 0, y: 20 }}
                className="pt-2"
              >
                <Link
                  href={SIGNUP_HREF}
                  onClick={toggleMenu}
                  className="accent-gradient inline-flex w-full items-center justify-center rounded-full px-5 py-3 text-base font-semibold text-white"
                >
                  Begin Journey
                </Link>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
