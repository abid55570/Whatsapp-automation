"use client";

import {
  BarChart3,
  Briefcase,
  CreditCard,
  Loader2,
  ShieldAlert,
  Users,
  Webhook,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { useMe } from "@/lib/queries";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

const NAV = [
  { href: "/admin", label: "Stats", icon: BarChart3, exact: true },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/businesses", label: "Businesses", icon: Briefcase },
  { href: "/admin/subscriptions", label: "Subscriptions", icon: CreditCard },
  { href: "/admin/webhooks", label: "Webhooks", icon: Webhook },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const hydrated = useAuthStore((s) => s.hydrated);
  const isAuthed = useAuthStore((s) => s.isAuthenticated());
  const { data: me, isLoading, error } = useMe();

  useEffect(() => {
    if (hydrated && !isAuthed) router.replace("/signup");
  }, [hydrated, isAuthed, router]);

  if (!hydrated || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  if (error || !me?.is_superuser) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 p-6">
        <div className="max-w-md text-center bg-white border border-slate-200 rounded-2xl p-8">
          <ShieldAlert className="h-12 w-12 mx-auto text-red-500 mb-3" />
          <h1 className="text-xl font-bold text-slate-900 mb-2">
            Forbidden
          </h1>
          <p className="text-slate-600 mb-4">
            Superuser access required.
          </p>
          <Link
            href="/dashboard"
            className="inline-block px-4 py-2 bg-brand-600 text-white rounded-lg font-medium"
          >
            Back to dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-slate-900 text-white sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-amber-400" />
            <span className="font-bold">Admin</span>
            <span className="text-xs text-slate-400 hidden sm:inline">
              · {me.phone}
            </span>
          </div>
          <Link
            href="/dashboard"
            className="text-xs text-slate-300 hover:text-white"
          >
            ← Back to app
          </Link>
        </div>
        <nav className="max-w-6xl mx-auto px-2 flex overflow-x-auto">
          {NAV.map((tab) => {
            const Icon = tab.icon;
            const active = tab.exact
              ? pathname === tab.href
              : pathname === tab.href || pathname.startsWith(tab.href + "/");
            return (
              <Link
                key={tab.href}
                href={tab.href}
                className={cn(
                  "px-3 py-2.5 text-xs sm:text-sm font-medium flex items-center gap-1.5 border-b-2 transition whitespace-nowrap",
                  active
                    ? "border-amber-400 text-white"
                    : "border-transparent text-slate-300 hover:text-white",
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
              </Link>
            );
          })}
        </nav>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-6">{children}</main>
    </div>
  );
}
