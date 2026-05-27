# Sales Playbook — close + setup on CX phone

Goal: shopkeeper says "haan" → bot live on their WhatsApp → trial activated → in <10 minutes total.

## Pre-visit kit

Carry:
1. Your phone with demo bot ready
2. Printed flyer (Devanagari, see businesspitch.md)
3. A4 paper QR code → links to signup page (already pre-filled tracking ?ref=field)
4. Pen + small notebook
5. Backup hotspot in case shop has no wifi/4G

## The 4-stage CX flow

```
1. Hook (15 sec)     →  attention
2. Demo (60 sec)     →  belief
3. Sign-up (3 min)   →  trial activated
4. Setup (5 min)     →  bot live on their WhatsApp
=================== Total ~10 min ===================
```

## Stage 1 — hook (use businesspitch.md lines)

If they're busy: "1 minute, dukandar bhai. Ek free cheez dikhata hu jo aapke kaam ki ho sakti hai. Pasand na aaye 1 minute me bata dena, chala jaunga."

## Stage 2 — demo on YOUR phone

```
You:  [open WhatsApp, send to demo bot] "kya open ho?"
Bot:  "हाँ जी, 9 बजे से रात 10 तक खुले हैं।"
You:  [send] "do atta ek dal"
Bot:  "🛒 Order: Atta 2 × ₹250, Toor dal 1 × ₹150. Total ₹650. Confirm?"
You:  "haan"
Bot:  "Pickup time 5 baje? Reply yes ya alag time bhejo"
You:  "yes"
Bot:  "Payment: online ya cash?"
You:  "cash"
Bot:  "✅ Order #ORD-42 confirmed. 5 baje ready hoga."
```

Then show your admin dashboard (PWA) on your phone:
- Inbox with that conversation
- Order #ORD-42 in pipeline
- Settings page — point at "Languages" — "Yeh 6 bhashayein samajhta hai"

Pause. Watch their face. If eyes light up → close. If skeptical → repeat with their use case.

## Stage 3 — sign up on CX's phone (3 min)

**Key: do it on THEIR phone so bot lives on their WhatsApp, not yours.**

### Step 3.1 — open signup page on CX phone
- Either: scan your printed QR code with their phone camera
- Or: WhatsApp them the signup link from your phone, they tap it

URL opens to `/signup?ref=field-yourname`

### Step 3.2 — phone + name
- CX enters their business WhatsApp number (the one customers message)
- Name: their shop name (e.g. "Sharma Kirana")

### Step 3.3 — verify via WhatsApp deep link
- Page shows green "Verify via WhatsApp" button + auto-detects WhatsApp installed
- Tap → WhatsApp opens with `verify-abc123` pre-typed → CX taps send to OUR platform number
- Page auto-detects (polling every 2s) → "✓ Verified" → JWT stored → logged in

### Step 3.4 — business type
- Multi-step form, you click for them:
  - Type: pick one (kirana/restaurant/salon/etc.)
  - Languages: ask "Customer Hindi mein likhte hain ya English?" → tap accordingly. Default: Hindi + Hinglish + English.
  - Tap "Create business"

Trial subscription auto-created. 14 days, 100 conv free.

## Stage 4 — connect THEIR WhatsApp Business (5 min, trickiest step)

### Option A — Embedded Signup (preferred, 90% of cx)

1. CX dashboard → "Connect WhatsApp" → big green button
2. Meta-hosted popup opens
3. CX logs in to their Facebook account (most kirana wallahs have FB)
4. Meta asks: "Allow WhatsApp Auto Platform to send/receive messages on behalf of [their biz]?" → Allow
5. CX selects their WhatsApp Business number from dropdown
6. Done — backend exchanges code → access token saved encrypted
7. Page shows: "✅ WhatsApp connected — [+91-XXXXX-XXXXX]"

**If they don't have FB** → Option B.

### Option B — Manual setup (10% of cx, more work)

For owners who have WhatsApp Business app but no FB / haven't migrated to Cloud API.

1. Explain: "Bhaiya, WhatsApp Business app ke alawa, Meta ka Cloud API setup karna hota hai ek baar. Main aapke saath karta hu — 5 min."

