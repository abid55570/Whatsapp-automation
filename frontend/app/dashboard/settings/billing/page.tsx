"use client";

import {
  AlertCircle,
  ArrowLeft,
  Check,
  CreditCard,
  ExternalLink,
  Loader2,
  Sparkles,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { apiErrorMessage } from "@/lib/api";
import {
  useCancelSubscription,
  useDisableAiAddon,
  useDisableTaxPack,
  useEnableAiAddon,
  useEnableTaxPack,
  useGstSettings,
  useMyBusiness,
  useUpgradePlan,
} from "@/lib/queries";
import { cn } from "@/lib/utils";

interface Plan {
  key: "starter" | "growth" | "pro";
  name: string;
  price_rupees: number;
  conversations: number;
  features: string[];
  recommended?: boolean;
}

const PLANS: Plan[] = [
  {
    key: "starter",
    name: "Starter",
    price_rupees: 399,
    conversations: 1000,
    features: [
      "Auto-reply (6 languages)",
      "1,000 conversations/month",
      "FAQ bot",
      "Inbox",
      "Sheet sync",
    ],
  },
  {
    key: "growth",
    name: "Growth",
    price_rupees: 999,
    conversations: 3000,
    recommended: true,
    features: [
      "Everything in Starter",
      "3,000 conversations/month",
      "Orders + Pickup flow",
      "Bookings + Calendar",
      "Razorpay payment links",
      "Analytics",
    ],
  },
  {
    key: "pro",
    name: "Pro",
    price_rupees: 1999,
    conversations: 6000,
    features: [
      "Everything in Growth",
      "6,000 conversations/month",
      "Broadcasts",
      "API access",
      "Webhooks",
      "Priority support",
    ],
  },
];

function formatRupees(n: number): string {
  return `₹${n.toLocaleString("en-IN")}`;
}

export default function BillingPage() {
  const router = useRouter();
  const { data: business, isLoading } = useMyBusiness();
  const upgrade = useUpgradePlan();
  const cancel = useCancelSubscription();
  const [pendingPlan, setPendingPlan] = useState<string | null>(null);

  async function handleUpgrade(plan: Plan["key"]) {
    setPendingPlan(plan);
    try {
      const result = await upgrade.mutateAsync({ plan });
      if (result.short_url) {
        toast.success("Redirecting to Razorpay...");
        window.location.href = result.short_url;
      } else {
        toast.error("Razorpay didn't return a checkout URL");
      }
    } catch (err) {
      toast.error(apiErrorMessage(err));
      setPendingPlan(null);
    }
  }

  async function handleCancel() {
    if (!confirm("Cancel subscription at end of billing period?")) return;
    try {
      await cancel.mutateAsync();
      toast.success("Subscription will end at next billing date.");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  if (isLoading || !business) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  const sub = business.subscription;
  const onTrial = sub?.plan === "trial";
  const frozen = sub?.status === "frozen";
  const active = sub?.status === "active";

  return (
    <div className="animate-fade-in pb-8">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-900">Billing</h1>
            <p className="text-xs text-slate-500">
              Pick a plan that fits your shop
            </p>
          </div>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {/* Current plan banner */}
        {sub && (
          <div
            className={cn(
              "card flex items-center gap-3",
              frozen
                ? "bg-red-50 border border-red-200"
                : active
                  ? "bg-emerald-50 border border-emerald-200"
                  : "bg-brand-50 border border-brand-200",
            )}
          >
            {frozen ? (
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0" />
            ) : (
              <Sparkles
                className={cn(
                  "h-5 w-5 flex-shrink-0",
                  active ? "text-emerald-600" : "text-brand-600",
                )}
              />
            )}
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm text-slate-900">
                {frozen
                  ? "Trial ended"
                  : onTrial
                    ? `Trial · ${sub.days_remaining_in_trial ?? 0} days left`
                    : `Active · ${sub.plan?.toUpperCase()}`}
              </p>
              <p className="text-xs text-slate-600">
                {sub.conversations_used}/{sub.conversations_included}{" "}
                conversations used
              </p>
            </div>
          </div>
        )}

        {/* Plan cards */}
        <div className="space-y-3">
          {PLANS.map((p) => {
            const isCurrent = sub?.plan === p.key;
            const upgrading = pendingPlan === p.key;
            return (
              <div
                key={p.key}
                className={cn(
                  "card relative",
                  p.recommended && "ring-2 ring-brand-500 border-brand-500",
                )}
              >
                {p.recommended && (
                  <span className="absolute -top-2 left-4 bg-brand-500 text-white text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full">
                    Recommended
                  </span>
                )}
                <div className="flex items-baseline justify-between mb-1">
                  <h3 className="font-bold text-lg text-slate-900">
                    {p.name}
                  </h3>
                  <div className="text-right">
                    <span className="text-2xl font-bold text-slate-900">
                      {formatRupees(p.price_rupees)}
                    </span>
                    <span className="text-xs text-slate-500">/mo</span>
                  </div>
                </div>
                <p className="text-xs text-slate-600 mb-3">
                  {p.conversations.toLocaleString("en-IN")} conversations included
                </p>
                <ul className="space-y-1.5 mb-4">
                  {p.features.map((f, i) => (
                    <li
                      key={i}
                      className="flex items-start gap-2 text-sm text-slate-700"
                    >
                      <Check className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
                {isCurrent && active ? (
                  <div className="flex items-center justify-center gap-2 py-2 text-sm font-medium text-emerald-700 bg-emerald-50 rounded-xl">
                    <Check className="h-4 w-4" />
                    Current plan
                  </div>
                ) : (
                  <Button
                    onClick={() => handleUpgrade(p.key)}
                    loading={upgrading}
                    fullWidth
                    variant={p.recommended ? "primary" : "secondary"}
                  >
                    <CreditCard className="h-4 w-4" />
                    {onTrial || frozen
                      ? `Upgrade to ${p.name}`
                      : `Switch to ${p.name}`}
                    <ExternalLink className="h-3 w-3" />
                  </Button>
                )}
              </div>
            );
          })}
        </div>

        {/* AI add-on */}
        <AiAddonCard
          business={business}
          paidPlanActive={active && !onTrial}
        />

        {/* Tax Pack add-on */}
        <TaxPackCard paidPlanActive={active && !onTrial} />

        {/* placeholder section removed below */}
        <div className="hidden">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🤖</span>
            <div className="flex-1">
              <h3 className="font-bold text-slate-900 mb-1">
                AI Add-on · ₹699/mo
              </h3>
              <p className="text-xs text-slate-600 mb-2">
                Smart replies · Multilingual auto-translate · Voice notes ·
                Summaries
              </p>
              <p className="text-xs text-indigo-700 font-medium">
                Coming soon — add to any paid plan
              </p>
            </div>
          </div>
        </div>

        {/* Cancel */}
        {active && (
          <button
            onClick={handleCancel}
            className="w-full text-sm text-red-600 hover:text-red-700 py-3 active:scale-95"
          >
            Cancel subscription
          </button>
        )}

        <p className="text-[11px] text-center text-slate-400 leading-relaxed">
          Payments processed by Razorpay · UPI, cards, net banking accepted ·
          Cancel anytime
        </p>
      </div>
    </div>
  );
}


function TaxPackCard({ paidPlanActive }: { paidPlanActive: boolean }) {
  const { data: gst } = useGstSettings();
  const enable = useEnableTaxPack();
  const disable = useDisableTaxPack();
  const isOn = Boolean(gst?.tax_pack_enabled);

  async function handleToggle() {
    if (!paidPlanActive) {
      toast.error("Upgrade to a paid plan first");
      return;
    }
    try {
      if (isOn) {
        await disable.mutateAsync();
        toast.success("Tax Pack disabled");
      } else {
        await enable.mutateAsync();
        toast.success("Tax Pack enabled · GSTR-1, GSTR-3B, ITR exports unlocked");
      }
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  const busy = enable.isPending || disable.isPending;

  return (
    <div
      className={cn(
        "rounded-xl border p-4",
        isOn
          ? "bg-gradient-to-br from-emerald-50 to-brand-50 border-emerald-300"
          : "bg-white border-slate-200",
      )}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <span className="text-2xl">🧾</span>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-slate-900 mb-1">
              Tax Pack · ₹299/mo
            </h3>
            <p className="text-xs text-slate-600">
              GSTR-1 JSON · GSTR-3B summary · ITR P&L · Purchase register ·
              Monthly CA email
            </p>
          </div>
        </div>
        <button
          onClick={handleToggle}
          disabled={busy}
          className={cn(
            "flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-semibold transition disabled:opacity-50 min-h-[32px]",
            isOn
              ? "bg-slate-900 text-white"
              : "bg-emerald-600 hover:bg-emerald-700 text-white",
          )}
        >
          {busy ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : isOn ? (
            "Disable"
          ) : (
            "Enable"
          )}
        </button>
      </div>
      {isOn && (
        <div className="text-xs text-emerald-700 font-medium flex items-center gap-1">
          <Check className="h-3 w-3" />
          Active · visit Tax Filing Center to download exports
        </div>
      )}
    </div>
  );
}


function AiAddonCard({
  business,
  paidPlanActive,
}: {
  business: ReturnType<typeof useMyBusiness>["data"];
  paidPlanActive: boolean;
}) {
  const enable = useEnableAiAddon();
  const disable = useDisableAiAddon();
  const sub = business?.subscription;
  const isOn = Boolean(sub?.ai_addon_enabled);

  async function handleToggle() {
    if (!paidPlanActive) {
      toast.error("Upgrade to a paid plan first");
      return;
    }
    try {
      if (isOn) {
        await disable.mutateAsync();
        toast.success("AI add-on disabled");
      } else {
        await enable.mutateAsync();
        toast.success("AI add-on enabled · 1500 AI replies/month");
      }
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <div
      className={cn(
        "card bg-gradient-to-br from-indigo-50 to-purple-50 border",
        isOn ? "border-indigo-500 ring-2 ring-indigo-500/30" : "border-indigo-200",
      )}
    >
      <div className="flex items-start gap-3 mb-3">
        <span className="text-3xl">🤖</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-bold text-slate-900">AI Add-on</h3>
            <span className="text-sm font-bold text-slate-900">₹699/mo</span>
          </div>
          <p className="text-xs text-slate-600 mt-0.5">
            Smart replies · Multi-lang auto-translate · 1,500 AI replies/mo
          </p>
        </div>
      </div>
      <ul className="space-y-1 text-xs text-slate-700 mb-3 pl-2">
        <li>• AI answers when no FAQ matches</li>
        <li>• Auto-translate replies to customer's language</li>
        <li>• Reply in Hindi / Hinglish / Bengali / Urdu</li>
      </ul>

      {isOn && sub ? (
        <>
          <div className="text-xs text-slate-600 mb-3">
            <span className="font-semibold text-indigo-700">
              {sub.ai_replies_used}/{sub.ai_replies_included}
            </span>{" "}
            AI replies used this month
          </div>
          <Button
            onClick={handleToggle}
            loading={disable.isPending}
            fullWidth
            variant="secondary"
          >
            Disable AI add-on
          </Button>
        </>
      ) : (
        <Button
          onClick={handleToggle}
          loading={enable.isPending}
          fullWidth
          variant="primary"
          disabled={!paidPlanActive}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          {paidPlanActive ? "Enable AI add-on" : "Upgrade first to enable AI"}
        </Button>
      )}
    </div>
  );
}
