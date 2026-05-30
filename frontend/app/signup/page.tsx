"use client";

import { ArrowRight, FlaskConical } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { motion } from "framer-motion";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import AuroraBackground from "@/components/ui/aurora-background";
import { Component as MagicCursor } from "@/components/ui/magic-cursor";
import { MouseFollowingEyes } from "@/components/ui/mouse-following-eyes";
import { apiErrorMessage } from "@/lib/api";
import { useStartVerification } from "@/lib/queries";

const SERIF = "'Instrument Serif', serif";

// Generate a unique-ish test phone number every page mount so multiple test
// signups in the same dev session don't collide.
const TEST_NAME = "Test Owner";
function genTestPhone() {
  const n = Math.floor(1000000 + Math.random() * 8999999);  // 7 digits
  return `9${String(n).padStart(9, "0").slice(0, 9)}`;
}

export default function SignupPage() {
  const router = useRouter();
  const [phone, setPhone] = useState("");
  const [fullName, setFullName] = useState("");
  const mutation = useStartVerification();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const result = await mutation.mutateAsync({
        phone,
        full_name: fullName || undefined,
      });
      // Stash everything we need on /verify
      sessionStorage.setItem("verification_id", result.verification_id);
      sessionStorage.setItem("deep_link", result.deep_link);
      sessionStorage.setItem(
        "platform_phone",
        result.platform_whatsapp_number ?? "",
      );
      sessionStorage.setItem("user_phone_input", phone);
      if (result.dev_code) {
        sessionStorage.setItem("dev_code", result.dev_code);
      } else {
        sessionStorage.removeItem("dev_code");
      }
      router.push("/signup/verify");
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-white p-4">
      {/* Flowing green aurora + sparkle cursor */}
      <AuroraBackground />
      <MagicCursor colors={["252 254 255", "37 211 102", "52 217 124"]} />

      {/* Home / logo top-left */}
      <Link
        href="/"
        aria-label="Back to home"
        className="group absolute left-5 top-5 z-20 flex items-center gap-2.5"
      >
        <span
          className="inline-block h-8 w-8 rounded-full transition-transform duration-300 group-hover:rotate-12"
          style={{ background: "linear-gradient(135deg,#25d366,#128c7e)" }}
        />
        <span
          className="text-2xl leading-none tracking-tight text-slate-900"
          style={{ fontFamily: SERIF }}
        >
          Whatly
        </span>
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 w-full max-w-md rounded-3xl border border-white/50 bg-white/55 p-6 shadow-[0_30px_90px_-28px_rgba(16,140,126,0.4)] backdrop-blur-2xl sm:p-8"
      >
        <div className="mb-7 text-center">
          <div className="mb-5 flex justify-center">
            <MouseFollowingEyes size={48} />
          </div>
          <h1 className="text-3xl italic text-slate-900" style={{ fontFamily: SERIF }}>
            Sign up free
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            14-day trial · No credit card
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Your name"
            placeholder="Ramesh Kumar"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            maxLength={100}
            autoFocus
          />
          <Input
            label="WhatsApp number"
            placeholder="9876543210"
            type="tel"
            inputMode="numeric"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            leftAdornment={<span className="text-sm font-medium">+91</span>}
            hint="We'll verify via WhatsApp — no OTP code to type"
            required
            minLength={10}
            maxLength={10}
            pattern="[6-9][0-9]{9}"
            autoComplete="tel-national"
          />
          <Button
            type="submit"
            loading={mutation.isPending}
            fullWidth
            size="lg"
          >
            Continue
            <ArrowRight className="h-5 w-5" />
          </Button>
        </form>

        {process.env.NODE_ENV !== "production" && (
          <button
            type="button"
            onClick={() => {
              setFullName(TEST_NAME);
              setPhone(genTestPhone());
              setTimeout(() => {
                const form = document.querySelector("form");
                form?.dispatchEvent(
                  new Event("submit", { cancelable: true, bubbles: true }),
                );
              }, 100);
            }}
            className="mt-4 w-full flex items-center justify-center gap-2 border-2 border-dashed border-amber-300 bg-amber-50 hover:bg-amber-100 text-amber-900 font-semibold px-4 py-2.5 rounded-xl text-sm min-h-[44px]"
          >
            <FlaskConical className="h-4 w-4" />
            Dev: signup with random test phone (no Meta needed)
          </button>
        )}

        <p className="text-xs text-center text-slate-500 mt-8">
          By continuing, you agree to our{" "}
          <Link href="/terms" className="underline">
            Terms
          </Link>{" "}
          and{" "}
          <Link href="/privacy" className="underline">
            Privacy Policy
          </Link>
          .
        </p>
      </motion.div>
    </main>
  );
}
