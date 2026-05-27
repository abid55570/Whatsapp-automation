"use client";

import { Clock, Package } from "lucide-react";
import Link from "next/link";

import { cn } from "@/lib/utils";
import type { OrderListItem, OrderStatus } from "@/types/api";

const STATUS_META: Record<
  OrderStatus,
  { label: string; color: string; emoji: string }
> = {
  new: { label: "New", color: "bg-blue-100 text-blue-700", emoji: "🆕" },
  confirmed: { label: "Confirmed", color: "bg-brand-100 text-brand-700", emoji: "✅" },
  preparing: { label: "Preparing", color: "bg-amber-100 text-amber-700", emoji: "👨‍🍳" },
  ready_for_pickup: { label: "Ready", color: "bg-emerald-100 text-emerald-700", emoji: "📦" },
  picked_up: { label: "Picked up", color: "bg-slate-100 text-slate-700", emoji: "✓" },
  packed: { label: "Packed", color: "bg-purple-100 text-purple-700", emoji: "📦" },
  out_for_delivery: { label: "Out for delivery", color: "bg-orange-100 text-orange-700", emoji: "🛵" },
  delivered: { label: "Delivered", color: "bg-emerald-100 text-emerald-700", emoji: "✓" },
  completed: { label: "Completed", color: "bg-slate-100 text-slate-700", emoji: "✓" },
  canceled: { label: "Canceled", color: "bg-red-100 text-red-700", emoji: "❌" },
};

function formatPrice(paise: number): string {
  const r = paise / 100;
  return r === Math.floor(r) ? `₹${r}` : `₹${r.toFixed(2)}`;
}

function formatTime(iso: string | null): string {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    day: "numeric",
    month: "short",
  });
}

function urgency(pickup_time: string | null): "soon" | "now" | null {
  if (!pickup_time) return null;
  const diffMin = (new Date(pickup_time).getTime() - Date.now()) / 60_000;
  if (diffMin < 0) return "now";
  if (diffMin < 15) return "soon";
  return null;
}

export function OrderCard({ order }: { order: OrderListItem }) {
  const meta = STATUS_META[order.status];
  const urg = urgency(order.pickup_time);

  return (
    <Link
      href={`/dashboard/orders/${order.id}`}
      className="card hover:bg-slate-50 active:bg-slate-100 transition active:scale-[0.99] block"
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="min-w-0">
          <p className="font-mono text-xs text-slate-500 truncate">
            #{order.order_number}
          </p>
          <h3 className="font-semibold text-slate-900 truncate text-sm">
            {order.contact.name || order.contact.whatsapp_phone}
          </h3>
        </div>
        <span
          className={cn(
            "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold whitespace-nowrap",
            meta.color,
          )}
        >
          {meta.emoji} {meta.label}
        </span>
      </div>

      <div className="flex items-center gap-3 text-xs text-slate-600">
        <span className="inline-flex items-center gap-1">
          <Package className="h-3 w-3" />
          {order.items_count} items
        </span>
        <span>·</span>
        <span className="font-semibold text-slate-900">
          {formatPrice(order.total_paise)}
        </span>
        <span>·</span>
        <span
          className={cn(
            "uppercase font-medium tracking-wide text-[10px]",
            order.payment_status === "paid"
              ? "text-emerald-600"
              : "text-orange-600",
          )}
        >
          {order.payment_status}
        </span>
      </div>

      {order.pickup_time && (
        <div
          className={cn(
            "mt-2 inline-flex items-center gap-1 text-[11px] font-medium px-2 py-1 rounded-lg",
            urg === "now"
              ? "bg-red-100 text-red-700"
              : urg === "soon"
                ? "bg-amber-100 text-amber-700"
                : "bg-slate-100 text-slate-600",
          )}
        >
          <Clock className="h-3 w-3" />
          {urg === "now"
            ? "Overdue!"
            : urg === "soon"
              ? "In ≤15m"
              : "Pickup"}{" "}
          · {formatTime(order.pickup_time)}
        </div>
      )}
    </Link>
  );
}
