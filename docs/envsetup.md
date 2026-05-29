# Env Setup — every key, step-by-step

Copy `.env.example` → `.env`. Fill in values below.

```
cp .env.example .env
```

## 1. App basics — already set, no action

```
APP_ENV=development        # set to production on deploy
APP_URL=http://localhost:3000
API_URL=http://localhost:8000
```

## 2. Postgres — local docker, no action

```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/whatsapp_saas
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/whatsapp_saas
```

In prod (managed DB e.g. RDS, Supabase, Neon): replace `postgres:5432` with host:port, set strong password.

## 3. Redis — local docker, no action

```
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

Prod: use Upstash Redis (free tier) or Redis Cloud.

## 4. SECRET_KEY (JWT signing) — REQUIRED

Generate:
```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```
Paste output into `SECRET_KEY=`. **Never commit. Rotate yearly.**

## 5. ENCRYPTION_KEY (Fernet, encrypts WA tokens at rest) — REQUIRED in prod

Generate:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Paste into `ENCRYPTION_KEY=`. Leave empty in dev (falls back to plaintext).

## 6. Meta WhatsApp Cloud API — REQUIRED for production

### Step-by-step
1. Go to https://developers.facebook.com → Login with FB account.
2. **My Apps** → **Create App** → choose **Business** → name "WhatsApp Auto Platform".
3. In app dashboard → **Add Products** → **WhatsApp** → Set up.
4. Copy:
   - `META_APP_ID` (top-right "App ID")
   - `META_APP_SECRET` (Settings → Basic → App Secret → Show)
5. **WhatsApp → API Setup** → copy temporary access token + phone_number_id → for **platform's own WA**:
   - `PLATFORM_WHATSAPP_PHONE_NUMBER_ID=<phone_number_id>`
   - `PLATFORM_WHATSAPP_ACCESS_TOKEN=<token>` (temporary — replace with permanent)
   - `PLATFORM_WHATSAPP_PHONE_NUMBER=+91...` (display number)
6. **WhatsApp → Configuration → Webhooks**:
   - Callback URL: `https://yourdomain.com/api/v1/webhooks/whatsapp`
   - Verify token: invent any random string → set `META_WEBHOOK_VERIFY_TOKEN=<that_string>`
   - Subscribe to fields: **messages**, **message_status**
7. **Embedded Signup** (lets cx connect their WA without leaving our app):
   - https://business.facebook.com/business/loginpage → Business Settings → Apps → Configurations
   - Create Embedded Signup config → copy config_id → `META_EMBEDDED_SIGNUP_CONFIG_ID=<id>`
8. **Graph API version** — leave `META_GRAPH_API_VERSION=v21.0` (auto-updates yearly).

### Permanent access token (for platform's own WA)
Temporary token expires in 24h. Generate System User token (60-day) or permanent:
- Business Settings → Users → System Users → Add → role = Admin
- Generate Token → select WhatsApp Business Management permissions
- Paste into `PLATFORM_WHATSAPP_ACCESS_TOKEN=`

## 7. Razorpay (payments + subscriptions) — REQUIRED for paid plans

### Step-by-step
1. https://razorpay.com → Sign up with business PAN/GST.
2. Dashboard → Settings → **API Keys** → Generate Test Key
3. Copy:
   - `RAZORPAY_KEY_ID=rzp_test_XXX`
   - `RAZORPAY_KEY_SECRET=YYY`
4. **Webhooks** → Add Webhook
   - URL: `https://yourdomain.com/api/v1/webhooks/razorpay`
   - Secret: generate random → set `RAZORPAY_WEBHOOK_SECRET=<that>`
   - Active events: `payment_link.paid`, `payment_link.expired`, `subscription.activated`, `subscription.cancelled`, `subscription.charged`
5. **Subscriptions → Plans** → Create Plan for each tier (do this once via dashboard or API):
   - Starter ₹399/month → copy `plan_xxx` → `RAZORPAY_PLAN_ID_STARTER=plan_xxx`
   - Growth ₹999/month → `RAZORPAY_PLAN_ID_GROWTH=plan_yyy`
   - Pro ₹1999/month → `RAZORPAY_PLAN_ID_PRO=plan_zzz`
   - AI add-on ₹699/month → `RAZORPAY_PLAN_ID_AI_ADDON=plan_www`
6. Switch to **Live mode** when ready → repeat with live keys.

### KYC required
- Submit PAN, bank account, GST (if any).
- Razorpay reviews 24–72h. Until approved, only test mode.

## 8. Google Sheets API — REQUIRED for sheet sync

### Step-by-step
1. https://console.cloud.google.com → Create project "whatsapp-auto-sheets"
2. **APIs & Services → Library** → enable **Google Sheets API** + **Google Drive API**
3. **Credentials → Create Credentials → Service Account**
   - Name: `sheets-sync`, role: none
