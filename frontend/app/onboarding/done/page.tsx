"use client";

import { CheckCircle2, MessageCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Button } from "@/components/ui/Button";
import { useMyBusiness } from "@/lib/queries";

export default function OnboardingDonePage() {
  const router = useRouter();
  const { data: business } = useMyBusiness();

  // Auto-redirect to dashboard after a few seconds
  useEffect(() => {
    const t = setTimeout(() => {
      router.replace("/dashboard");
    }, 4000);
    return () => clearTimeout(t);
  }, [router]);

  const trialDays = business?.subscription?.days_remaining_in_trial ?? 14;

  return (
    <div className="animate-fade-in text-center py-8">
      <div className="inline-flex w-24 h-24 rounded-full bg-emerald-100 items-center justify-center mb-6 animate-slide-up">
        <CheckCircle2 className="h-14 w-14 text-emerald-500" strokeWidth={2} />
      </div>

      <h1 className="text-3xl font-bold text-slate-900 mb-2">
        You're all set! 🎉
      </h1>
      <p className="text-slate-600 mb-8">
        {business?.name ?? "Your business"} is ready to receive WhatsApp
        messages on autopilot.
      </p>

      <div className="space-y-3 text-left max-w-sm mx-auto mb-8">
        <div className="card flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
          <span className="text-sm text-slate-700">
            Profile created · {business?.business_type ?? ""}
          </span>
        </div>
        <div className="card flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
          <span className="text-sm text-slate-700">
            WhatsApp{" "}
            {business?.whatsapp_connected ? "connected" : "ready to connect"}
          </span>
        </div>
        <div className="card flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />
          <span className="text-sm text-slate-700">
            {business?.intent_count ?? 12} auto-replies configured
          </span>
        </div>
        <div className="card flex items-center gap-3">
          <span className="text-2xl">🎁</span>
          <span className="text-sm text-slate-700">
            <span className="font-semibold">{trialDays} days</span> of free
            trial remaining
          </span>
        </div>
      </div>

      <Button onClick={() => router.replace("/dashboard")} fullWidth size="lg">
        <MessageCircle className="h-5 w-5" />
        Go to Dashboard
      </Button>
      <p className="text-xs text-slate-400 mt-3">
        Redirecting automatically...
      </p>
    </div>
  );
}
