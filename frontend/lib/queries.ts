/** TanStack Query hooks — wraps every backend endpoint we use. */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./api";
import type {
  AdminBusinessRow,
  AdminPaginated,
  AdminStats,
  AdminSubscriptionRow,
  AdminUserRow,
  AdminUserUpdate,
  AdminWebhookEvent,
  Business,
  BusinessCreateRequest,
  BusinessIntent,
  BusinessIntentsBulkRequest,
  ConversationDetail,
  DashboardStats,
  FulfillmentConfig,
  FulfillmentConfigUpdate,
  GlobalIntent,
  GstSettings,
  GstSettingsUpdate,
  Invoice,
  InvoiceCreate,
  InvoiceStatus,
  MessageDetail,
  OnboardingStatus,
  OrderDetail,
  OrderListFilter,
  OrderStatusUpdateRequest,
  PaginatedConversations,
  PaginatedInvoices,
  PaginatedMessages,
  PaginatedOrders,
  PaginatedPurchaseInvoices,
  PurchaseInvoice,
  PurchaseInvoiceCreate,
  ReportsOverview,
  SendMessageRequest,
  SheetSync,
  SheetSyncCreate,
  SheetSyncUpdate,
  StartVerificationRequest,
  StartVerificationResponse,
  User,
  VerificationStatusResponse,
  WhatsAppConnectRequest,
} from "@/types/api";

// ============================================================
// Auth
// ============================================================

export function useMe() {
  return useQuery<User>({
    queryKey: ["me"],
    queryFn: async () => (await api.get("/api/v1/auth/me")).data,
  });
}

export function useStartVerification() {
  return useMutation<
    StartVerificationResponse,
    Error,
    StartVerificationRequest
  >({
    mutationFn: async (data) =>
      (await api.post("/api/v1/auth/start-verification", data)).data,
  });
}

export function useVerificationStatus(verificationId: string | null) {
  return useQuery<VerificationStatusResponse>({
    queryKey: ["verification-status", verificationId],
    queryFn: async () =>
      (
        await api.get(`/api/v1/auth/verification-status/${verificationId}`)
      ).data,
    enabled: Boolean(verificationId),
    refetchInterval: (q) => {
      const data = q.state.data as VerificationStatusResponse | undefined;
      if (data?.status === "verified" || data?.status === "expired") return false;
      return 2000;
    },
  });
}

export function useDevSimulateVerify() {
  return useMutation<unknown, Error, { phone: string; code: string }>({
    mutationFn: async ({ phone, code }) =>
      (
        await api.post(
          "/api/v1/auth/dev/simulate-whatsapp-verify",
          null,
          { params: { phone, code } },
        )
      ).data,
  });
}

// ============================================================
// Business
// ============================================================

export function useMyBusiness() {
  return useQuery<Business>({
    queryKey: ["business"],
    queryFn: async () => (await api.get("/api/v1/businesses/me")).data,
    retry: (count, err: unknown) => {
      const e = err as { response?: { status?: number } };
      return e?.response?.status !== 404 && count < 2;
    },
  });
}

export function useCreateBusiness() {
  const qc = useQueryClient();
  return useMutation<Business, Error, BusinessCreateRequest>({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["business"] });
      qc.invalidateQueries({ queryKey: ["onboarding-status"] });
    },
  });
}

export function useConnectWhatsApp() {
  const qc = useQueryClient();
  return useMutation<Business, Error, WhatsAppConnectRequest>({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses/me/whatsapp/connect", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["business"] });
      qc.invalidateQueries({ queryKey: ["onboarding-status"] });
    },
  });
}

export function useOnboardingStatus() {
  return useQuery<OnboardingStatus>({
    queryKey: ["onboarding-status"],
    queryFn: async () =>
      (await api.get("/api/v1/businesses/me/onboarding-status")).data,
  });
}

// ============================================================
// Intents
// ============================================================

export function useGlobalIntents() {
  return useQuery<GlobalIntent[]>({
    queryKey: ["global-intents"],
    queryFn: async () => (await api.get("/api/v1/intents")).data,
  });
}

export function useMyIntents() {
  return useQuery<BusinessIntent[]>({
    queryKey: ["my-intents"],
    queryFn: async () =>
      (await api.get("/api/v1/businesses/me/intents")).data,
  });
}

