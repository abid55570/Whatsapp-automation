"use client";

import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { StepIndicator } from "@/components/StepIndicator";
import { useOnboardingStatus } from "@/lib/queries";
import { useAuthStore } from "@/stores/auth";

export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const isAuthed = useAuthStore((s) => s.isAuthenticated());
  const hydrated = useAuthStore((s) => s.hydrated);

  useEffect(() => {
    if (hydrated && !isAuthed) {
      router.replace("/signup");
    }
  }, [hydrated, isAuthed, router]);

  const { data: status, isLoading } = useOnboardingStatus();

  if (!hydrated || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-md mx-auto p-4">
          <StepIndicator currentStep={status?.next_step} />
        </div>
      </header>
      <main className="flex-1 max-w-md mx-auto w-full p-4 pb-24">
        {children}
      </main>
    </div>
  );
}
