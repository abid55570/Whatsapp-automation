/** TypeScript types matching the backend Pydantic schemas. */

export type BusinessType =
  | "restaurant"
  | "salon"
  | "clinic"
  | "shop"
  | "gym"
  | "coaching"
  | "agency"
  | "d2c"
  | "home_business"
  | "custom";

export type Language =
  | "english"
  | "hindi"
  | "hinglish"
  | "urdu"
  | "bhojpuri"
  | "bengali";

export type PlanType = "trial" | "starter" | "growth" | "pro";

export type SubscriptionStatus =
  | "trialing"
  | "active"
  | "past_due"
  | "canceled"
  | "frozen";

export type OnboardingStep =
  | "create_business"
  | "connect_whatsapp"
  | "configure_intents"
  | "done";

export type MessageDirection = "inbound" | "outbound";

export type MessageStatus =
  | "queued"
  | "sent"
  | "delivered"
  | "read"
  | "failed";

export type ConversationStatus = "open" | "closed";

export type SheetType = "faqs" | "products" | "services" | "customers";

export type OrderStatus =
  | "new"
  | "confirmed"
  | "preparing"
  | "ready_for_pickup"
  | "picked_up"
  | "packed"
  | "out_for_delivery"
  | "delivered"
  | "completed"
  | "canceled";

export type FulfillmentType = "pickup" | "delivery" | "dine_in";
export type OrderListFilter = "all" | "active" | "completed" | "canceled";

export type PickupPrepStrategy = "fixed" | "per_item" | "slots" | "auto";

export interface FulfillmentConfig {
  id: string;
  pickup_enabled: boolean;
  pickup_address: string | null;
  pickup_landmark: string | null;
  pickup_hours_start: string;
  pickup_hours_end: string;
  pickup_closed_days: number[];
  pickup_prep_strategy: PickupPrepStrategy;
  pickup_fixed_minutes: number;
  pickup_per_item_minutes: number;
  pickup_slots: string[];
  delivery_enabled: boolean;
  delivery_fee_paise: number;
  delivery_minimum_order_paise: number;
  delivery_radius_km: number;
  delivery_estimate_minutes: number;
  created_at: string;
  updated_at: string;
}

export type UpgradePlan = "starter" | "growth" | "pro";

export interface UpgradeRequest {
  plan: UpgradePlan;
}

export interface UpgradeResponse {
  razorpay_subscription_id: string;
  short_url: string;
  status: string;
  plan: string;
}

export interface FulfillmentConfigUpdate {
  pickup_enabled?: boolean;
  pickup_address?: string | null;
  pickup_landmark?: string | null;
  pickup_hours_start?: string;
  pickup_hours_end?: string;
  pickup_closed_days?: number[];
  pickup_prep_strategy?: PickupPrepStrategy;
  pickup_fixed_minutes?: number;
  pickup_per_item_minutes?: number;
  pickup_slots?: string[];
  delivery_enabled?: boolean;
  delivery_fee_paise?: number;
  delivery_minimum_order_paise?: number;
  delivery_radius_km?: number;
  delivery_estimate_minutes?: number;
}

export interface OrderContactSummary {
  id: string;
  whatsapp_phone: string;
  name: string | null;
}

export interface OrderItem {
  id: string;
  product_name: string;
  price_paise: number;
  quantity: number;
  subtotal_paise: number;
}

export interface OrderListItem {
  id: string;
  order_number: string;
  status: OrderStatus;
  payment_status: string;
  fulfillment_type: string;
  payment_method: string | null;
  total_paise: number;
  items_count: number;
  pickup_time: string | null;
  created_at: string;
  contact: OrderContactSummary;
}

export interface OrderDetail extends OrderListItem {
  pickup_landmark: string | null;
  pickup_confirmed_at: string | null;
  delivery_estimated_at: string | null;
  delivery_address: Record<string, unknown>;
  notes: string | null;
  razorpay_payment_link_id: string | null;
  razorpay_payment_id: string | null;
  updated_at: string;
  items: OrderItem[];
}

