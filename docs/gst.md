# GST + Invoicing — owner's guide

For Indian shopkeepers using **WhatsApp Auto** to handle invoicing, GST filing
prep, and ITR-4 income tax returns.

> Hindi/Hinglish translations follow each English section. हिन्दी अनुवाद नीचे है।

## 1. Should I turn on the Tax Pack?

**English** — Turn it ON if any of these apply:
- You have a GSTIN
- Your monthly turnover > ₹1.5 lakh
- Customers ask you for "GST invoice" / "bill"
- You file GSTR-1 / GSTR-3B monthly

Cost: ₹299/month on top of your Starter/Growth/Pro plan. Cancel anytime.

**Hinglish** — Tax Pack on karein agar:
- Aapke paas GSTIN hai
- Mahine ka ₹1.5 lakh+ ka sale hai
- Customer "GST bill" maangte hain
- Aap monthly GSTR file karte ho

Kharcha ₹299/mahina, kabhi bhi band kar sakte ho.

## 2. One-time setup (5 minutes)

### Step 1 — Enable Tax Pack
Open the app → Settings → **Subscription** → toggle **Tax Pack** ON.

### Step 2 — Enter GST details
Settings → **GST settings**:
- **GSTIN** — paste your 15-character GSTIN. State code auto-detected.
- **GST scheme** — pick:
  - **Regular** (default for most owners)
  - **Composition** (1%/5%/6% flat — if you opted for the scheme)
  - **Unregistered** (turnover under ₹20 lakh — no GSTIN)
- **PAN** — 10-character PAN of the business
- **Legal name** — name on your GST registration (if different from shop name)
- **Address** — exactly as in GST registration certificate
- **Invoice prefix** — default `INV`. Use your initials: `SHM`, `RAM`, etc.

Tap **Save settings**.

## 3. Creating an invoice

Three ways:

### A. Auto from a WhatsApp order
When a customer's order moves to **Confirmed**, an invoice is auto-created and
the PDF is shared on their WhatsApp. No action needed.

### B. Manual — from the dashboard
Settings → **Invoices** → **+ New**:
- Customer name + WhatsApp number (both optional for cash sales)
- For B2B: customer GSTIN (state auto-derived)
- Add items: name, qty, unit, rate. **HSN code auto-fills** when you tab out of the name field (e.g. typing "atta" → HSN 1101).
- Pick GST rate per item (0%, 5%, 12%, 18%, 28%)
- Tap **Issue Invoice**

The PDF downloads + WhatsApp share happens in one tap on the invoice detail page.

### C. From an existing order (if WhatsApp order flow didn't auto-create)
Open the order → tap **Generate Invoice** (link to be added in V2.1).

## 4. Sharing with customer on WhatsApp

Open any invoice → **Send WhatsApp**.

The customer gets a message like:
```
🧾 Invoice INV-26-0042 — Total ₹1,180
Subtotal: ₹1,000
GST: ₹180
📄 Download: https://yourdomain.com/i/abc123
```

PDF link works for 7 days, then auto-refreshes if they tap again.

## 5. e-Invoice (IRN) — for B2B with turnover > ₹5 cr

If your annual turnover crosses ₹5 crore, GST law requires **e-invoicing**
for all B2B invoices.

On any B2B invoice detail page, tap **Generate e-Invoice IRN**.

The app submits to the Government IRP (Invoice Registration Portal) and gets
back a unique IRN + signed QR code. Both are printed on the PDF and persisted.

Once generated, the IRN cannot be changed. If you cancel the invoice you must
also cancel the IRN on the IRP portal (manual step).

**Setup required**: Platform must be onboarded with the IRP. Contact us if
your turnover crosses the threshold and we'll help set it up.

## 6. Monthly filing — GSTR-1 + GSTR-3B

### Tax Filing Center
Settings → **Tax Filing Center**.

Pick the month from the dropdown. You see:
- Sales invoices count + total
- GST collected (CGST + SGST + IGST)
- ITC available (from purchase bills)
- **Net tax to pay** = GST collected − ITC available

### Download GSTR-1 JSON
- Tap **GSTR-1 JSON**
- File downloads. Go to **gst.gov.in → Returns → GSTR-1 → Prepare offline**
- Upload the JSON. Verify totals. Submit.

### Download GSTR-3B summary
- Tap **GSTR-3B Summary**
- Excel file downloads with all sections pre-filled
- Go to **gst.gov.in → Returns → GSTR-3B**
- Copy values from the xlsx into the portal form
- File using DSC / EVC

