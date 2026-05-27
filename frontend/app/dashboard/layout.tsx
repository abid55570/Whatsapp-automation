"use client";

import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { BottomNav } from "@/components/BottomNav";
import { useOnboardingStatus } from "@/lib/queries";
import { useAuthStore } from "@/stores/auth";

export default function DashboardLayout({
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

  useEffect(() => {
    if (!status) return;
    if (status.next_step !== "done") {
      // Force user back through onboarding if not finished
      const routes: Record<string, string> = {
        create_business: "/onboarding/business",
        connect_whatsapp: "/onboarding/whatsapp",
        configure_intents: "/onboarding/intents",
      };
      const target = routes[status.next_step];
      if (target) router.replace(target);
    }
  }, [status, router]);

  if (!hydrated || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <main className="flex-1 max-w-md mx-auto w-full pb-20">{children}</main>
      <BottomNav />
    </div>
  );
}
