"use client";

import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import { Navbar1 } from "@/components/ui/navbar1";
import SmoothScroll from "./SmoothScroll";
import LoadingScreen from "./LoadingScreen";
import PhoneJourney from "./PhoneJourney";
import Marquee from "./Marquee";
import BentoWorks from "./BentoWorks";
import Testimonials from "./Testimonials";
import HowItWorks from "./HowItWorks";
import Stats from "./Stats";
import PricingSection from "@/components/ui/pricing-section-4";
import FAQ from "./FAQ";
import HoverFooter from "./HoverFooter";

/** Whatly landing — a single phone moves in 3D through the hero + use-case
 *  journey, then the supporting sections follow. */
export default function Landing() {
  const [isLoading, setIsLoading] = useState(true);

  return (
    <div className="bg-white font-sans text-slate-900">
      <SmoothScroll />
      <AnimatePresence>
        {isLoading && <LoadingScreen onComplete={() => setIsLoading(false)} />}
      </AnimatePresence>

      <Navbar1 />
      <main>
        {/* 3D phone hero + use-case journey — unchanged */}
        <PhoneJourney />

        {/* New components, beneath the mockup flow */}
        <Marquee text="WHATSAPP AUTOMATION" />
        <BentoWorks />
        <Testimonials />

        <HowItWorks />
        <Stats />
        <PricingSection />
        <FAQ />
        <HoverFooter />
      </main>
    </div>
  );
}
