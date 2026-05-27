"use client";

import { ExternalLink, Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { apiErrorMessage, api } from "@/lib/api";

interface MetaSignupData {
  phone_number_id: string;
  waba_id: string;
}

interface Props {
  appId: string;
  configId: string;
  onSuccess: () => void;
}

/**
 * Meta WhatsApp Embedded Signup button.
 *
 * Loads FB JS SDK, opens FB.login with the configured config_id,
 * listens for the WA_EMBEDDED_SIGNUP postMessage with phone_number_id,
 * then POSTs the OAuth code + phone_number_id to the backend.
 */
export function MetaSignupButton({ appId, configId, onSuccess }: Props) {
  const [pending, setPending] = useState(false);
  const [sdkReady, setSdkReady] = useState(false);
  const signupDataRef = useRef<MetaSignupData | null>(null);

  // Load FB SDK once
  useEffect(() => {
    if (typeof window === "undefined") return;
    // @ts-expect-error — FB global injected by SDK
    if (window.FB) {
      setSdkReady(true);
      return;
    }
    // @ts-expect-error
    window.fbAsyncInit = function () {
      // @ts-expect-error
      window.FB.init({
        appId,
        cookie: true,
        xfbml: true,
        version: "v21.0",
      });
      setSdkReady(true);
    };
    const id = "facebook-jssdk";
    if (document.getElementById(id)) return;
    const fjs = document.getElementsByTagName("script")[0];
    const script = document.createElement("script");
    script.id = id;
    script.src = "https://connect.facebook.net/en_US/sdk.js";
    fjs.parentNode!.insertBefore(script, fjs);
  }, [appId]);

  // Listen for embedded-signup postMessage
  useEffect(() => {
    function onMessage(ev: MessageEvent) {
      if (
        !ev.origin.includes("facebook.com") &&
        !ev.origin.includes("meta.com")
      ) {
        return;
      }
      try {
        const data = typeof ev.data === "string" ? JSON.parse(ev.data) : ev.data;
        if (data?.type === "WA_EMBEDDED_SIGNUP" && data?.event === "FINISH") {
          signupDataRef.current = {
            phone_number_id: data.data?.phone_number_id ?? "",
            waba_id: data.data?.waba_id ?? "",
          };
        }
      } catch {
        // ignore non-JSON messages
      }
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, []);

  const launch = useCallback(() => {
    // @ts-expect-error
    if (!window.FB || !configId) {
      toast.error("Meta SDK not ready. Reload page.");
      return;
    }
    setPending(true);
    // @ts-expect-error
    window.FB.login(
      async (response: { authResponse?: { code?: string } }) => {
        const code = response?.authResponse?.code;
        if (!code) {
          setPending(false);
          toast.error("Sign-up canceled");
          return;
        }
        // Wait briefly for the postMessage to land
        await new Promise((r) => setTimeout(r, 500));
        const sig = signupDataRef.current;
        if (!sig?.phone_number_id) {
          setPending(false);
          toast.error("Did not receive phone number from Meta. Try again.");
          return;
        }
        try {
          await api.post("/api/v1/businesses/me/whatsapp/meta-exchange", {
            code,
            phone_number_id: sig.phone_number_id,
            business_account_id: sig.waba_id || undefined,
          });
          toast.success("WhatsApp connected!");
          onSuccess();
        } catch (err) {
          toast.error(apiErrorMessage(err));
        } finally {
          setPending(false);
        }
      },
      {
        config_id: configId,
        response_type: "code",
        override_default_response_type: true,
        extras: { setup: {} },
      },
    );
  }, [configId, onSuccess]);

  const disabled = !sdkReady || !configId || pending;

  return (
    <button
      onClick={launch}
      disabled={disabled}
      className="w-full inline-flex items-center justify-center gap-2 bg-[#1877F2] hover:bg-[#166FE5] text-white font-semibold px-6 py-3 rounded-xl transition active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {pending ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : (
        <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      )}
      Sign in with Facebook
      <ExternalLink className="h-3.5 w-3.5 opacity-70" />
    </button>
  );
}
