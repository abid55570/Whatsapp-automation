"use client";

import { Loader2, Package } from "lucide-react";
import { useState } from "react";

import { OrderCard } from "@/components/OrderCard";
import { useOrders } from "@/lib/queries";
import { cn } from "@/lib/utils";
import type { OrderListFilter } from "@/types/api";

const FILTERS: { key: OrderListFilter; label: string }[] = [
  { key: "active", label: "Active" },
  { key: "completed", label: "Done" },
  { key: "all", label: "All" },
  { key: "canceled", label: "Canceled" },
];

export default function OrdersListPage() {
  const [filter, setFilter] = useState<OrderListFilter>("active");
  const { data, isLoading } = useOrders(filter);

  const items = data?.items ?? [];

  return (
    <div className="animate-fade-in">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <h1 className="text-xl font-bold text-slate-900 mb-0.5">Orders</h1>
        <p className="text-xs text-slate-500">
          {data?.total ?? 0} {(data?.total ?? 0) === 1 ? "order" : "orders"}
        </p>
        <div className="flex gap-2 mt-3 overflow-x-auto -mx-1 px-1">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              className={cn(
                "px-3 py-1.5 rounded-full text-xs font-medium transition active:scale-95 whitespace-nowrap",
                filter === f.key
                  ? "bg-brand-500 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200",
              )}
            >
              {f.label}
            </button>
          ))}
        </div>
      </header>

      <div className="p-4">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-16">
            <div className="inline-flex w-16 h-16 rounded-2xl bg-slate-100 items-center justify-center mb-4">
              <Package className="h-7 w-7 text-slate-400" />
            </div>
            <h2 className="font-semibold text-slate-900 mb-1">
              No {filter === "all" ? "" : filter} orders
            </h2>
            <p className="text-sm text-slate-500 max-w-xs mx-auto">
              Customer orders from WhatsApp will show up here.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((o) => (
              <OrderCard key={o.id} order={o} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
