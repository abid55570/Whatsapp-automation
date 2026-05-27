"use client";

import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { useState } from "react";

import { useAdminWebhookEvents } from "@/lib/queries";

export default function AdminWebhooksPage() {
  const [source, setSource] = useState("");
  const [offset, setOffset] = useState(0);
  const limit = 50;
  const { data, isLoading } = useAdminWebhookEvents(source, limit, offset);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <h1 className="text-2xl font-bold text-slate-900">Webhook events</h1>
        <select
          value={source}
          onChange={(e) => {
            setSource(e.target.value);
            setOffset(0);
          }}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">All sources</option>
          <option value="meta_whatsapp">Meta WhatsApp</option>
          <option value="razorpay">Razorpay</option>
        </select>
      </div>

      {isLoading || !data ? (
        <div className="flex justify-center py-16">
          <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-x-auto">
          <table className="w-full text-sm min-w-[760px]">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="text-left py-2 px-3">Time</th>
                <th className="text-left py-2 px-3">Source</th>
                <th className="text-left py-2 px-3">Type</th>
                <th className="text-left py-2 px-3">Sig</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-left py-2 px-3">Error</th>
              </tr>
            </thead>
            <tbody>
              {data.items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No webhook events.
                  </td>
                </tr>
              ) : (
                data.items.map((e) => (
                  <tr key={e.id} className="border-t border-slate-100">
                    <td className="py-2 px-3 text-xs text-slate-600">
                      {new Date(e.received_at).toLocaleString()}
                    </td>
                    <td className="py-2 px-3 text-xs">{e.source}</td>
                    <td className="py-2 px-3 text-xs font-mono">
                      {e.event_type}
                    </td>
                    <td className="py-2 px-3">
                      {e.signature_verified ? (
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      ) : (
                        <XCircle className="h-4 w-4 text-red-500" />
                      )}
                    </td>
                    <td className="py-2 px-3">
                      <span
                        className={
                          e.processed
                            ? "px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded"
                            : "px-2 py-0.5 bg-amber-100 text-amber-700 text-xs rounded"
                        }
                      >
                        {e.processed ? "processed" : "pending"}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-xs text-red-600 max-w-xs truncate">
                      {e.error || "—"}
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
