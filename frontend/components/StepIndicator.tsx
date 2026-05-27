"use client";

import { Check } from "lucide-react";

import { cn } from "@/lib/utils";
import type { OnboardingStep } from "@/types/api";

interface Step {
  key: OnboardingStep | "verify";
  label: string;
}

const STEPS: Step[] = [
  { key: "verify", label: "Verify" },
  { key: "create_business", label: "Business" },
  { key: "connect_whatsapp", label: "WhatsApp" },
  { key: "configure_intents", label: "Replies" },
];

interface Props {
  currentStep: OnboardingStep | "verify" | undefined;
}

export function StepIndicator({ currentStep }: Props) {
  // Determine progress index
  let activeIdx = 0;
  if (currentStep === "done") activeIdx = STEPS.length;
  else activeIdx = STEPS.findIndex((s) => s.key === currentStep);
  if (activeIdx < 0) activeIdx = 0;

  return (
    <div className="flex items-center justify-between">
      {STEPS.map((step, idx) => {
        const completed = idx < activeIdx;
        const current = idx === activeIdx;
        return (
          <div key={step.key} className="flex items-center flex-1 last:flex-none">
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition",
                  completed && "bg-brand-500 text-white",
                  current && "bg-brand-100 text-brand-700 ring-2 ring-brand-500",
                  !completed && !current && "bg-slate-100 text-slate-400",
                )}
              >
                {completed ? <Check className="h-4 w-4" /> : idx + 1}
              </div>
              <span
                className={cn(
                  "text-[10px] mt-1 font-medium",
                  completed && "text-brand-600",
                  current && "text-brand-700",
                  !completed && !current && "text-slate-400",
                )}
              >
                {step.label}
              </span>
            </div>
            {idx < STEPS.length - 1 && (
              <div
                className={cn(
                  "flex-1 h-0.5 mx-1 mb-4 rounded-full transition",
                  idx < activeIdx ? "bg-brand-500" : "bg-slate-200",
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
