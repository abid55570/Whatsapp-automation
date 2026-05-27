# User Flow — end to end

Two actors:
- **Owner** = shop owner using our SaaS (the paying customer)
- **Customer** = end-shopper who WhatsApps the shop

## A. Owner signup → first auto-reply (~5 min)

### Step 1 — landing
- Visit `yourdomain.com` on phone
- Sees pricing, demo, "Start free trial" CTA

### Step 2 — phone verify
- Click "Start free trial"
- Enter phone + name
- Page shows **"Verify via WhatsApp"** big green button + deep link
- Tap → opens WhatsApp → "verify-abc123" pre-filled → send to our platform number
- Page polls every 2s — auto-detects verified → user logged in (JWT)

### Step 3 — create business
- Choose business type (kirana/restaurant/salon/clinic/...)
- Pick languages (multi-select: Hindi, Hinglish, English, Bengali, Urdu, Bhojpuri)
- Timezone defaults Asia/Kolkata

Auto-creates: 14-day trial subscription (100 conv), default intent library.

### Step 4 — connect own WhatsApp Business
- Two options:
  - **Embedded Signup** (Meta SDK) — clicks button, Meta-hosted popup, owner picks WA number, code exchanged → done in 30s
  - **Manual** — paste phone_number_id + access_token (for owners who already set up Meta)

### Step 5 — configure intents
- See pre-built intents: greeting, hours, location, menu, price, delivery, COD, holiday, thanks
- Each: enable + edit reply text (or auto-translate via AI add-on)
- Owner edits in their own language; bot uses customer's language at runtime

### Step 6 — done
- Dashboard home: stats + recent inbox
- Bot is live — customers messaging the shop get auto-replies immediately

## B. Customer ↔ Bot conversation

### Greeting / FAQ
```
CX: Namaste kya khula hai?
Bot: हाँ जी, सुबह 9 से रात 10 तक खुले हैं। 🕒
```

### Order intent triggers
```
CX: do atta, ek dal, 2 oil
Bot: 🛒 Order received:
     • Atta 5kg × 2 = ₹500
     • Toor dal 1kg × 1 = ₹150
     • Mustard oil 1L × 2 = ₹360
     Total: ₹1010

     Confirm? (Yes / No)

CX: haan
Bot: 🚶 Pickup details
     ⏰ Ready by 5:00 pm
     📍 Sharma Kirana, Shop 5
     
     Reply YES to confirm, or send a different time (e.g. "6 baje")

CX: yes
Bot: 💳 How to pay?
     online — UPI/card now,  or  cash — at pickup

CX: cash
Bot: ✅ Order #ORD-1042 confirmed!
     📅 Pickup by: 5:00 pm
     💰 Total: ₹1010
     💵 Payment: Cash on pickup
     We'll remind you when it's ready.
```

### Online payment variant
```
CX: online
Bot: ✅ Order #ORD-1042 confirmed!
     💳 Pay now: https://rzp.io/i/abc123
     We'll start once payment received.
```

After Razorpay webhook fires `payment_link.paid` → bot: "Payment received ✓ Preparing your order now."

### Unknown question + AI add-on enabled
```
CX: kya aap free me deliver karte ho?
Bot (no match → AI fallback):
    "Free delivery 1km tak hai bhaiya. Usse zyada par ₹30 charge. 🚲"
```

### Unknown + no AI
- Bot stays silent. Conversation lands in owner's inbox as "needs attention".

## C. Owner managing on phone

### Inbox
- All conversations, unread badge per chat
- Tap → view full thread, reply manually if needed
- 10-second auto-refresh

### Orders
- Pipeline view: New → Confirmed → Preparing → Ready → Picked up
- Tap order → details, customer phone, items, total
- Status update → cx auto-notified on WhatsApp

### Sheet sync (price/menu updates)
- Owner opens Google Sheet on phone
- Edits prices: "Atta 5kg: 250 → 260"
- Saves sheet
- Within 5 min (auto-sync) or instantly (click "Sync now" in app) → bot uses new prices

### Settings
- WhatsApp connection status
- Pickup hours, prep time strategy
- Plan/usage (conversations used vs included)
- Languages
- Privacy: export data ZIP, delete account

## D. Trial → paid conversion

### Day 11 (3 days left)
- App shows banner: "Trial ends Friday. ₹399 to keep auto-replies on."
- Inbox UI dimmed unread count → urgency

### Day 14 (last day)
- Banner becomes red. WA push to owner: "Your trial ends today. Upgrade?"

### Day 15 (expired without paying)
- Subscription status → FROZEN
- Bot stops auto-replying
- Owner sees: "Trial expired. Upgrade to resume." Single big button → Razorpay checkout
- Click → Razorpay subscription → ₹399 mandate
- On `subscription.activated` webhook → status ACTIVE → bot resumes within seconds

## E. AI add-on toggle

- Settings → Subscription → "Enable AI smart-replies — ₹699/mo"
- Toggle on → Razorpay collects ₹699 mandate
- Bot now: matching engine first, AI fallback when miss
- Toggle off any time → reverts to silent-on-miss

## F. Account deletion (DPDP)

- Settings → Privacy → Delete Account
- Warning modal: "30-day retention then full wipe"
- Type "DELETE" → confirm
- Account soft-deleted (phone marked, bot stops)
- Celery beat task wipes after 30 days