2. On your laptop (open it from bag):
   - Go to https://developers.facebook.com/apps → CX logs in with their FB / creates one if needed
   - Use your "Reseller Tool" — a pre-built FB app you own (https://developers.facebook.com/apps/YOUR_APP_ID)
   - Add CX's WhatsApp number as a phone_number in your app
   - Copy phone_number_id + temporary access token

3. Back on CX phone → dashboard → "Connect WhatsApp" → "Manual" tab
   - Paste phone_number_id + access_token
   - Save

**Time-saver: build "Reseller flow" later** — your FB app holds many WA numbers, you onboard them on behalf. Reduces Option B to 2 min.

### Option C — Defer (last resort)

If neither works in 5 min:
- "Bhaiya yeh setup baad mein kar lenge. Aaj inbox + demo dekhte hain. Main kal sham ko aakar 10 min me karwa dunga." → schedule day-2 visit.
- Mark in your CRM "needs WA connect Day 2".
- BUT: trial day 1 already started. Tell them.

## Stage 5 — configure intents (2 min)

1. Dashboard auto-redirects to onboarding step "Configure replies"
2. Pre-built intents shown — all enabled by default with English replies
3. Quick wins (do these 3 in 60 sec):
   - **Hours**: tap "edit" → ask "kab khulta hai aapki dukan?" → type "9 AM se 10 PM"
   - **Location**: ask "address" → type
   - **Menu/price**: skip if they have Google Sheet ready; else tap "skip"
4. Tap "Done"

Bot live. Send a test message from YOUR phone to THEIR WhatsApp to verify:
```
You → CX shop's WA: "open ho?"
Bot replies (on their WA): "हाँ जी, 9 से 10 खुले हैं"
```

CX sees their phone WhatsApp Business app receive + auto-reply. **Magic moment.** Take a photo of their face.

## Stage 6 — Google Sheet setup (optional, defer if time short)

1. "Aapke paas Google account hai?" → if yes:
2. Send them link to "Products Template" Google Sheet — they make a copy
3. Edit Sheet on their phone: product name, price, in stock yes/no
4. Share Sheet with `sheets-sync@xxx.iam.gserviceaccount.com` as Viewer
5. In dashboard → "Sheets" → paste Sheet URL → save
6. Click "Sync now" → bot now uses their menu/prices

If no Google account: "Phone se Google account banao, 30 sec. Phir baad me karenge."

## Stage 7 — close + leave

1. "Bhaiya, 14 din free hai. Customer ke msg ka auto reply chalu hai abhi. Dekhna kal sham — kitne msg auto-handle hue."
2. Set follow-up: schedule a WhatsApp reminder day 7 from your CRM
3. Give them business card + your direct WhatsApp number for support
4. "Koi bhi dikkat — bas mujhe WhatsApp kar dena. Main turant reply karunga."
5. Take signed paper consent (optional but recommended for legal):
   - "Mujhe trial khatam hone ke baad ₹399/mahina ka offer accept hai" — tick yes/no
   - Helps if they later dispute the ₹399 charge

## Post-visit (within 1 hour, same day)

From your phone:
1. WhatsApp message to CX: "Bhaiya namaste 🙏 Aaj setup hua. Yeh aapka dashboard link — bookmark kar lo: yourdomain.com/dashboard. Trial 14 din free, fir ₹399. Kal koi dikkat ho to WA karna."
2. Note in CRM: signup date, plan interest, follow-up dates, language pref

## Common setup failures + recovery

| Problem | Fix |
|---|---|
| WhatsApp verification SMS not received | Switch to Voice OTP option (Meta gives this) |
| FB login fails | Reset password (CX uses "forgot password" — Gmail OTP usually works) |
| Phone_number_id not appearing in Embedded Signup | CX hasn't migrated to Cloud API. Use Option B. |
| Bot doesn't reply during test | Check backend logs `docker compose logs backend | grep webhook` — usually webhook URL wrong in Meta dashboard. Fix and retry. |
| CX panics "customer ko galat reply gaya!" | Disable bot toggle in dashboard, calm them, fix intent text, re-enable |
| 14 days end, CX hasn't paid | Day 13 push reminder + day 15 freeze. If they ignore — call personally day 17. |

## 7-day follow-up message

```
Bhaiya namaste 🙏
Hum 7 din pehle aapki dukan ka WhatsApp Auto laga ke aaye the.
Bot ne kitne msg auto reply kiye, dashboard pe dikh raha hoga.
Koi dikkat? Trial 7 din aur baki hai.
Reply karo to ek 5 min me call ya WA pe baat kar sakte hain.
```

## Day-12 final push

```
Bhaiya, 2 din me trial khatam ho jayega.
Plan select karna ho to abhi kar lo — ₹399 mahina, koi card nahi maangenge, UPI auto-debit se.
Pasand nahi aaya to koi baat nahi — automatic band ho jayega 2 din me.
Reply "haan" agar plan continue rakhna hai.
```

## Goal numbers

- 10 visits/day → 3 setups → 1 paying after trial (worst case)
- 30 visits/week → 9 setups → 3 paying/week → **12 paying/month**

Reach 50 paying in ~5 months at this rate. Beats the worst-case in revenue.md.
