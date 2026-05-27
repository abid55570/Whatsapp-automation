"use client";

import {
  AlertCircle,
  ArrowLeft,
  Clock,
  Loader2,
  MapPin,
  Package,
  Phone,
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/Button";
import { apiErrorMessage } from "@/lib/api";
import { useOrder, useUpdateOrderStatus } from "@/lib/queries";
import { cn } from "@/lib/utils";
import type { OrderStatus } from "@/types/api";

const STATUS_LABEL: Record<OrderStatus, string> = {
  new: "🆕 New",
  confirmed: "✅ Confirmed",
  preparing: "👨‍🍳 Preparing",
  ready_for_pickup: "📦 Ready for pickup",
  picked_up: "✓ Picked up",
  packed: "📦 Packed",
  out_for_delivery: "🛵 Out for delivery",
  delivered: "✓ Delivered",
  completed: "✓ Completed",
  canceled: "❌ Canceled",
};

const PICKUP_NEXT: Record<string, OrderStatus[]> = {
  new: ["confirmed", "canceled"],
  confirmed: ["preparing", "canceled"],
  preparing: ["ready_for_pickup", "canceled"],
  ready_for_pickup: ["picked_up", "canceled"],
  picked_up: ["completed"],
};

const DELIVERY_NEXT: Record<string, OrderStatus[]> = {
  new: ["confirmed", "canceled"],
  confirmed: ["preparing", "canceled"],
  preparing: ["packed", "canceled"],
  packed: ["out_for_delivery", "canceled"],
  out_for_delivery: ["delivered"],
  delivered: ["completed"],
};

function formatPrice(paise: number): string {
  const r = paise / 100;
  return r === Math.floor(r) ? `₹${r}` : `₹${r.toFixed(2)}`;
}

function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-IN", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function OrderDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const orderId = params.id;
  const { data: order, isLoading } = useOrder(orderId);
  const updateStatus = useUpdateOrderStatus(orderId);

  if (isLoading || !order) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-brand-500" />
      </div>
    );
  }

  const nextStatuses =
    order.fulfillment_type === "delivery"
      ? DELIVERY_NEXT[order.status] ?? []
      : PICKUP_NEXT[order.status] ?? [];

  async function setStatus(s: OrderStatus) {
    try {
      await updateStatus.mutateAsync({ status: s });
      toast.success(`Status updated`);
    } catch (err) {
      toast.error(apiErrorMessage(err));
    }
  }

  const paid = order.payment_status === "paid";

  return (
    <div className="animate-fade-in pb-8">
      <header className="sticky top-0 bg-white border-b border-slate-200 z-10 p-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.back()}
            className="p-1 hover:bg-slate-100 rounded-lg active:scale-95"
          >
            <ArrowLeft className="h-5 w-5 text-slate-700" />
          </button>
          <div className="flex-1 min-w-0">
            <p className="font-mono text-xs text-slate-500">
              #{order.order_number}
            </p>
            <h1 className="text-lg font-bold text-slate-900">
              {STATUS_LABEL[order.status]}
            </h1>
          </div>
        </div>
      </header>

      <div className="p-4 space-y-4">
        {/* Customer */}
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-brand-100 to-emerald-100 text-brand-700 font-semibold flex items-center justify-center">
              {(order.contact.name || order.contact.whatsapp_phone)
                .charAt(0)
                .toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-slate-900 truncate">
                {order.contact.name || "Unknown"}
              </p>
              <a
                href={`https://wa.me/${order.contact.whatsapp_phone.replace(/[^\d]/g, "")}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-brand-600 inline-flex items-center gap-1"
              >
                <Phone className="h-3 w-3" />
                {order.contact.whatsapp_phone}
              </a>
            </div>
          </div>
        </div>

        {/* Pickup / Delivery info */}
        {order.fulfillment_type === "pickup" && order.pickup_time && (
          <div className="card">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                <Clock className="h-5 w-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <p className="font-semibold text-slate-900 text-sm">
                  Pickup time
                </p>
                <p className="text-sm text-slate-700 mt-0.5">
                  {formatDateTime(order.pickup_time)}
                </p>
                {order.pickup_landmark && (
                  <p className="text-xs text-slate-500 mt-1 inline-flex items-start gap-1">
                    <MapPin className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    {order.pickup_landmark}
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Items */}
        <div className="card">
          <h3 className="font-semibold text-slate-900 text-sm mb-3 inline-flex items-center gap-2">
            <Package className="h-4 w-4" />
            Items ({order.items_count})
          </h3>
          <div className="space-y-2">
            {order.items.map((it) => (
              <div
                key={it.id}
                className="flex items-center justify-between text-sm"
              >
                <span className="text-slate-700">
                  {it.product_name} × {it.quantity}
                </span>
                <span className="font-mono text-slate-900">
                  {formatPrice(it.subtotal_paise)}
                </span>
              </div>
            ))}
          </div>
          <div className="border-t border-slate-100 mt-3 pt-3 flex items-center justify-between">
            <span className="font-semibold text-slate-900">Total</span>
            <span className="font-bold text-lg text-slate-900">
              {formatPrice(order.total_paise)}
            </span>
          </div>
        </div>

        {/* Payment */}
        <div
          className={cn(
            "card flex items-center gap-3",
            paid
              ? "bg-emerald-50 border border-emerald-200"
              : "bg-orange-50 border border-orange-200",
          )}
        >
          <div
            className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              paid ? "bg-emerald-100" : "bg-orange-100",
            )}
          >
            {paid ? (
              <span className="text-emerald-600 text-xl">✓</span>
            ) : (
              <AlertCircle className="h-5 w-5 text-orange-600" />
            )}
          </div>
          <div className="flex-1">
            <p className="font-semibold text-slate-900 text-sm">
              {paid ? "Paid" : "Payment pending"}
            </p>
            <p className="text-xs text-slate-600">
              {order.payment_method ?? "—"}
            </p>
          </div>
        </div>

        {/* Status actions */}
        {nextStatuses.length > 0 && (
          <div className="card">
            <h3 className="font-semibold text-slate-900 text-sm mb-3">
              Update status
            </h3>
            <div className="space-y-2">
              {nextStatuses.map((s) => (
                <Button
                  key={s}
                  onClick={() => setStatus(s)}
                  loading={updateStatus.isPending}
                  fullWidth
                  variant={s === "canceled" ? "danger" : "primary"}
                  size="md"
                >
                  Mark as {STATUS_LABEL[s]}
                </Button>
              ))}
            </div>
          </div>
        )}

        <p className="text-xs text-slate-400 text-center">
          Created {formatDateTime(order.created_at)}
        </p>
      </div>
    </div>
  );
}