export function useBulkConfigureIntents() {
  const qc = useQueryClient();
  return useMutation<BusinessIntent[], Error, BusinessIntentsBulkRequest>({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses/me/intents", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["my-intents"] });
      qc.invalidateQueries({ queryKey: ["onboarding-status"] });
    },
  });
}

// ============================================================
// Conversations / Messages
// ============================================================

export function useConversations(
  filter: "all" | "unread" = "all",
  limit = 20,
  offset = 0,
) {
  return useQuery<PaginatedConversations>({
    queryKey: ["conversations", filter, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/conversations", {
          params: { filter, limit, offset },
        })
      ).data,
    refetchInterval: 10_000,
  });
}

export function useConversation(conversationId: string | null) {
  return useQuery<ConversationDetail>({
    queryKey: ["conversation", conversationId],
    queryFn: async () =>
      (await api.get(`/api/v1/conversations/${conversationId}`)).data,
    enabled: Boolean(conversationId),
  });
}

export function useMessages(
  conversationId: string | null,
  limit = 50,
  offset = 0,
) {
  return useQuery<PaginatedMessages>({
    queryKey: ["messages", conversationId, limit, offset],
    queryFn: async () =>
      (
        await api.get(`/api/v1/conversations/${conversationId}/messages`, {
          params: { limit, offset },
        })
      ).data,
    enabled: Boolean(conversationId),
    refetchInterval: 5_000,
  });
}

export function useSendMessage(conversationId: string) {
  const qc = useQueryClient();
  return useMutation<MessageDetail, Error, SendMessageRequest>({
    mutationFn: async (data) =>
      (
        await api.post(
          `/api/v1/conversations/${conversationId}/messages`,
          data,
        )
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["messages", conversationId] });
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}

export function useMarkRead(conversationId: string) {
  const qc = useQueryClient();
  return useMutation<unknown, Error, void>({
    mutationFn: async () =>
      (
        await api.post(`/api/v1/conversations/${conversationId}/mark-read`)
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["conversations"] });
      qc.invalidateQueries({ queryKey: ["conversation", conversationId] });
    },
  });
}

// ============================================================
// Dashboard
// ============================================================

export function useDashboardStats(days = 7) {
  return useQuery<DashboardStats>({
    queryKey: ["dashboard-stats", days],
    queryFn: async () =>
      (await api.get("/api/v1/dashboard/stats", { params: { days } })).data,
    refetchInterval: 30_000,
  });
}

// ============================================================
// Google Sheets sync
// ============================================================

export function useSheets() {
  return useQuery<SheetSync[]>({
    queryKey: ["sheets"],
    queryFn: async () =>
      (await api.get("/api/v1/businesses/me/sheets")).data,
    refetchInterval: 5_000, // poll while syncs are running
  });
}

export function useCreateSheet() {
  const qc = useQueryClient();
  return useMutation<SheetSync, Error, SheetSyncCreate>({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses/me/sheets", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sheets"] });
    },
  });
}

