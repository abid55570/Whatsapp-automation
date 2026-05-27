"use client";

import { Home, MessageCircle, Settings, Zap } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const TABS = [
  { href: "/dashboard", icon: Home, label: "Home", exact: true },
  { href: "/dashboard/inbox", icon: MessageCircle, label: "Chats" },
  { href: "/onboarding/intents", icon: Zap, label: "Replies" },
  { href: "/dashboard/settings", icon: Settings, label: "Settings" },
];

export function BottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-20 pb-safe"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <div className="max-w-md mx-auto flex">
        {TABS.map((tab) => {
          const active = tab.exact
            ? pathname === tab.href
            : pathname === tab.href || pathname.startsWith(tab.href + "/");
          const Icon = tab.icon;
          return (
            <Link
              key={tab.href}
              href={tab.href}
              aria-label={tab.label}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex-1 flex flex-col items-center justify-center gap-0.5 min-h-[48px] py-2 transition active:scale-95",
                active ? "text-brand-600" : "text-slate-500 hover:text-slate-700",
              )}
            >
              <Icon
                className={cn(
                  "h-5 w-5 transition",
                  active && "fill-brand-100",
                )}
                strokeWidth={active ? 2.5 : 2}
              />
              <span
                className={cn(
                  "text-[10px] font-medium",
                  active && "font-semibold",
                )}
              >
                {tab.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
