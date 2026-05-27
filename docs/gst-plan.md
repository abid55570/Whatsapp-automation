# GST + Invoicing + Tax Filing — comprehensive plan

> **Status:** locked. Week 1 building now. Updates as scope evolves.
> **Decisions:** Full V3 scope · ₹299/mo add-on · WeasyPrint · Cloudflare R2

## Why this matters (revenue lever)

- Every Indian shop with >₹20L turnover = mandatory GST. Most kirana/restaurant/salon owners struggle with monthly GSTR-1 / GSTR-3B filing.
- CAs charge ₹500–₹2000/month for filing prep.
- Bundled into our SaaS = lock-in + price-tier upgrade signal.
- **₹299 "Tax Pack" add-on** → +75% MRR from existing users at near-zero infra cost.
- 30% attach × 100 users = +₹9,000/mo. Blended ARPU ₹704 → ₹794 (+13%).

## Scope phases

| Feature | MVP | V2 | V3 |
|---|---|---|---|
| GST settings per business (GSTIN, state) | ✓ | | |
| GST-compliant invoice PDF | ✓ | | |
| WhatsApp share invoice to CX | ✓ | | |
| Auto tax calc (CGST/SGST/IGST) | ✓ | | |
| HSN/SAC code per product | ✓ | | |
| Monthly sales register Excel | ✓ | | |
| GSTR-1 export (JSON for GST portal) | | ✓ | |
| GSTR-3B summary | | ✓ | |
| Purchase register (B2B inputs) | | ✓ | |
| ITR-4 P&L summary | | | ✓ |
| e-invoice (IRN) for >₹5cr turnover | | | ✓ |
| Monthly CA email automation | | | ✓ |

## Indian GST primer (foundational)

- **GSTIN** = 15-char identifier, state-prefixed
- **CGST + SGST** = intra-state sale (e.g., Delhi→Delhi, 9% + 9% = 18%)
- **IGST** = inter-state sale (Delhi→UP, 18% single)
- **HSN code** = product category. 4-digit if turnover >₹5cr, 6-digit if >₹50cr.
- **SAC code** = services (e.g., 9967 = transport)
- **Composition scheme** = small biz (<₹1.5cr) flat 1%/5%/6%. Different invoice format ("Bill of Supply").
- **Tax slabs** = 0%, 5%, 12%, 18%, 28%
- **GSTR-1** = outward supplies, due 11th next month
- **GSTR-3B** = summary + payment, due 20th next month

## Data model

### Business extensions
```
gstin: str | None              # 15-char, nullable
gst_state_code: str | None     # 2-digit
gst_scheme: Enum["regular", "composition", "unregistered"]
gst_composition_rate: int | None  # 1/5/6 (%)
legal_name: str | None
pan: str | None
business_address_line1, line2, city, state, pincode
invoice_prefix: str             # default "INV"
invoice_seq: int                # auto-increment per FY
fiscal_year_start: date         # default Apr 1
```

### Product extensions
```
hsn_code: str | None
gst_rate: int                  # 0/5/12/18/28
is_service: bool               # → uses SAC
unit: str                       # "kg", "pc", "L", "hr"
```

### New: Invoice
```
id, business_id, order_id?, contact_id?
invoice_number, invoice_date, fiscal_year
# Customer (denormalized — immutable post-issue)
cx_name, cx_phone, cx_gstin?, cx_address?, cx_state_code?
# Amounts in paise
subtotal_paise, discount_paise, taxable_paise
cgst_paise, sgst_paise, igst_paise, cess_paise
round_off_paise, total_paise
# Meta
place_of_supply, reverse_charge, invoice_type
status: draft|issued|paid|cancelled
pdf_url, razorpay_payment_link?, paid_at?
```

### New: InvoiceLine
```
id, invoice_id, line_number
description, hsn_code, quantity (Decimal), unit
rate_paise, discount_pct, gst_rate
taxable_paise, cgst_paise, sgst_paise, igst_paise, total_paise
```

### New: PurchaseInvoice (V2 — for ITC claim)
Same shape as Invoice but for inward supplies.

## Backend services layout

```
app/services/gst/
├── __init__.py
├── calculator.py           # CGST/SGST/IGST tax split
├── invoice_number.py       # FY-aware sequence
├── validation.py           # GSTIN/HSN/PAN regex + checksum
├── pdf_generator.py        # WeasyPrint
├── einvoice.py             # IRN/IRP integration (V3)
├── share.py                # WhatsApp delivery
├── hsn_lookup.py           # fuzzy match by product name
├── templates/
│   ├── invoice.html        # Jinja2
│   ├── invoice.css
│   └── bill_of_supply.html
└── exporters/
    ├── sales_register.py   # xlsx (pandas)
    ├── gstr1.py            # JSON per portal schema
    ├── gstr3b_summary.py   # xlsx
    └── itr4_pnl.py         # xlsx
```

## API endpoints

```
POST   /api/v1/businesses/me/gst-settings
GET    /api/v1/businesses/me/gst-settings

POST   /api/v1/businesses/me/invoices
POST   /api/v1/businesses/me/orders/{id}/invoice
GET    /api/v1/businesses/me/invoices
GET    /api/v1/businesses/me/invoices/{id}
GET    /api/v1/businesses/me/invoices/{id}/pdf
POST   /api/v1/businesses/me/invoices/{id}/share
POST   /api/v1/businesses/me/invoices/{id}/cancel

GET    /api/v1/businesses/me/reports/sales-register?from=&to=&format=xlsx
GET    /api/v1/businesses/me/reports/gstr1?month=YYYY-MM&format=json
GET    /api/v1/businesses/me/reports/gstr3b-summary?month=YYYY-MM&format=xlsx
GET    /api/v1/businesses/me/reports/itr4?fy=YYYY-YY&format=xlsx
```

