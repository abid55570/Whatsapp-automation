"use client";

import {
  Bell,
  Bot,
  FileSpreadsheet,
  Languages,
  MessageCircle,
  Package,
  TrendingUp,
  Users,
  Zap,
} from "lucide-react";
import Link from "next/link";

import { StatCard } from "@/components/StatCard";
import { TrialBanner } from "@/components/TrialBanner";
import { useDashboardStats, useMyBusiness } from "@/lib/queries";

export default function DashboardHomePage() {
  const { data: business } = useMyBusiness();
  const { data: stats, isLoading } = useDashboardStats(7);

  return (
    <div className="p-4 animate-fade-in">
      <header className="mb-4">
        <p className="text-xs text-slate-500 uppercase tracking-wide font-semibold">
          {new Date().toLocaleDateString("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
          })}
        </p>
        <h1 className="text-2xl font-bold text-slate-900 mt-0.5">
          Hi, {business?.name?.split(" ")[0] ?? "there"} 👋
        </h1>
      </header>

      <TrialBanner subscription={business?.subscription ?? null} />

      {/* Top row: needs attention + auto-replied */}
      <div className="flex gap-3 mb-3">
        <StatCard
          label="Needs reply"
          value={stats?.needs_attention_count ?? 0}
          icon={Bell}
          iconColor="text-orange-600"
          iconBg="bg-orange-100"
          highlight={(stats?.needs_attention_count ?? 0) > 0}
        />
        <StatCard
          label="Auto-replied"
          value={stats?.auto_replied_count ?? 0}
          hint={`${stats?.auto_reply_rate ?? 0}% of inbound`}
          icon={Bot}
          iconColor="text-emerald-600"
          iconBg="bg-emerald-100"
        />
      </div>

      {/* Second row */}
      <div className="flex gap-3 mb-3">
        <StatCard
          label="Messages (7d)"
          value={stats?.total_messages ?? 0}
          hint={`${stats?.inbound_messages ?? 0} in · ${stats?.outbound_messages ?? 0} out`}
          icon={MessageCircle}
          iconColor="text-brand-600"
          iconBg="bg-brand-100"
        />
        <StatCard
          label="Contacts (7d)"
          value={stats?.unique_contacts ?? 0}
          icon={Users}
          iconColor="text-indigo-600"
          iconBg="bg-indigo-100"
        />
      </div>

      {/* Third row */}
      <div className="flex gap-3 mb-6">
        <StatCard
          label="Open chats"
          value={stats?.active_conversations ?? 0}
          hint="In 24h window"
          icon={TrendingUp}
          iconColor="text-blue-600"
          iconBg="bg-blue-100"
        />
        <StatCard
          label="Today"
          value={stats?.conversations_today ?? 0}
          hint="New chats"
          icon={Zap}
          iconColor="text-amber-600"
          iconBg="bg-amber-100"
        />
      </div>

      {/* Quick links */}
      <div className="space-y-2 mb-6">
        <h2 className="text-sm font-semibold text-slate-600 px-1 mb-2">
          Quick actions
        </h2>
        <Link
          href="/dashboard/inbox"
          className="card flex items-center gap-3 hover:bg-slate-50 transition active:scale-[0.99]"
        >
          <div className="w-10 h-10 rounded-xl bg-brand-100 flex items-center justify-center">
            <MessageCircle className="h-5 w-5 text-brand-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-slate-900 text-sm">
              Open inbox
            </p>
            <p className="text-xs text-slate-500">
              See conversations &amp; reply
            </p>
          </div>
          {(stats?.needs_attention_count ?? 0) > 0 && (
            <span className="bg-orange-500 text-white text-xs font-semibold px-2 py-0.5 rounded-full">
              {stats?.needs_attention_count}
            </span>
          )}
        </Link>

        <Link
          href="/onboarding/intents"
          className="card flex items-center gap-3 hover:bg-slate-50 transition active:scale-[0.99]"
        >
          <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
            <Zap className="h-5 w-5 text-amber-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-slate-900 text-sm">
              Edit auto-replies
            </p>
            <p className="text-xs text-slate-500">
              {business?.intent_count ?? 0} enabled
            </p>
          </div>
        </Link>

        <Link
          href="/dashboard/orders"
          className="card flex items-center gap-3 hover:bg-slate-50 transition active:scale-[0.99]"
        >
          <div className="w-10 h-10 rounded-xl bg-indigo-100 flex items-center justify-center">
            <Package className="h-5 w-5 text-indigo-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-slate-900 text-sm">
              Orders
            </p>
            <p className="text-xs text-slate-500">
              Pickup & delivery pipeline
            </p>
          </div>
        </Link>

        <Link
          href="/dashboard/sheets"
          className="card flex items-center gap-3 hover:bg-slate-50 transition active:scale-[0.99]"
        >
          <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
            <FileSpreadsheet className="h-5 w-5 text-green-600" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-slate-900 text-sm">
              Google Sheets
            </p>
            <p className="text-xs text-slate-500">
              Sync FAQs from a spreadsheet
            </p>
          </div>
        </Link>
      </div>

      {/* Language breakdown */}
      {!isLoading && stats && Object.keys(stats.matched_languages).length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Languages className="h-4 w-4 text-slate-600" />
            <h2 className="text-sm font-semibold text-slate-700">
              Customer languages
            </h2>
          </div>
          <div className="space-y-2">
            {Object.entries(stats.matched_languages)
              .sort((a, b) => b[1] - a[1])
              .map(([lang, count]) => {
                const total = Object.values(stats.matched_languages).reduce(
                  (a, b) => a + b,
                  0,
                );
                const pct = total > 0 ? (count / total) * 100 : 0;
                return (
                  <div key={lang} className="flex items-center gap-2 text-sm">
                    <span className="capitalize text-slate-700 w-20 text-xs">
                      {lang}
                    </span>
                    <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-brand-500 rounded-full"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-500 w-10 text-right">
                      {count}
                    </span>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
