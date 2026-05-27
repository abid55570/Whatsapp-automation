"use client";

import {
  Bell,
  ChevronRight,
  Clock,
  CreditCard,
  FileSpreadsheet,
  FileText,
  Globe,
  LogOut,
  MessageSquare,
  Package,
  Phone,
  Receipt,
  Settings as SettingsIcon,
  Shield,
  ShieldAlert,
  Sparkles,
  User as UserIcon,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useMe, useMyBusiness } from "@/lib/queries";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth";

interface RowProps {
  icon: React.ComponentType<{ className?: string }>;
  iconBg?: string;
  iconColor?: string;
  label: string;
  value?: string;
  href?: string;
  onClick?: () => void;
  danger?: boolean;
}

function Row({
  icon: Icon,
  iconBg = "bg-slate-100",
  iconColor = "text-slate-600",
  label,
  value,
  href,
  onClick,
  danger,
}: RowProps) {
  const inner = (
    <div className="flex items-center gap-3 w-full">
      <div
        className={cn(
          "w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0",
          iconBg,
        )}
      >
        <Icon className={cn("h-4 w-4", iconColor)} />
      </div>
      <div className="flex-1 min-w-0 text-left">
        <p
          className={cn(
            "text-sm font-medium",
            danger ? "text-red-600" : "text-slate-900",
          )}
        >
          {label}
        </p>
        {value && (
          <p className="text-xs text-slate-500 truncate">{value}</p>
        )}
      </div>
      {(href || onClick) && (
        <ChevronRight className="h-4 w-4 text-slate-400 flex-shrink-0" />
      )}
    </div>
  );

  const classes =
    "block p-3 hover:bg-slate-50 active:bg-slate-100 transition border-b border-slate-100 last:border-b-0";

  if (href) {
    return (
      <Link href={href} className={classes}>
        {inner}
      </Link>
    );
  }
  if (onClick) {
    return (
      <button onClick={onClick} className={cn(classes, "w-full text-left")}>
        {inner}
      </button>
    );
  }
  return <div className={classes}>{inner}</div>;
}