## Frontend pages

```
/dashboard/invoices                  list + filter
/dashboard/invoices/new              manual create
/dashboard/invoices/[id]             detail + share + cancel + download
/dashboard/reports                   Tax Filing Center
/dashboard/settings/gst              GSTIN, scheme, address
/dashboard/settings/billing          add Tax Pack toggle
```

## WhatsApp integration

Auto on order CONFIRMED:
```
Bot → CX: ✅ Invoice INV-2026-0042 for ₹2,500
         Subtotal: ₹2,118
         GST (18%): ₹382
         📄 Download: https://yourdomain.com/i/abc123
         Pay via UPI: https://rzp.io/i/xyz
```

B2B GSTIN capture flow:
```
Bot: Aap GST registered ho? (yes/no)
CX: yes
Bot: GSTIN bhejo
CX: 27AABCT1234A1Z5
Bot: ✓ B2B invoice ban gaya. Aap ITC claim kar sakte ho.
```

## Pricing matrix

| Plan | Conv | Tax Pack | Price/mo |
|---|---|---|---|
| Trial | 100 | — | ₹0 |
| Starter | 1,000 | optional +₹299 | ₹399 / ₹698 |
| Growth | 3,000 | optional +₹299 | ₹999 / ₹1,298 |
| Pro | 6,000 | optional +₹299 | ₹1,999 / ₹2,298 |
| AI add-on | — | — | +₹699 |

## Compliance requirements

| Requirement | Handling |
|---|---|
| GSTIN validation | 15-char regex + checksum |
| Invoice numbering (sequential, no gaps) | DB sequence per (business, FY); never delete, only cancel |
| Invoice retention 6 years | Soft-delete; archive to S3 IA after 1yr |
| Invoice immutability after issue | status=issued locks fields; cancel = credit note |
| e-invoice (IRN) for >₹5cr | V3 — IRP integration |
| Composition scheme | "Bill of Supply" not "Tax Invoice", swap PDF template |
| Disclaimers | "computer-generated", jurisdiction in PDF |
| Place of supply | Always included on invoice |
| HSN summary | Auto-aggregated in GSTR-1 |

## Env vars (new)

```
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_ENDPOINT=https://<account>.r2.cloudflarestorage.com
R2_BUCKET=whatsapp-auto-invoices
R2_PUBLIC_BASE=https://invoices.yourdomain.com
INVOICE_SIGNED_URL_TTL_DAYS=7

EINVOICE_USERNAME=
EINVOICE_PASSWORD=
EINVOICE_CLIENT_ID=
EINVOICE_CLIENT_SECRET=
EINVOICE_BASE=https://einvapi.charteredinfo.com   # sandbox; live URL later
EINVOICE_GSTIN=<platform GSTIN>

RAZORPAY_PLAN_ID_TAX_ADDON=plan_xxxxx
```

## Effort estimate (solo)

| Week | Tasks | Hours |
|---|---|---|
| 1 | DB migration, models, calc, validation, invoice number, schemas, 20+ tests | 40 |
| 2 | PDF (WeasyPrint), R2 storage, API endpoints, WA share, frontend invoice list/detail | 40 |
| 3 | GSTR-1 JSON, GSTR-3B summary, sales register xlsx, purchase invoices, Reports UI | 40 |
| 4 | ITR-4 P&L, e-invoice IRN, monthly CA email, HSN auto-suggest | 40 |
| 5 | 60+ tests, polish, soft-launch to 5 users | 30 |
| **Total** | | **190 hrs ≈ 5 weeks** |

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| Wrong GST calc → legal trouble | Big T&C disclaimer; recommend CA review; 60+ unit tests for calc engine |
| GSTIN typo → invalid invoice | Real-time regex + checksum + state-code match |
| Wrong place-of-supply (CGST vs IGST) | Default seller_state; require buyer state for B2B |
| Owner cancels invoice → sequence gap | Maintain "cancelled" record, never reuse number; voided stamp |
| Tax rate changes (govt updates) | Rates in DB table, not hardcoded |
| HSN code unknown by owner | Fuzzy match against GST HSN CSV by product name |

## Files to add/modify (preview)

```
backend/
  app/
    models/invoice.py, purchase_invoice.py         NEW
    models/business.py, order.py, product.py       MODIFY
    schemas/invoice.py, gst.py, report.py          NEW
    services/gst/*                                 NEW (10+ files)
    api/v1/invoices.py, reports.py                 NEW
    api/v1/router.py, businesses.py                MODIFY
    workers/tasks/gst.py                           NEW
    core/storage.py                                NEW
  alembic/versions/0009_gst_invoicing.py           NEW
  data/hsn_codes.csv, gst_state_codes.json         NEW
  tests/test_gst/                                  NEW (~80 tests)

frontend/
  app/dashboard/invoices/*, reports/, settings/gst NEW
  lib/queries.ts                                   MODIFY
  types/api.ts                                     MODIFY

docs/gst.md                                        NEW (user how-to)
```