4. After create → **Keys** tab → **Add Key → JSON** → downloads `service-account.json`
5. Move to `./backend/credentials/google-service-account.json`
6. Set `GOOGLE_SHEETS_CREDENTIALS_PATH=./credentials/google-service-account.json`
7. Copy the service account email (looks like `sheets-sync@xxx.iam.gserviceaccount.com`)
8. **Tell every customer**: "Share your Google Sheet with `sheets-sync@xxx.iam.gserviceaccount.com` as Viewer" — bot can read.

## 9. Email — NOT USED

Whatly sends zero emails. All notifications (signup verification, orders,
invoices, status updates) go via WhatsApp. Owners download GST filing packs
directly from the dashboard and forward to their CA on WhatsApp/their own
email client. No SMTP / Resend / SES setup needed.

## 10. MSG91 / Fast2SMS (SMS fallback) — OPTIONAL

Only if WhatsApp verification fails for cx. Skip until 1000+ users.

```
MSG91_AUTH_KEY=
MSG91_SENDER_ID=WAAUTO
```

## 11. Anthropic Claude (AI add-on) — REQUIRED only for AI tier

1. https://console.anthropic.com → Sign up → Add payment method
2. **API Keys → Create Key** → `ANTHROPIC_API_KEY=sk-ant-xxx`
3. `AI_PROVIDER=anthropic` (default)
4. `AI_MODEL=claude-haiku-4-5` (cheapest, ~₹0.15/reply)

## 12. OpenAI (fallback AI) — OPTIONAL

1. https://platform.openai.com → API Keys → Create → `OPENAI_API_KEY=sk-xxx`
2. Add ₹400 credit. `gpt-4o-mini` ~₹0.10/reply.

## 13. Rate limiting — defaults ok

```
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=120/minute
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_WEBHOOK=2000/minute
```

Tighten in prod under load. Set `RATE_LIMIT_ENABLED=false` in tests.

## 14. Plan limits — defaults are ₹399/999/1999 spec

Don't change unless re-pricing.

## 15. Sentry (error tracking) — OPTIONAL prod

1. https://sentry.io → New Project → Python
2. Copy DSN → `SENTRY_DSN=https://...`

## 15a. Cloudflare R2 (invoice PDF storage) — REQUIRED for Tax Pack

R2 is S3-compatible, no egress fees — ~₹85/mo for 100GB.

1. https://dash.cloudflare.com → Sign up
2. Sidebar → **R2 Object Storage** → enable
3. **Create bucket** → name `whatsapp-auto-invoices`
4. Top-right → **Manage R2 API Tokens** → Create with **Object Read & Write**
5. Copy:
   - Access Key ID → `R2_ACCESS_KEY_ID=...`
   - Secret Access Key → `R2_SECRET_ACCESS_KEY=...`
   - S3 API Endpoint → `R2_ENDPOINT=https://<id>.r2.cloudflarestorage.com`
6. `R2_BUCKET=whatsapp-auto-invoices`
7. (Optional) Custom domain → `R2_PUBLIC_BASE=https://invoices.yourdomain.com`
8. `INVOICE_SIGNED_URL_TTL_DAYS=7`

## 15b. IRP / e-invoice (turnover > ₹5 cr) — OPTIONAL

Required only when an owner crosses ₹5 cr annual turnover.

1. Platform onboards on https://einvoice1.gst.gov.in/Others/APIRegistration
2. After approval, copy:
   - Username → `EINVOICE_USERNAME=...`
   - Password → `EINVOICE_PASSWORD=...`
   - Client ID → `EINVOICE_CLIENT_ID=...`
   - Client Secret → `EINVOICE_CLIENT_SECRET=...`
   - Platform GSTIN → `EINVOICE_GSTIN=...`
3. `EINVOICE_BASE=https://einv-apisandbox.nic.in` (sandbox; switch to `https://einvoice1.gst.gov.in` for prod)

Leave blank to disable — app handles gracefully.

## 15c. Tax Pack Razorpay plan — OPTIONAL

To bill ₹299/mo for Tax Pack via Razorpay:
1. Razorpay → Plans → Create → name "Tax Pack", monthly, ₹299
2. `RAZORPAY_PLAN_ID_TAX_ADDON=plan_xxx`

MVP toggles a DB flag without billing — wire up Razorpay subscription flow in V2.

## 16. Frontend env (separate from backend `.env`)

```
NEXT_PUBLIC_API_URL=http://localhost:8000   # prod: https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME=WhatsApp Auto
NEXT_PUBLIC_RAZORPAY_KEY_ID=rzp_test_XXX    # same as backend KEY_ID, public is fine
```

## Checklist before launch
- [ ] `SECRET_KEY` strong, unique per env
- [ ] `ENCRYPTION_KEY` set in prod (NOT empty)
- [ ] Meta app reviewed + approved by FB
- [ ] Razorpay KYC approved + Live mode
- [ ] Webhook URLs HTTPS (use ngrok in dev: `ngrok http 8000`)
- [ ] Google Service Account file `.gitignored`
- [ ] `.env` `.gitignored`
- [ ] Domain DNS pointed to server (A record)
- [ ] SSL cert (Caddy / Cloudflare auto)