export default function SettingsPage() {
  const router = useRouter();
  const { data: user } = useMe();
  const { data: business } = useMyBusiness();
  const clearAuth = useAuthStore((s) => s.clearAuth);

  function handleLogout() {
    clearAuth();
    router.replace("/");
  }

  const sub = business?.subscription;
  const planLabel = sub
    ? sub.plan === "trial"
      ? `Trial · ${sub.days_remaining_in_trial ?? 0} days left`
      : sub.plan.charAt(0).toUpperCase() + sub.plan.slice(1)
    : "—";

  return (
    <div className="animate-fade-in pb-8">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10 p-4">
        <h1 className="text-xl font-bold text-slate-900">Settings</h1>
      </header>

      {/* Profile card */}
      <div className="p-4">
        <div className="card flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-brand-100 to-emerald-100 text-brand-700 font-semibold flex items-center justify-center text-lg">
            {(user?.full_name || user?.phone || "?").charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-semibold text-slate-900 truncate">
              {user?.full_name || "Owner"}
            </p>
            <p className="text-sm text-slate-500 truncate">{user?.phone}</p>
          </div>
        </div>
      </div>

      {/* Business */}
      <div className="px-4">
        <h2 className="text-xs uppercase tracking-wide font-semibold text-slate-500 mb-2 px-1">
          Business
        </h2>
        <div className="bg-white rounded-2xl overflow-hidden shadow-soft">
          <Row
            icon={SettingsIcon}
            iconColor="text-slate-600"
            label="Profile"
            value={business?.name || "—"}
          />
          <Row
            icon={Phone}
            iconBg="bg-emerald-100"
            iconColor="text-emerald-600"
            label="WhatsApp Business"
            value={
              business?.whatsapp_connected
                ? business?.whatsapp_display_phone || "Connected"
                : "Not connected"
            }
            href="/onboarding/whatsapp"
          />
          <Row
            icon={Zap}
            iconBg="bg-amber-100"
            iconColor="text-amber-600"
            label="Auto-replies"
            value={`${business?.intent_count ?? 0} enabled`}
            href="/onboarding/intents"
          />
          <Row
            icon={Package}
            iconBg="bg-indigo-100"
            iconColor="text-indigo-600"
            label="Orders"
            value="Pickup & delivery pipeline"
            href="/dashboard/orders"
          />
          <Row
            icon={FileText}
            iconBg="bg-violet-100"
            iconColor="text-violet-600"
            label="Invoices"
            value="GST invoices · PDF · WhatsApp share"
            href="/dashboard/invoices"
          />
          <Row
            icon={Receipt}
            iconBg="bg-pink-100"
            iconColor="text-pink-600"
            label="GST settings"
            value="GSTIN · scheme · invoice prefix"
            href="/dashboard/settings/gst"
          />
          <Row
            icon={FileSpreadsheet}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            label="Tax Filing Center"
            value="GSTR-1 · GSTR-3B · sales register"
            href="/dashboard/reports"
          />
          <Row
            icon={Clock}
            iconBg="bg-orange-100"
            iconColor="text-orange-600"
            label="Pickup & Delivery"
            value="Hours, prep time, slots, fees"
            href="/dashboard/settings/fulfillment"
          />
          <Row
            icon={FileSpreadsheet}
            iconBg="bg-green-100"
            iconColor="text-green-600"
            label="Google Sheets"
            value="Sync FAQs / menu / services"
            href="/dashboard/sheets"
          />
          <Row
            icon={Globe}
            iconBg="bg-indigo-100"
            iconColor="text-indigo-600"
            label="Languages"
            value={business?.languages?.join(", ") || "—"}
          />
        </div>
      </div>

      {/* Subscription */}
      <div className="px-4 mt-6">
        <h2 className="text-xs uppercase tracking-wide font-semibold text-slate-500 mb-2 px-1">
          Subscription
        </h2>
        <div className="bg-white rounded-2xl overflow-hidden shadow-soft">
          <Row
            icon={Sparkles}
            iconBg="bg-brand-100"
            iconColor="text-brand-600"
            label="Current plan"
            value={planLabel}
          />
          <Row
            icon={MessageSquare}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            label="Conversations used"
            value={`${sub?.conversations_used ?? 0} / ${sub?.conversations_included ?? 0}`}
          />
          <Row
            icon={CreditCard}
            iconBg="bg-emerald-100"
            iconColor="text-emerald-600"
            label="Upgrade plan"
            href="/dashboard/settings/billing"
          />
        </div>
      </div>

      {/* Account */}
      <div className="px-4 mt-6">
        <h2 className="text-xs uppercase tracking-wide font-semibold text-slate-500 mb-2 px-1">
          Account
        </h2>
        <div className="bg-white rounded-2xl overflow-hidden shadow-soft">
          <Row
            icon={UserIcon}
            label="Personal details"
            value={user?.phone}
          />
          <Row
            icon={Globe}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            label="App language"
            value="हिन्दी / English / Hinglish ..."
            href="/dashboard/settings/language"
          />
          <Row icon={Bell} label="Notifications" />
          <Row
            icon={Shield}
            iconBg="bg-blue-100"
            iconColor="text-blue-600"
            label="Privacy & Data"
            value="Export · Delete account"
            href="/dashboard/settings/privacy"
          />
          <Row
            icon={LogOut}
            iconBg="bg-red-100"
            iconColor="text-red-600"
            label="Log out"
            onClick={handleLogout}
            danger
          />
        </div>
      </div>

      {/* Superuser-only */}
      {user?.is_superuser && (
        <div className="px-4 mt-6">
          <h2 className="text-xs uppercase tracking-wide font-semibold text-slate-500 mb-2 px-1">
            Platform admin
          </h2>
          <div className="bg-white rounded-2xl overflow-hidden shadow-soft">
            <Row
              icon={ShieldAlert}
              iconBg="bg-amber-100"
              iconColor="text-amber-600"
              label="Admin dashboard"
              value="Platform-wide oversight"
              href="/admin"
            />
          </div>
        </div>
      )}

      <p className="text-center text-xs text-slate-400 mt-8">
        WhatsApp Business Automation · v0.1.0
      </p>
    </div>
  );
}