### Due dates
- **GSTR-1** — 11th of next month (or quarterly via QRMP scheme)
- **GSTR-3B** — 20th of next month
- Late filing fee: ₹50/day + interest on unpaid tax

## 7. Recording purchases (for ITC)

When you receive a supplier bill, record it in the app:

Settings → **Tax Filing Center → Add supplier bills** OR
direct link → **Supplier Bills**:

- Supplier name + GSTIN (if registered)
- Bill number + bill date
- Taxable amount (without GST) in rupees
- CGST + SGST (or IGST for interstate purchases)
- Total
- Category (raw_materials, freight, office, etc.)
- **Capital goods?** check if it's machinery / equipment
- **ITC eligible?** uncheck if expense is personal / blocked

This feeds the **ITC available** number on your monthly dashboard, reducing
your tax payable.

## 8. Annual filing — ITR-4 (Sugam)

For presumptive scheme (turnover < ₹2 cr, mostly small shops):

Tax Filing Center → scroll to **Annual filing** → **ITR-4 P&L**.

Downloads an Excel with 5 sheets:
- **Overview** — gross turnover (cash vs digital), presumed profit @8%/6%
- **Quarterly** — Q1–Q4 totals
- **Monthly Sales** — month-wise breakdown
- **Expenses** — supplier bills by month + category
- **Filing Worksheet** — pre-mapped to ITR-4 fields

Take the xlsx to your CA OR file yourself at **incometax.gov.in → ITR-4**.

## 9. Sharing reports with your CA

Whatly doesn't send emails — you download the filing pack and forward to
your CA the way you prefer (WhatsApp, email, drive link, whatever they use).

Recommended monthly routine:
1. Open **Tax Filing Center**
2. Tap **GSTR-1 JSON** + **GSTR-3B Summary** + **Sales Register**
3. Three files download to your phone
4. WhatsApp them to your CA in one message ("Bhaisahab, last month ke files")

Takes 30 seconds. Your CA gets the same data they'd get from any automation
without you needing to maintain email settings.

## 10. Cancelling an invoice

Open the invoice → scroll to bottom → **Cancel invoice** → enter reason →
**Yes, cancel**.

- The invoice number is NOT reused (GST law)
- The invoice still shows in your records with a "CANCELLED" badge
- It's excluded from GSTR-1, GSTR-3B, and the sales register
- If you already shared the PDF with the customer, send them a polite WhatsApp
  message that the invoice was voided

## 11. Pricing math example (Maharashtra shop, 18% GST)

You sell to a Maharashtra customer (intra-state):
- Item: Atta 10 kg @ ₹500 → ₹5,000
- GST 18% → CGST ₹450 + SGST ₹450
- Total: **₹5,900**
- Customer pays ₹5,900
- You owe govt: ₹450 CGST + ₹450 SGST (after ITC offset from purchases)

You sell to a Delhi customer (interstate):
- Same ₹5,000 item
- GST 18% → IGST ₹900
- Total: **₹5,900**
- You owe govt: ₹900 IGST (single tax)

## 12. Common errors

| Error | Fix |
|---|---|
| "GSTIN not set — configure in Settings → GST" | Settings → GST settings → enter your 15-char GSTIN |
| "Invalid GSTIN — check format + checksum" | GSTIN must be 15 chars: 2-digit state + 10-char PAN + 1-char entity + Z + 1-char checksum. Verify on gst.gov.in. |
| "Cannot remove the last active superuser" | Promote another user first (admin panel) |
| Invoice PDF doesn't show Hindi text | Fonts auto-install in Docker; if running outside Docker, install `fonts-noto-core fonts-indic` |
| GSTR-1 upload fails on portal | Check `gstin` and `fp` fields in the JSON match your registration |
| IRN generation fails — "duplicate invoice" | Same invoice already submitted to IRP. Use the cached IRN. |

## 13. Disclaimer

**WhatsApp Auto computes from your invoices. It is not a tax filing service.
Always verify numbers with your CA before submitting to the GST portal or IRP.**

We are not liable for any miscalculation, missed filing, or penalty arising
from use of this tool. See Terms of Service.

## 14. Hindi — संक्षेप में

- **Tax Pack** = ₹299/mahina add-on
- Settings → **GST settings** → GSTIN daalo
- Invoice automatically banta hai jab order confirm hota hai
- Mahine ke aakhir mein **Tax Filing Center** se GSTR-1 + GSTR-3B download karo
- Government portal pe upload karo, ya CA ko bhejo
- Saalana **ITR-4 P&L** download karo, CA ko de do

Koi bhi dikkat — WhatsApp pe message karo. Quick help milegi.