export function useTriggerSheetSync() {
  const qc = useQueryClient();
  return useMutation<unknown, Error, string>({
    mutationFn: async (id) =>
      (await api.post(`/api/v1/businesses/me/sheets/${id}/sync`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sheets"] });
      qc.invalidateQueries({ queryKey: ["my-intents"] });
    },
  });
}

export function useUpdateSheet() {
  const qc = useQueryClient();
  return useMutation<
    SheetSync,
    Error,
    { id: string; data: SheetSyncUpdate }
  >({
    mutationFn: async ({ id, data }) =>
      (await api.patch(`/api/v1/businesses/me/sheets/${id}`, data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sheets"] });
    },
  });
}

export function useDeleteSheet() {
  const qc = useQueryClient();
  return useMutation<unknown, Error, string>({
    mutationFn: async (id) =>
      (await api.delete(`/api/v1/businesses/me/sheets/${id}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["sheets"] });
    },
  });
}

// ============================================================
// Orders (owner dashboard)
// ============================================================

export function useOrders(
  filter: OrderListFilter = "active",
  limit = 20,
  offset = 0,
) {
  return useQuery<PaginatedOrders>({
    queryKey: ["orders", filter, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/businesses/me/orders", {
          params: { filter, limit, offset },
        })
      ).data,
    refetchInterval: 10_000,
  });
}

export function useOrder(orderId: string | null) {
  return useQuery<OrderDetail>({
    queryKey: ["order", orderId],
    queryFn: async () =>
      (await api.get(`/api/v1/businesses/me/orders/${orderId}`)).data,
    enabled: Boolean(orderId),
    refetchInterval: 10_000,
  });
}

export function useUpdateOrderStatus(orderId: string) {
  const qc = useQueryClient();
  return useMutation<OrderDetail, Error, OrderStatusUpdateRequest>({
    mutationFn: async (data) =>
      (
        await api.patch(`/api/v1/businesses/me/orders/${orderId}`, data)
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["orders"] });
      qc.invalidateQueries({ queryKey: ["order", orderId] });
    },
  });
}

// ============================================================
// Fulfillment config (pickup / delivery settings)
// ============================================================

export function useFulfillmentConfig() {
  return useQuery<FulfillmentConfig>({
    queryKey: ["fulfillment-config"],
    queryFn: async () =>
      (await api.get("/api/v1/businesses/me/fulfillment-config")).data,
  });
}

export function useUpdateFulfillmentConfig() {
  const qc = useQueryClient();
  return useMutation<FulfillmentConfig, Error, FulfillmentConfigUpdate>({
    mutationFn: async (data) =>
      (await api.put("/api/v1/businesses/me/fulfillment-config", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["fulfillment-config"] });
    },
  });
}

// ============================================================
// SaaS subscription upgrade
// ============================================================

export function useUpgradePlan() {
  return useMutation<
    { razorpay_subscription_id: string; short_url: string; status: string; plan: string },
    Error,
    { plan: "starter" | "growth" | "pro" }
  >({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses/me/subscription/upgrade", data)).data,
  });
}

export function useCancelSubscription() {
  const qc = useQueryClient();
  return useMutation<unknown, Error, void>({
    mutationFn: async () =>
      (await api.post("/api/v1/businesses/me/subscription/cancel")).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["business"] });
    },
  });
}

export function useEnableAiAddon() {
  const qc = useQueryClient();
  return useMutation<unknown, Error, void>({
    mutationFn: async () =>
      (await api.post("/api/v1/businesses/me/subscription/ai-addon/enable")).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["business"] });
    },
  });
}

export function useDisableAiAddon() {
  const qc = useQueryClient();
  return useMutation<unknown, Error, void>({
    mutationFn: async () =>
      (await api.post("/api/v1/businesses/me/subscription/ai-addon/disable")).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["business"] });
    },
  });
}

// ============================================================
// Account (DPDP: export, delete)
// ============================================================

export async function downloadAccountExport(): Promise<void> {
  const resp = await api.get("/api/v1/account/export", {
    responseType: "blob",
  });
  const url = window.URL.createObjectURL(new Blob([resp.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = `whatsapp-auto-export-${new Date()
    .toISOString()
    .slice(0, 10)}.zip`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export function useDeleteAccount() {
  return useMutation<unknown, Error, void>({
    mutationFn: async () =>
      (
        await api.delete("/api/v1/account/me", {
          params: { confirm: "DELETE" },
        })
      ).data,
  });
}

// ============================================================
// GST settings + Invoices
// ============================================================

export function useGstSettings() {
  return useQuery<GstSettings>({
    queryKey: ["gst-settings"],
    queryFn: async () =>
      (await api.get("/api/v1/businesses/me/gst-settings")).data,
  });
}

export function useUpdateGstSettings() {
  const qc = useQueryClient();
  return useMutation<GstSettings, Error, GstSettingsUpdate>({
    mutationFn: async (data) =>
      (await api.put("/api/v1/businesses/me/gst-settings", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["gst-settings"] });
    },
  });
}

export function useInvoices(
  status: InvoiceStatus | "all" = "all",
  limit = 50,
  offset = 0,
) {
  return useQuery<PaginatedInvoices>({
    queryKey: ["invoices", status, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/businesses/me/invoices", {
          params: { status, limit, offset },
        })
      ).data,
  });
}

export function useInvoice(invoiceId: string | null) {
  return useQuery<Invoice>({
    queryKey: ["invoice", invoiceId],
    queryFn: async () =>
      (await api.get(`/api/v1/businesses/me/invoices/${invoiceId}`)).data,
    enabled: Boolean(invoiceId),
  });
}

export function useCreateInvoice() {
  const qc = useQueryClient();
  return useMutation<Invoice, Error, InvoiceCreate>({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses/me/invoices", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

export function useCancelInvoice(invoiceId: string) {
  const qc = useQueryClient();
  return useMutation<Invoice, Error, { reason: string }>({
    mutationFn: async (data) =>
      (
        await api.post(
          `/api/v1/businesses/me/invoices/${invoiceId}/cancel`,
          data,
        )
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices"] });
      qc.invalidateQueries({ queryKey: ["invoice", invoiceId] });
    },
  });
}

export function useShareInvoice(invoiceId: string) {
  return useMutation<
    { sent: boolean; pdf_url: string },
    Error,
    { to_phone?: string }
  >({
    mutationFn: async (data) =>
      (
        await api.post(
          `/api/v1/businesses/me/invoices/${invoiceId}/share`,
          data,
        )
      ).data,
  });
}

export async function downloadInvoicePdf(
  invoiceId: string,
  invoiceNumber: string,
): Promise<void> {
  const resp = await api.get(
    `/api/v1/businesses/me/invoices/${invoiceId}/pdf`,
    { responseType: "blob" },
  );
  const url = window.URL.createObjectURL(
    new Blob([resp.data], { type: "application/pdf" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = `${invoiceNumber}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

// ============================================================
// Purchase invoices
// ============================================================

export function usePurchaseInvoices(limit = 50, offset = 0) {
  return useQuery<PaginatedPurchaseInvoices>({
    queryKey: ["purchase-invoices", limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/businesses/me/purchase-invoices", {
          params: { limit, offset },
        })
      ).data,
  });
}

export function useCreatePurchaseInvoice() {
  const qc = useQueryClient();
  return useMutation<PurchaseInvoice, Error, PurchaseInvoiceCreate>({
    mutationFn: async (data) =>
      (await api.post("/api/v1/businesses/me/purchase-invoices", data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["purchase-invoices"] });
      qc.invalidateQueries({ queryKey: ["reports-overview"] });
    },
  });
}

export function useDeletePurchaseInvoice() {
  const qc = useQueryClient();
  return useMutation<unknown, Error, string>({
    mutationFn: async (id) =>
      (await api.delete(`/api/v1/businesses/me/purchase-invoices/${id}`)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["purchase-invoices"] });
      qc.invalidateQueries({ queryKey: ["reports-overview"] });
    },
  });
}

// ============================================================
// Tax-filing reports
// ============================================================

export function useReportsOverview(month?: string) {
  return useQuery<ReportsOverview>({
    queryKey: ["reports-overview", month || "current"],
    queryFn: async () =>
      (
        await api.get("/api/v1/businesses/me/reports/overview", {
          params: month ? { month } : undefined,
        })
      ).data,
  });
}

async function _downloadFile(
  path: string,
  filename: string,
  params?: Record<string, string>,
): Promise<void> {
  const resp = await api.get(path, { params, responseType: "blob" });
  const blobType = resp.headers["content-type"] || "application/octet-stream";
  const url = window.URL.createObjectURL(
    new Blob([resp.data], { type: blobType }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export async function downloadSalesRegister(
  from?: string,
  to?: string,
): Promise<void> {
  const params: Record<string, string> = {};
  if (from) params.from = from;
  if (to) params.to = to;
  await _downloadFile(
    "/api/v1/businesses/me/reports/sales-register",
    `sales-register-${from || "month"}.xlsx`,
    params,
  );
}

export async function downloadGstr1(month: string): Promise<void> {
  await _downloadFile(
    "/api/v1/businesses/me/reports/gstr1",
    `gstr1-${month}.json`,
    { month },
  );
}

export async function downloadGstr3b(month: string): Promise<void> {
  await _downloadFile(
    "/api/v1/businesses/me/reports/gstr3b-summary",
    `gstr3b-${month}.xlsx`,
    { month },
  );
}

export async function downloadPurchaseRegister(
  from?: string,
  to?: string,
): Promise<void> {
  const params: Record<string, string> = {};
  if (from) params.from = from;
  if (to) params.to = to;
  await _downloadFile(
    "/api/v1/businesses/me/reports/purchase-register",
    `purchase-register-${from || "month"}.xlsx`,
    params,
  );
}

export async function downloadItr4(fy: string): Promise<void> {
  await _downloadFile(
    "/api/v1/businesses/me/reports/itr4",
    `itr4-pnl-${fy}.xlsx`,
    { fy },
  );
}

// ---- HSN auto-suggest ----

export interface HsnSuggestion {
  code: string;
  desc: string;
  rate: number;
  unit: string;
  score: number;
}

export async function suggestHsn(
  query: string,
  limit = 5,
): Promise<HsnSuggestion[]> {
  if (!query.trim()) return [];
  const resp = await api.get("/api/v1/businesses/me/hsn-suggest", {
    params: { q: query, limit },
  });
  return resp.data.results as HsnSuggestion[];
}

// ---- e-invoice (IRN) ----

export function useGenerateEInvoiceIrn(invoiceId: string) {
  const qc = useQueryClient();
  return useMutation<
    {
      irn: string;
      signed_qr_code: string | null;
      idempotent: boolean;
      ack_no?: string;
      ack_dt?: string;
    },
    Error,
    void
  >({
    mutationFn: async () =>
      (
        await api.post(`/api/v1/businesses/me/invoices/${invoiceId}/einvoice`)
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoice", invoiceId] });
      qc.invalidateQueries({ queryKey: ["invoices"] });
    },
  });
}

export function useEnableTaxPack() {
  const qc = useQueryClient();
  return useMutation<{ tax_pack_enabled: boolean }, Error, void>({
    mutationFn: async () =>
      (
        await api.post("/api/v1/businesses/me/subscription/tax-pack/enable")
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["gst-settings"] });
      qc.invalidateQueries({ queryKey: ["reports-overview"] });
    },
  });
}

export function useDisableTaxPack() {
  const qc = useQueryClient();
  return useMutation<{ tax_pack_enabled: boolean }, Error, void>({
    mutationFn: async () =>
      (
        await api.post("/api/v1/businesses/me/subscription/tax-pack/disable")
      ).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["gst-settings"] });
      qc.invalidateQueries({ queryKey: ["reports-overview"] });
    },
  });
}

