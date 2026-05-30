"use client";
import Link from "next/link";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Sparkles as SparklesComp } from "@/components/ui/sparkles";
import { TimelineContent } from "@/components/ui/timeline-animation";
import { VerticalCutReveal } from "@/components/ui/vertical-cut-reveal";
import { cn } from "@/lib/utils";
import NumberFlow from "@number-flow/react";
import { motion } from "framer-motion";
import { useRef, useState } from "react";
import { PLANS, SIGNUP_HREF } from "@/components/landing/content";

const PricingSwitch = ({ onSwitch }: { onSwitch: (value: string) => void }) => {
  const [selected, setSelected] = useState("0");

  const handleSwitch = (value: string) => {
    setSelected(value);
    onSwitch(value);
  };

  return (
    <div className="flex justify-center">
      <div className="relative z-10 mx-auto flex w-fit rounded-full border border-white/10 bg-neutral-900 p-1">
        {[
          { v: "0", label: "Monthly" },
          { v: "1", label: "Yearly" },
        ].map(({ v, label }) => (
          <button
            key={v}
            onClick={() => handleSwitch(v)}
            className={cn(
              "relative z-10 h-10 w-fit rounded-full px-3 py-1 font-medium transition-colors sm:px-6 sm:py-2",
              selected === v ? "text-white" : "text-gray-300"
            )}
          >
            {selected === v && (
              <motion.span
                layoutId="switch"
                className="absolute left-0 top-0 h-10 w-full rounded-full border-4 border-[#1faa59] bg-gradient-to-t from-[#1faa59] to-[#25d366] shadow-sm shadow-[#1faa59]"
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
              />
            )}
            <span className="relative flex items-center gap-2">
              {label}
              {v === "1" && (
                <span className="rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-semibold">
                  2 mo free
                </span>
              )}
            </span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default function PricingSection() {
  const [isYearly, setIsYearly] = useState(false);
  const pricingRef = useRef<HTMLDivElement>(null);

  const revealVariants = {
    visible: (i: number) => ({
      y: 0,
      opacity: 1,
      filter: "blur(0px)",
      transition: { delay: i * 0.4, duration: 0.5 },
    }),
    hidden: { filter: "blur(10px)", y: -20, opacity: 0 },
  };

  const togglePricingPeriod = (value: string) => setIsYearly(Number.parseInt(value) === 1);

  return (
    <div
      id="pricing"
      className="relative mx-auto overflow-x-hidden bg-[#06140e] pb-20"
      ref={pricingRef}
    >
      <TimelineContent
        animationNum={4}
        timelineRef={pricingRef}
        customVariants={revealVariants}
        className="absolute top-0 h-96 w-screen overflow-hidden [mask-image:radial-gradient(50%_50%,white,transparent)]"
      >
        <div className="absolute bottom-0 left-0 right-0 top-0 bg-[linear-gradient(to_right,#ffffff2c_1px,transparent_1px),linear-gradient(to_bottom,#3a3a3a01_1px,transparent_1px)] bg-[size:70px_80px]" />
        <SparklesComp
          density={280}
          speed={1}
          color="#FFFFFF"
          className="absolute inset-x-0 bottom-0 h-full w-full [mask-image:radial-gradient(50%_50%,white,transparent_85%)]"
        />
      </TimelineContent>

      <TimelineContent
        animationNum={5}
        timelineRef={pricingRef}
        customVariants={revealVariants}
        className="absolute left-0 top-[-114px] z-0 flex h-[113.625vh] w-full flex-none flex-col flex-nowrap content-start items-start justify-start gap-2.5 overflow-hidden p-0"
      >
        <div className="relative w-full">
          <div
            className="absolute left-[-568px] right-[-568px] top-0 h-[2053px] flex-none rounded-full"
            style={{ border: "200px solid #128c7e", filter: "blur(92px)", WebkitFilter: "blur(92px)" }}
          />
          <div
            className="absolute left-[-568px] right-[-568px] top-0 h-[2053px] flex-none rounded-full"
            style={{ border: "200px solid #1faa59", filter: "blur(92px)", WebkitFilter: "blur(92px)" }}
          />
        </div>
      </TimelineContent>

      <article className="relative z-50 mx-auto mb-6 max-w-3xl space-y-2 pt-32 text-center">
        <h2 className="text-4xl font-medium text-white">
          <VerticalCutReveal
            splitBy="words"
            staggerDuration={0.15}
            staggerFrom="first"
            reverse
            containerClassName="justify-center"
            transition={{ type: "spring", stiffness: 250, damping: 40, delay: 0 }}
          >
            Plans that work best for your shop
          </VerticalCutReveal>
        </h2>

        <TimelineContent
          as="p"
          animationNum={0}
          timelineRef={pricingRef}
          customVariants={revealVariants}
          className="text-gray-300"
        >
          Trusted by shops across India. Pick what fits how you sell — upgrade
          anytime.
        </TimelineContent>

        <TimelineContent
          as="div"
          animationNum={1}
          timelineRef={pricingRef}
          customVariants={revealVariants}
        >
          <PricingSwitch onSwitch={togglePricingPeriod} />
        </TimelineContent>
      </article>

      <div
        className="absolute left-[10%] right-[10%] top-0 z-0 h-full w-[80%]"
        style={{
          backgroundImage: "radial-gradient(circle at center, #1faa59 0%, transparent 70%)",
          opacity: 0.5,
          mixBlendMode: "multiply",
        }}
      />

      <div className="mx-auto grid max-w-5xl gap-4 px-4 py-6 md:grid-cols-3">
        {PLANS.map((plan, index) => {
          const yearly = plan.price * 10;
          return (
            <TimelineContent
              key={plan.name}
              as="div"
              animationNum={2 + index}
              timelineRef={pricingRef}
              customVariants={revealVariants}
            >
              <Card
                className={`relative border-neutral-800 text-white ${
                  plan.recommended
                    ? "z-20 bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 shadow-[0px_-13px_300px_0px_#0b6b3a]"
                    : "z-10 bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900"
                }`}
              >
                {plan.recommended && (
                  <span className="absolute right-5 top-5 rounded-full bg-gradient-to-t from-[#1faa59] to-[#25d366] px-3 py-1 text-xs font-semibold text-white">
                    Most popular
                  </span>
                )}
                <CardHeader className="text-left">
                  <h3 className="mb-2 text-3xl">{plan.name}</h3>
                  <div className="flex items-baseline">
                    <span className="text-4xl font-semibold">
                      <NumberFlow
                        value={isYearly ? yearly : plan.price}
                        format={{ style: "currency", currency: "INR", maximumFractionDigits: 0 }}
                        className="text-4xl font-semibold"
                      />
                    </span>
                    <span className="ml-1 text-gray-300">/{isYearly ? "year" : "month"}</span>
                  </div>
                  <p className="mb-4 text-sm text-gray-300">
                    {plan.conv.toLocaleString("en-IN")} conversations / month
                  </p>
                </CardHeader>

                <CardContent className="pt-0">
                  <Link
                    href={SIGNUP_HREF}
                    className={`mb-6 block w-full rounded-xl p-4 text-center text-xl ${
                      plan.recommended
                        ? "border border-[#25d366] bg-gradient-to-t from-[#1faa59] to-[#25d366] text-white shadow-lg shadow-[#0b6b3a]"
                        : "border border-neutral-800 bg-gradient-to-t from-neutral-950 to-neutral-600 text-white shadow-lg shadow-neutral-900"
                    }`}
                  >
                    Start free trial
                  </Link>

                  <div className="space-y-3 border-t border-neutral-700 pt-4">
                    <h4 className="mb-3 text-base font-medium">What&apos;s included:</h4>
                    <ul className="space-y-2">
                      {plan.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center gap-2">
                          <span className="grid h-2.5 w-2.5 place-content-center rounded-full bg-[#25d366]" />
                          <span className="text-sm text-gray-300">{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </TimelineContent>
          );
        })}
      </div>
    </div>
  );
}
