"use client";

import { ArrowRight, ShieldCheck } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { MetaSignupButton } from "@/components/MetaSignupButton";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { apiErrorMessage } from "@/lib/api";
import { useConnectWhatsApp } from "@/lib/queries";

const META_APP_ID = process.env.NEXT_PUBLIC_META_APP_ID || "";
const META_CONFIG_ID = process.env.NEXT_PUBLIC_META_EMBEDDED_SIGNUP_CONFIG_ID || "";

export default function ConnectWhatsAppPage() {
  const router = useRouter();
  const [showManual, setShowManual] = useState(false);
  const [phoneNumberId, setPhoneNumberId] = useState("");
  const [accessToken, setAccessToken] = useState("");
  const [displayPhone, setDisplayPhone] = useState("");
  const [businessAccountId, setBusinessAccountId] = useState("");

  const mutation = useConnectWhatsApp();
  const embeddedSignupReady = Boolean(META_APP_ID && META_CONFIG_ID);

  async function handleManualSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await mutation.mutateAsync({
        phone_number_id: phoneNumberId.trim(),
        access_token: accessToken.trim(),
        display_phone: displayPhone.trim() || undefined,
        business_account_id: businessAccountId.trim() || undefined,
      });
      toast.success("WhatsApp connected!");
      router.replace("/onboarding/intents");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  function handleMetaSuccess() {
    router.replace("/onboarding/intents");
  }

  return (
    <div className="animate-fade-in">
      <div className="inline-flex w-12 h-12 rounded-2xl bg-brand-500 text-white text-2xl items-center justify-center mb-4 shadow-soft">
        🔗
      </div>
      <h1 className="text-2xl font-bold text-slate-900 mb-1">
        Connect WhatsApp Business
      </h1>
      <p className="text-slate-600 text-sm mb-6">
        One-tap setup via Meta. We never see your password.
      </p>

      {/* Embedded Signup (preferred path) */}
      {embeddedSignupReady && !showManual && (
        <>
          <MetaSignupButton
            appId={META_APP_ID}
            configId={META_CONFIG_ID}
            onSuccess={handleMetaSuccess}
          />

          <div className="flex items-center gap-2 text-xs text-slate-500 mt-6 justify-center">
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
            <span>Token encrypted at rest · Never shared</span>
          </div>

          <button
            onClick={() => setShowManual(true)}
            className="text-sm text-slate-500 hover:text-slate-700 mt-4 block mx-auto underline"
          >
            Or enter credentials manually
          </button>
        </>
      )}

      {/* Manual fallback (dev / when embedded signup not configured) */}
      {(!embeddedSignupReady || showManual) && (
        <>
          {!embeddedSignupReady && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 mb-5 text-xs text-amber-900">
              <p className="font-semibold mb-1">⚠️ Dev mode</p>
              <p>
                Meta Embedded Signup not configured. Paste credentials from{" "}
                <a
                  href="https://developers.facebook.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline"
                >
                  Meta Developer Console
                </a>
                .
              </p>
            </div>
          )}

          <form onSubmit={handleManualSubmit} className="space-y-4">
            <Input
              label="Phone Number ID *"
              placeholder="123456789012345"
              value={phoneNumberId}
              onChange={(e) => setPhoneNumberId(e.target.value)}
              required
            />
            <Input
              label="Access Token *"
              type="password"
              placeholder="EAAB..."
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              required
              minLength={10}
            />
            <Input
              label="Display Phone (optional)"
              placeholder="+919876543210"
              value={displayPhone}
              onChange={(e) => setDisplayPhone(e.target.value)}
            />
            <Input
              label="Business Account ID (optional)"
              placeholder="987654321"
              value={businessAccountId}
              onChange={(e) => setBusinessAccountId(e.target.value)}
            />
            <Button
              type="submit"
              loading={mutation.isPending}
              fullWidth
              size="lg"
              disabled={!phoneNumberId.trim() || !accessToken.trim()}
            >
              Connect WhatsApp
              <ArrowRight className="h-5 w-5" />
            </Button>
          </form>

          {embeddedSignupReady && (
            <button
              onClick={() => setShowManual(false)}
              className="text-sm text-slate-500 hover:text-slate-700 mt-4 block mx-auto underline"
            >
              ← Back to Facebook sign-in
            </button>
          )}
        </>
      )}

      <button
        onClick={() => router.replace("/onboarding/intents")}
        className="text-sm text-slate-500 hover:text-slate-700 mt-4 block mx-auto"
      >
        Skip for now
      </button>
    </div>
  );
}
