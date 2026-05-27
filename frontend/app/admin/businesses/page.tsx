"use client";

import { Loader2, Search } from "lucide-react";
import { useState } from "react";

import { useAdminBusinesses } from "@/lib/queries";

export default function AdminBusinessesPage() {
  const [q, setQ] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 50;
  const { data, isLoading } = useAdminBusinesses(q, limit, offset);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h1 className="text-2xl font-bold text-slate-900">Businesses</h1>
        <div className="relative">
          <Search className="h-4 w-4 absolute left-2.5 top-2.5 text-slate-400" />
          <input
            value={q}
            onChange={(e) => {
              setQ(e.target.value);
              setOffset(0);
            }}
            placeholder="Search by name"
            className="pl-8 pr-3 py-2 border border-slate-300 rounded-lg text-sm w-full sm:w-64"
          />
        </div>
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
                <th className="text-left py-2 px-3">Type</th>
                <th className="text-left py-2 px-3">WhatsApp</th>
                <th className="text-left py-2 px-3">Plan</th>
                <th className="text-left py-2 px-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-slate-500">
                    No businesses found.
                  </td>
                </tr>
              ) : (
                data.items.map((b) => (
                  <tr key={b.id} className="border-t border-slate-100">
                    <td className="py-2 px-3">
                      <div className="font-medium text-slate-900">{b.name}</div>
                      {!b.onboarding_completed && (
                        <span className="text-[10px] uppercase text-orange-600">
                          onboarding
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-3 text-slate-600">
                      {b.business_type}
                    </td>
                    <td className="py-2 px-3 text-xs">
                      {b.whatsapp_connected ? (
                        <span className="text-green-600">
                          {b.whatsapp_display_phone || "connected"}
                        </span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="py-2 px-3 text-slate-600">
                      {b.plan || "—"}
                    </td>
                    <td className="py-2 px-3">
                      <span
                        className={
                          b.sub_status === "active"
                            ? "px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded"
                            : b.sub_status === "frozen"
                            ? "px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded"
                            : "px-2 py-0.5 bg-slate-100 text-slate-600 text-xs rounded"
                        }
                      >
                        {b.sub_status || "none"}
                      </span>
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
          <div>
            {data.total} total · showing {offset + 1}–
            {Math.min(offset + limit, data.total)}
          </div>
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