// ============================================================
// Admin (superuser only)
// ============================================================

export function useAdminStats() {
  return useQuery<AdminStats>({
    queryKey: ["admin", "stats"],
    queryFn: async () => (await api.get("/api/v1/admin/stats")).data,
    refetchInterval: 30_000,
  });
}

export function useAdminUsers(q: string, limit = 50, offset = 0) {
  return useQuery<AdminPaginated<AdminUserRow>>({
    queryKey: ["admin", "users", q, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/admin/users", {
          params: { q: q || undefined, limit, offset },
        })
      ).data,
  });
}

export function useUpdateAdminUser() {
  const qc = useQueryClient();
  return useMutation<
    AdminUserRow,
    Error,
    { userId: string; data: AdminUserUpdate }
  >({
    mutationFn: async ({ userId, data }) =>
      (await api.patch(`/api/v1/admin/users/${userId}`, data)).data,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
      qc.invalidateQueries({ queryKey: ["admin", "stats"] });
    },
  });
}

export function useAdminBusinesses(q: string, limit = 50, offset = 0) {
  return useQuery<AdminPaginated<AdminBusinessRow>>({
    queryKey: ["admin", "businesses", q, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/admin/businesses", {
          params: { q: q || undefined, limit, offset },
        })
      ).data,
  });
}

export function useAdminSubscriptions(status: string, limit = 50, offset = 0) {
  return useQuery<AdminPaginated<AdminSubscriptionRow>>({
    queryKey: ["admin", "subscriptions", status, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/admin/subscriptions", {
          params: { status: status || undefined, limit, offset },
        })
      ).data,
  });
}

export function useAdminWebhookEvents(source: string, limit = 50, offset = 0) {
  return useQuery<AdminPaginated<AdminWebhookEvent>>({
    queryKey: ["admin", "webhook-events", source, limit, offset],
    queryFn: async () =>
      (
        await api.get("/api/v1/admin/webhook-events", {
          params: { source: source || undefined, limit, offset },
        })
      ).data,
    refetchInterval: 15_000,
  });
}
