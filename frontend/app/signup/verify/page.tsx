"use client";

import { ExternalLink, Loader2, MessageCircle, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { apiErrorMessage } from "@/lib/api";
import {
  useDevSimulateVerify,
  useVerificationStatus,
} from "@/lib/queries";
import { useAuthStore } from "@/stores/auth";

export default function VerifyPage() {
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const [verificationId, setVerificationId] = useState<string | null>(null);
  const [deepLink, setDeepLink] = useState<string>("");
  const [userPhone, setUserPhone] = useState<string>("");
  const [devCode, setDevCode] = useState<string | null>(null);

  // Pull stored signup data
  useEffect(() => {
    const id = sessionStorage.getItem("verification_id");
    const link = sessionStorage.getItem("deep_link");
    const phone = sessionStorage.getItem("user_phone_input");
    const code = sessionStorage.getItem("dev_code");

    if (!id || !link) {
      router.replace("/signup");
      return;
    }
    setVerificationId(id);
    setDeepLink(link);
    setUserPhone(phone || "");
    setDevCode(code);
  }, [router]);

  const { data: status } = useVerificationStatus(verificationId);

  // Handle status transitions
  useEffect(() => {
    if (!status) return;
    if (status.status === "verified" && status.access_token && status.user) {
      setAuth(status.access_token, status.user);
      sessionStorage.clear();
      toast.success("Verified! 🎉");
      router.replace("/onboarding/business");
    } else if (status.status === "expired") {
      toast.error("Code expired. Please try again.");
      router.replace("/signup");
    }
  }, [status, setAuth, router]);

  const devSim = useDevSimulateVerify();

  async function handleDevSimulate() {
    if (!devCode || !userPhone) return;
    try {
      await devSim.mutateAsync({ phone: userPhone, code: devCode });
      // Polling will pick up the change within 2s
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-brand-50 to-white p-4 flex flex-col items-center justify-center">
      <div className="w-full max-w-sm text-center animate-fade-in">
        <div className="inline-flex w-20 h-20 rounded-3xl bg-brand-500 text-white text-4xl items-center justify-center mb-6 shadow-soft-lg animate-pulse">
          📱
        </div>

        <h1 className="text-2xl font-bold text-slate-900 mb-2">
          Verify via WhatsApp
        </h1>
        <p className="text-slate-600 mb-8 text-sm">
          Tap the button below — WhatsApp will open with a pre-filled message.
          <br />
          Just hit send. We'll log you in automatically.
        </p>

        <a
          href={deepLink}
          target="_blank"
          rel="noopener noreferrer"
          className="bg-brand-500 hover:bg-brand-600 text-white font-semibold rounded-xl px-6 py-4 shadow-soft inline-flex w-full items-center justify-center gap-2 text-lg transition active:scale-[0.98]"
        >
          <MessageCircle className="h-5 w-5" />
          Open WhatsApp & Verify
          <ExternalLink className="h-4 w-4" />
        </a>

        <div className="flex items-center justify-center gap-2 text-sm text-slate-500 mt-6">
          {status?.status === "pending" || !status ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Waiting for your WhatsApp message...</span>
            </>
          ) : status.status === "expired" ? (
            <span className="text-red-500">Verification expired</span>
          ) : null}
        </div>

        {devCode && (
          <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl text-left">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-bold text-amber-900 uppercase tracking-wide">
                🛠️ Dev Mode
              </span>
            </div>
            <p className="text-xs text-amber-900 mb-2">
              Use this to simulate the WhatsApp round-trip without setting up
              the platform's WA number.
            </p>
            <div className="flex items-center gap-2">
              <code className="text-sm font-mono bg-white px-2 py-1.5 rounded border border-amber-300 flex-1 text-center">
                {devCode}
              </code>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleDevSimulate}
                loading={devSim.isPending}
              >
                Simulate Send
              </Button>
            </div>
          </div>
        )}

        <button
          onClick={() => router.replace("/signup")}
          className="text-sm text-slate-500 hover:text-slate-700 mt-6 inline-flex items-center gap-1"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Wrong number? Start over
        </button>
      </div>
    </main>
  );
}