export interface PaginatedOrders {
  items: OrderListItem[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface OrderStatusUpdateRequest {
  status: OrderStatus;
  notes?: string;
}

// ============================================================
// Auth
// ============================================================

export interface User {
  id: string;
  phone: string;
  email: string | null;
  full_name: string | null;
  phone_verified: boolean;
  preferred_language?: string;
  is_superuser?: boolean;
}

export interface StartVerificationRequest {
  phone: string;
  full_name?: string;
}

export interface StartVerificationResponse {
  verification_id: string;
  deep_link: string;
  expires_at: string;
  platform_whatsapp_number: string;
  dev_code?: string | null;
}

export interface VerificationStatusResponse {
  status: "pending" | "verified" | "expired";
  access_token?: string | null;
  token_type?: string | null;
  user?: User | null;
}

// ============================================================
// Business / Subscription
// ============================================================

export interface Subscription {
  plan: string;
  status: string;
  ai_addon_enabled: boolean;
  trial_started_at: string | null;
  trial_ends_at: string | null;
  days_remaining_in_trial: number | null;
  current_period_start: string | null;
  current_period_end: string | null;
  conversations_included: number;
  conversations_used: number;
  conversations_remaining: number;
  ai_replies_included: number;
  ai_replies_used: number;
  ai_replies_remaining: number;
}

export interface Business {
  id: string;
  name: string;
  business_type: string;
  timezone: string;
  languages: string[];
  whatsapp_connected: boolean;
  whatsapp_display_phone: string | null;
  onboarding_completed: boolean;
  created_at: string;
  subscription: Subscription | null;
  intent_count: number;
}

export interface BusinessCreateRequest {
  name: string;
  business_type: BusinessType;
  languages: Language[];
  timezone?: string;
}

export interface WhatsAppConnectRequest {
  phone_number_id: string;
  business_account_id?: string;
  display_phone?: string;
  access_token: string;
}

export interface OnboardingStatus {
  user_exists: boolean;
  business_created: boolean;
  whatsapp_connected: boolean;
  intents_configured: boolean;
  onboarding_completed: boolean;
  next_step: OnboardingStep;
}

// ============================================================
// Intents
// ============================================================

export interface GlobalIntent {
  key: string;
  name: string;
  description: string;
  default_reply_template: string;
  category: string;
  priority: number;
  languages_covered: string[];
  keyword_counts: Record<string, number>;
  emoji_preview: string[];
}

export interface BusinessIntent {
  id: string;
  intent_key: string;
  enabled: boolean;
  reply_text: string;
  reply_translations: Record<string, string>;
  media_url: string | null;
  custom_keywords: string[];
  priority: number;
  name: string | null;
  description: string | null;
  category: string | null;
}

export interface BusinessIntentConfigure {
  intent_key: string;
  enabled?: boolean;
  reply_text: string;
  reply_translations?: Record<string, string>;
  media_url?: string | null;
  custom_keywords?: string[];
  priority?: number;
}

export interface BusinessIntentsBulkRequest {
  intents: BusinessIntentConfigure[];
}

// ============================================================
// Conversations / Messages
// ============================================================

export interface ContactSummary {
  id: string;
  whatsapp_phone: string;
  name: string | null;
  profile_picture_url: string | null;
  tags: string[];
}

export interface MessagePreview {
  id: string;
  direction: MessageDirection;
  body: string | null;
  type: string;
  is_auto_reply: boolean;
  created_at: string;
}

export interface MessageDetail {
  id: string;
  conversation_id: string;
  direction: MessageDirection;
  type: string;
  status: MessageStatus;
  body: string | null;
  media_url: string | null;
  media_mime_type: string | null;
  template_name: string | null;
  is_auto_reply: boolean;
  matched_intent_key: string | null;
  matched_confidence: number | null;
  matched_layer: string | null;
  detected_language: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  read_at: string | null;
  failed_reason: string | null;
  created_at: string;
}

export interface ConversationListItem {
  id: string;
  contact: ContactSummary;
  last_message: MessagePreview | null;
  unread_count: number;
  status: ConversationStatus;
  category: string;
  started_at: string;
  last_message_at: string | null;
  expires_at: string | null;
}

export interface ConversationDetail {
  id: string;
  contact: ContactSummary;
  status: ConversationStatus;
  category: string;
  started_at: string;
  expires_at: string | null;
  last_message_at: string | null;
  unread_count: number;
}

export interface PaginatedConversations {
  items: ConversationListItem[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface PaginatedMessages {
  items: MessageDetail[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface SendMessageRequest {
  body: string;
}

// ============================================================
// Dashboard stats
// ============================================================

// ============================================================
// Google Sheets sync
// ============================================================

export interface SheetSync {
  id: string;
  sheet_url: string;
  sheet_id: string;
  sheet_tab_name: string;
  sheet_type: string;
  auto_sync: boolean;
  sync_interval_minutes: number;
  last_synced_at: string | null;
  last_sync_status: string | null;
  last_sync_error: string | null;
  rows_synced: number;
  created_at: string;
}

export interface SheetSyncCreate {
  sheet_url: string;
  sheet_type: SheetType;
  sheet_tab_name?: string;
  auto_sync?: boolean;
  sync_interval_minutes?: number;
}

export interface SheetSyncUpdate {
  sheet_tab_name?: string;
  auto_sync?: boolean;
  sync_interval_minutes?: number;
}

export interface DashboardStats {
  period_days: number;
  period_start: string;
  period_end: string;
  total_messages: number;
  inbound_messages: number;
  outbound_messages: number;
  auto_replied_count: number;
  needs_attention_count: number;
  unique_contacts: number;
  active_conversations: number;
  conversations_today: number;
  auto_reply_rate: number;
  matched_languages: Record<string, number>;
}

// ============================================================
// GST + Invoicing
// ============================================================

export type GstScheme = "unregistered" | "regular" | "composition";

export type InvoiceStatus = "draft" | "issued" | "paid" | "cancelled";
export type InvoiceType =
  | "b2c"
  | "b2b"
  | "b2c_large"
  | "export"
  | "bill_of_supply";

export interface GstSettings {
  gstin: string | null;
  gst_state_code: string | null;
  gst_scheme: GstScheme;
  gst_composition_rate: number | null;
  legal_name: string | null;
  pan: string | null;
  business_address_line1: string | null;
  business_address_line2: string | null;
  business_city: string | null;
  business_state: string | null;
  business_pincode: string | null;
  invoice_prefix: string;
  invoice_seq: number;
  current_invoice_fy: string | null;
  tax_pack_enabled: boolean;
}

export interface GstSettingsUpdate {
  gstin?: string | null;
  gst_scheme?: GstScheme;
  gst_composition_rate?: number | null;
  legal_name?: string | null;
  pan?: string | null;
  business_address_line1?: string | null;
  business_address_line2?: string | null;
  business_city?: string | null;
  business_state?: string | null;
  business_pincode?: string | null;
  invoice_prefix?: string;
}

export interface InvoiceLine {
  id: string;
  line_number: number;
  description: string;
  hsn_code: string | null;
  quantity: string;
  unit: string;
  rate_paise: number;
  discount_pct: number;
  gst_rate: number;
  taxable_paise: number;
  cgst_paise: number;
  sgst_paise: number;
  igst_paise: number;
  cess_paise: number;
  total_paise: number;
}

export interface Invoice {
  id: string;
  business_id: string;
  order_id: string | null;
  contact_id: string | null;
  invoice_number: string;
  invoice_date: string;
  fiscal_year: string;
  cx_name: string | null;
  cx_phone: string | null;
  cx_gstin: string | null;
  cx_address: string | null;
  cx_state_code: string | null;
  subtotal_paise: number;
  discount_paise: number;
  taxable_paise: number;
  cgst_paise: number;
  sgst_paise: number;
  igst_paise: number;
  cess_paise: number;
  round_off_paise: number;
  total_paise: number;
  place_of_supply: string | null;
  reverse_charge: boolean;
  invoice_type: InvoiceType;
  notes: string | null;
  status: InvoiceStatus;
  issued_at: string | null;
  paid_at: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  pdf_url: string | null;
  razorpay_payment_link: string | null;
  irn: string | null;
  created_at: string;
  lines: InvoiceLine[];
}

export interface InvoiceLineCreate {
  description: string;
  hsn_code?: string | null;
  quantity: string;
  unit?: string;
  rate_paise: number;
  discount_pct?: number;
  gst_rate: number;
}

export interface InvoiceCreate {
  invoice_date?: string | null;
  cx_name?: string | null;
  cx_phone?: string | null;
  cx_gstin?: string | null;
  cx_address?: string | null;
  cx_state_code?: string | null;
  place_of_supply?: string | null;
  reverse_charge?: boolean;
  notes?: string | null;
  lines: InvoiceLineCreate[];
  issue_now?: boolean;
}

export interface PaginatedInvoices {
  items: Invoice[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// ---- Purchase invoices ----

export interface PurchaseInvoice {
  id: string;
  business_id: string;
  supplier_name: string;
  supplier_gstin: string | null;
  supplier_state_code: string | null;
  bill_number: string;
  bill_date: string;
  taxable_paise: number;
  cgst_paise: number;
  sgst_paise: number;
  igst_paise: number;
  cess_paise: number;
  total_paise: number;
  category: string | null;
  is_capital_goods: boolean;
  is_itc_eligible: boolean;
  notes: string | null;
  status: "draft" | "recorded" | "cancelled";
  created_at: string;
}

export interface PurchaseInvoiceCreate {
  supplier_name: string;
  supplier_gstin?: string | null;
  supplier_state_code?: string | null;
  bill_number: string;
  bill_date: string;
  taxable_paise: number;
  cgst_paise?: number;
  sgst_paise?: number;
  igst_paise?: number;
  cess_paise?: number;
  total_paise: number;
  category?: string | null;
  is_capital_goods?: boolean;
  is_itc_eligible?: boolean;
  notes?: string | null;
}

export interface PaginatedPurchaseInvoices {
  items: PurchaseInvoice[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// ---- Reports ----

export interface ReportsOverview {
  period: {
    month: string;
    label: string;
    from: string;
    to: string;
  };
  sales: {
    invoices: number;
    taxable_paise: number;
    cgst_paise: number;
    sgst_paise: number;
    igst_paise: number;
    cess_paise: number;
    total_paise: number;
  };
  purchases: {
    bills: number;
    taxable_paise: number;
    itc_available_paise: number;
  };
  tax_to_pay_paise: number;
  gstin_set: boolean;
  tax_pack_enabled: boolean;
}

// ============================================================
// Admin (superuser)
// ============================================================

export interface AdminStats {
  total_users: number;
  active_users: number;
  superusers: number;
  total_businesses: number;
  onboarded_businesses: number;
  trialing_subs: number;
  active_subs: number;
  frozen_subs: number;
  canceled_subs: number;
  plan_breakdown: Record<string, number>;
  total_orders: number;
  paid_orders: number;
  total_revenue_paise: number;
  webhook_events_24h: number;
}

export interface AdminUserRow {
  id: string;
  phone: string;
  email: string | null;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  phone_verified: boolean;
  preferred_language: string;
  last_login_at: string | null;
  created_at: string;
}

export interface AdminBusinessRow {
  id: string;
  name: string;
  business_type: string;
  owner_user_id: string;
  whatsapp_connected: boolean;
  whatsapp_display_phone: string | null;
  onboarding_completed: boolean;
  created_at: string;
  plan: string | null;
  sub_status: string | null;
}

export interface AdminSubscriptionRow {
  id: string;
  business_id: string;
  plan: string;
  status: string;
  ai_addon_enabled: boolean;
  trial_ends_at: string | null;
  current_period_end: string | null;
  conversations_used: number;
  conversations_included: number;
  razorpay_subscription_id: string | null;
  created_at: string;
}

export interface AdminWebhookEvent {
  id: string;
  source: string;
  event_type: string;
  signature_verified: boolean;
  processed: boolean;
  error: string | null;
  received_at: string;
}

export interface AdminUserUpdate {
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface AdminPaginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}
