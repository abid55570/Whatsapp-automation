# Dev mode — test without Meta WhatsApp credentials

You don't need real Meta WhatsApp Cloud API credentials to develop locally.
The signup → verify flow has a bypass that works offline.

## How it works

When `APP_ENV=development`:

1. **Signup page** (`/signup`) — enter any phone number. The backend creates
   a normal OTP row but **also returns the plaintext code** in the response
   (`dev_code` field). In production this field is null.

2. **Verify page** (`/signup/verify`) — instead of opening WhatsApp to send
   `verify-abc123`, you see a yellow **Dev Mode** panel showing the code
   and a **Simulate** button. Clicking it calls
   `POST /api/v1/auth/dev/simulate-whatsapp-verify` which marks the OTP
   consumed exactly like a real WhatsApp message would.

3. **Polling** — the verify page polls `/auth/verification-status/{id}`
   every 2 sec. Once the OTP is consumed, the response includes the JWT
   access token + the User row → frontend stashes them → redirects to
   `/onboarding/business`.

You're logged in. No Meta. No real phone.

## One-click test signup

Even faster: on `/signup` in dev mode there's a yellow dashed button:

> 🧪 **Dev: signup with random test phone (no Meta needed)**

Click it → fills the form with `Test Owner` + a random `+91 9XXXXXXXXX`
number → auto-submits → lands on `/signup/verify` → tap **Simulate** → done.

Three clicks from a fresh browser to a logged-in dashboard.

## Why random phones?

Each test signup creates a real User row. If you use the same phone twice
in a session the second signup gets `phone already exists`. Random phones
avoid that.

To clean up later:
```sql
-- Run in adminer (http://localhost:8080)
DELETE FROM users WHERE phone LIKE '+919%' AND full_name = 'Test Owner';
```

## Testing inbound messages without Meta webhook

The bot's auto-reply engine is in `app/services/whatsapp/processor.py` →
`process_inbound_message()`. To test it without Meta:

```bash
docker compose exec backend python -c "
import asyncio
from datetime import datetime
from decimal import Decimal
from app.core.database import AsyncSessionLocal
from app.services.whatsapp.processor import process_inbound_message
from app.services.whatsapp.schemas import WAMessage, WAText, WAContact, WAProfile

async def main():
    async with AsyncSessionLocal() as db:
        msg = WAMessage(
            id='wamid.test1', **{'from': '919876543210'},
            timestamp='1700000000', type='text',
            text=WAText(body='kya open hai?'),
        )
        contact = WAContact(wa_id='919876543210', profile=WAProfile(name='Test CX'))
        result = await process_inbound_message(
            db,
            phone_number_id='YOUR_TEST_BIZ_PHONE_NUMBER_ID',
            msg=msg, contact_data=contact,
        )
        print(result)

asyncio.run(main())
"
```

Replace `YOUR_TEST_BIZ_PHONE_NUMBER_ID` with the value you set on a test
Business row when going through onboarding. (In dev, the "Connect
WhatsApp" page accepts any string for `phone_number_id` + `access_token`
since we never actually call Meta.)

## Testing the order flow

After connecting WhatsApp (with fake creds) + configuring intents:

```bash
# Make sure your test business has at least 1 Product in Sheets
docker compose exec backend python -c "
# ... same pattern, send 'do atta, 1 dal' as the body
# ... bot will reply with order cart
"
```

The bot's reply gets persisted as a `Message` row but **isn't sent to
Meta** in dev because the access token is fake. Check the Message table
in adminer to see what would have been sent.

## Skipping the language picker

`/language?next=/signup` redirects to the language picker before signup.
If you want to skip it during dev:

- Set the cookie manually: open devtools → Application → Cookies →
  `locale=en` (or hi/hinglish/etc.)
- Or visit `/signup` directly (the language gate only fires from the
  landing CTA).

## Production behavior

When `APP_ENV=production`:

- `dev_code` is `null` in the API response (so it can't leak to clients)
- `/dev/simulate-whatsapp-verify` returns 403
- The Dev Mode panel + yellow signup button don't render
- The config validator refuses to boot unless real Meta + Razorpay
  secrets are set

## Environment toggle

Set in `.env`:
```env
APP_ENV=development   # bypass works
# OR
APP_ENV=production    # bypass disabled, real Meta required
```

The validator (`core/config.py:_validate_production_secrets`) is strict —
it'll fail boot with a clear list of missing secrets if you try
`APP_ENV=production` with empty `META_APP_SECRET` etc.

## What's still real

Even in dev mode, these are real:
- The database (postgres persists data across restarts)
- Razorpay test mode (if you set test keys, payment links actually work)
- AI add-on (if you set Anthropic/OpenAI keys, real LLM calls happen)
- The bot's matching engine (Hindi/Hinglish/etc. detection — real algos)

Only the **Meta WhatsApp transport layer** is bypassed.
