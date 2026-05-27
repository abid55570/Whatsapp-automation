"use client";

import { Loader2 } from "lucide-react";
import { useState } from "react";

import { useAdminSubscriptions } from "@/lib/queries";

const STATUSES = [
  { value: "", label: "All" },
  { value: "trialing", label: "Trialing" },
  { value: "active", label: "Active" },
  { value: "frozen", label: "Frozen" },
  { value: "canceled", label: "Canceled" },
  { value: "past_due", label: "Past due" },
];

export default function AdminSubscriptionsPage() {
  const [status, setStatus] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 50;
  const { data, isLoading } = useAdminSubscriptions(status, limit, offset);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h1 className="text-2xl font-bold text-slate-900">Subscriptions</h1>
        <select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setOffset(0);
          }}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        >
          {STATUSES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading || !data ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-x-auto">
          <table className="w-full text-sm min-w-[720px]">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="text-left py-2 px-3">Business</th>
                <th className="text-left py-2 px-3">Plan</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-left py-2 px-3">AI</th>
                <th className="text-left py-2 px-3">Usage</th>
                <th className="text-left py-2 px-3">Period end</th>
              </tr>
            </thead>
            <tbody>
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No subscriptions.
                  </td>
                </tr>
              ) : (
                data.items.map((s) => (
                  <tr key={s.id} className="border-t border-slate-100">
                    <td className="py-2 px-3 text-xs font-mono text-slate-700">
                      {s.business_id.slice(0, 8)}…
                    </td>
                    <td className="py-2 px-3 font-medium">{s.plan}</td>
                    <td className="py-2 px-3">
                      <span
                        className={
                          s.status === "active"
                            ? "px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded"
                            : s.status === "trialing"
                            ? "px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded"
                            : s.status === "frozen"
                            ? "px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded"
                            : "px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded"
                        }
                      >
                        {s.status}
                      </span>
                    </td>
                    <td className="py-2 px-3">
                      {s.ai_addon_enabled ? "✓" : "—"}
                    </td>
                    <td className="py-2 px-3 text-xs text-slate-600">
                      {s.conversations_used}/{s.conversations_included}
                    </td>
                    <td className="py-2 px-3 text-xs text-slate-600">
                      {s.current_period_end
                        ? new Date(s.current_period_end).toLocaleDateString()
                        : s.trial_ends_at
                        ? `trial: ${new Date(s.trial_ends_at).toLocaleDateString()}`
                        : "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {data && (
        <div className="flex items-center justify-between text-sm text-slate-600">
          <div>{data.total} total</div>
          <div className="flex gap-2">
            <button
              disabled={offset === 0}
              onClick={() => setOffset(Math.max(0, offset - limit))}
              className="px-3 py-1.5 border border-slate-300 rounded disabled:opacity-40"
            >
              Prev
            </button>
            <button
              disabled={!data.has_more}
              onClick={() => setOffset(offset + limit)}
              className="px-3 py-1.5 border border-slate-300 rounded disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
