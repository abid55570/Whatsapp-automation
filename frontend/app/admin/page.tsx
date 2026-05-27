"use client";

import { Loader2 } from "lucide-react";

import { useAdminStats } from "@/lib/queries";

function StatCard({
  label,
  value,
  hint,
}: {
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4">
      <div className="text-xs text-slate-500 uppercase tracking-wider">
        {label}
      </div>
      <div className="text-2xl font-bold text-slate-900 mt-1">{value}</div>
      {hint && <div className="text-xs text-slate-400 mt-0.5">{hint}</div>}
    </div>
  );
}

export default function AdminStatsPage() {
  const { data, isLoading } = useAdminStats();

  if (isLoading || !data) {
    return (
      <div className="flex justify-center py-16">
        <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
      </div>
    );
  }

  const revenue = (data.total_revenue_paise / 100).toLocaleString("en-IN");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900">Platform Stats</h1>

      <section>
        <h2 className="text-sm font-semibold text-slate-600 mb-3">Users</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <StatCard label="Total" value={data.total_users} />
          <StatCard label="Active" value={data.active_users} />
          <StatCard label="Superusers" value={data.superusers} />
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-600 mb-3">Businesses</h2>
        <div className="grid grid-cols-2 gap-3">
          <StatCard label="Total" value={data.total_businesses} />
          <StatCard label="Onboarded" value={data.onboarded_businesses} />
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-600 mb-3">
          Subscriptions
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <StatCard label="Trialing" value={data.trialing_subs} />
          <StatCard label="Active" value={data.active_subs} />
          <StatCard label="Frozen" value={data.frozen_subs} />
          <StatCard label="Canceled" value={data.canceled_subs} />
        </div>
        {Object.keys(data.plan_breakdown).length > 0 && (
          <div className="mt-3 bg-white border border-slate-200 rounded-xl p-4">
            <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">
              Plan breakdown (active)
            </div>
            <div className="flex flex-wrap gap-2">
              {Object.entries(data.plan_breakdown).map(([plan, n]) => (
                <span
                  key={plan}
                  className="px-2.5 py-1 bg-slate-100 text-slate-700 text-xs rounded-md"
                >
                  {plan}: <b>{n}</b>
                </span>
              ))}
            </div>
          </div>
        )}
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-600 mb-3">Revenue</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <StatCard label="Total orders" value={data.total_orders} />
          <StatCard label="Paid orders" value={data.paid_orders} />
          <StatCard
            label="Revenue"
            value={`₹${revenue}`}
            hint="lifetime (paid)"
          />
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-slate-600 mb-3">Webhooks</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <StatCard
            label="Events 24h"
            value={data.webhook_events_24h}
            hint="Meta + Razorpay"
          />
        </div>
      </section>
    </div>
  );
}
