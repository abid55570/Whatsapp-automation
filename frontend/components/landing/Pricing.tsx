"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Check } from "lucide-react";
import SectionHeader from "./SectionHeader";
import { PLANS, SIGNUP_HREF } from "./content";

export default function Pricing() {
  return (
    <section id="pricing" className="bg-white py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6 md:px-10 lg:px-16">
        <SectionHeader
          eyebrow="Pricing"
          heading="Honest, *simple* pricing"
          subtext="Pay only for what your shop uses. Cancel anytime — no setup fees."
        />

        <div className="mt-10 grid gap-5 md:grid-cols-3 md:gap-6">
          {PLANS.map((plan, i) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 36 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1], delay: i * 0.08 }}
              viewport={{ once: true, margin: "-60px" }}
              className="relative"
            >
              {plan.recommended && (
                <span className="accent-gradient absolute -top-3 left-1/2 z-10 -translate-x-1/2 rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-white">
                  Most Popular
                </span>
              )}
              <div
                className={`relative h-full overflow-hidden rounded-3xl border bg-white p-6 ${
                  plan.recommended ? "border-transparent shadow-soft-lg" : "border-slate-200 shadow-soft"
                }`}
              >
                {plan.recommended && (
                  <span
                    aria-hidden
                    style={{ inset: "-1px" }}
                    className="accent-gradient-animated absolute -z-10 rounded-3xl"
                  />
                )}
                {plan.recommended && (
                  <span aria-hidden className="absolute inset-[2px] -z-10 rounded-3xl bg-white" />
                )}

                <h3 className="font-display-serif text-2xl italic text-slate-900">{plan.name}</h3>
                <div className="mt-2 flex items-baseline gap-1">
                  <span className="text-4xl font-semibold text-slate-900">₹{plan.price}</span>
                  <span className="text-sm text-slate-400">/month</span>
                </div>
                <p className="mt-1 text-xs text-slate-400">
                  {plan.conv.toLocaleString("en-IN")} conversations included
                </p>

                <ul className="mt-6 space-y-2.5">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-slate-600">
                      <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-brand-500" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={SIGNUP_HREF}
                  className={`mt-6 block rounded-full py-3 text-center text-sm font-semibold transition-transform duration-300 active:scale-[0.98] ${
                    plan.recommended
                      ? "accent-gradient text-white hover:scale-[1.02]"
                      : "border border-slate-200 text-slate-900 hover:bg-slate-50"
                  }`}
                >
                  Start free trial
                </Link>
              </div>
            </motion.div>
          ))}
        </div>

        {/* AI add-on strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true, margin: "-60px" }}
          className="mx-auto mt-6 flex max-w-2xl flex-col items-center gap-3 rounded-3xl border border-slate-200 bg-[#f5faf6] p-6 text-center sm:flex-row sm:text-left"
        >
          <span className="text-3xl">🤖</span>
          <div className="flex-1">
            <div className="font-semibold text-slate-900">AI Add-on</div>
            <p className="text-sm text-slate-500">
              Smart-reply fallback · Auto-translate to the customer’s language · 1,500 AI replies/mo
            </p>
          </div>
          <span className="font-display-serif text-2xl italic text-gradient">+₹699/mo</span>
        </motion.div>

        <p className="mt-6 text-center text-xs text-slate-400">
          All prices excl. GST · UPI / cards / net banking via Razorpay · 14-day free trial · No commitment
        </p>
      </div>
    </section>
  );
}
