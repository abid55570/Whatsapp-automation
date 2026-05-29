# Production Deployment — where each container goes

Local docker-compose runs 9 containers. In production you split them by risk
class. Some are public, some private, some never deploy.

## Container summary

| Container | Local role | Production target | Public? |
|---|---|---|---|
| `wa_frontend` | Next.js 15 PWA on :3000 | **Vercel** OR Cloudflare Pages | ✅ Yes |
| `wa_backend` | FastAPI on :8000 | **VPS / Render / Fly.io / Railway** | ✅ Yes (via reverse proxy) |
| `wa_postgres` | Postgres 16 on :5432 | **Neon / Supabase / managed Postgres** | ❌ Private |
| `wa_redis` | Redis 7 on :6379 | **Upstash / Redis Cloud** | ❌ Private |
| `wa_worker` | Celery worker | **Same VPS as backend** (or Render worker) | ❌ Private |
| `wa_beat` | Celery beat scheduler | **Same VPS as backend** (single replica only!) | ❌ Private |
| `wa_flower` | Celery dashboard | **Same VPS, behind auth + IP allowlist** | 🔒 Restricted |
| `wa_adminer` | DB GUI on :8080 | **DO NOT DEPLOY** — use SSH tunnel locally | ❌ Never |

## Recommended production architecture (~₹500/month)

```
         Internet
            │
            ▼
   ┌────────────────┐
   │  Cloudflare    │  ← DNS + SSL + CDN (free)
   │  whatly.in     │
   └────┬───────┬───┘
        │       │
        │       └────────────► Vercel
        │                       (frontend, free Hobby tier)
        │
        ▼
   ┌────────────────────────────────────┐
   │  Hetzner CX22 VPS (₹420/mo)        │
   │  ────────────────────────────────  │
   │  Caddy ─► :8000 backend (FastAPI)  │
   │       └─► :5555 flower (private)   │
   │                                    │
   │  Celery worker + beat (systemd)    │
   │  Loki + Grafana (optional)         │
   └────────────────────────────────────┘
            │
            ├──► Neon free Postgres
            ├──► Upstash free Redis
            └──► Cloudflare R2 (PDFs, free 10 GB)
```

> Whatly sends **zero emails** — all notifications flow through WhatsApp.
> Owners download GST filing packs directly from the dashboard and forward
> them to their CA. No SMTP / SES / Resend setup required.

## 1. Frontend → Vercel (free)

```bash
npm i -g vercel
cd frontend
vercel --prod
```

- Connect domain `whatly.in` → automatic SSL
- Set env var: `NEXT_PUBLIC_API_URL=https://api.whatly.in`
- Bundled CI/CD on every push to main

**Why Vercel:** Next.js native, free tier covers ~100GB bandwidth/month, edge
runtime for icon/og routes works out of the box.

**Alternative:** Cloudflare Pages (free) — same flow, slightly slower SSR cold
starts.

## 2. Backend → Hetzner CX22 VPS (₹420/mo)

One-time provision:
```bash
ssh root@your-server
apt update && apt install -y docker.io docker-compose-plugin git ufw caddy
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw --force enable
git clone <your-repo> /opt/whatly
cd /opt/whatly
cp .env.example .env
nano .env   # fill real prod secrets
```

`Caddyfile`:
```
api.whatly.in {
    reverse_proxy backend:8000
}

flower.whatly.in {
    basicauth {
        admin <hashed-password>
    }
    @internal {
        remote_ip 122.165.0.0/16 49.207.0.0/16   # your home IPs
    }
    handle @internal {
        reverse_proxy flower:5555
    }
    respond 403
}
```

Append to `docker-compose.yml`:
```yaml
  caddy:
    image: caddy:2-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    networks: [wa_network]
```

Then:
```bash
docker compose up -d
docker compose exec backend alembic upgrade head
```

## 3. Postgres → Neon (free, then ₹420/mo at scale)

- https://neon.tech → create project in **AP-Singapore** region (closest to India)
- Copy connection string → `DATABASE_URL=postgresql+asyncpg://user:pw@ep-xxx.aws.neon.tech/db?sslmode=require`
- Also set `SYNC_DATABASE_URL=postgresql+psycopg2://...` for alembic
- Remove `postgres` service from `docker-compose.yml` in prod

**Why managed:** automated backups, point-in-time restore, branching for
testing. Pay-as-you-go starts free.

**Alternative:** Supabase (similar pricing, also includes auth + storage we
don't use).

## 4. Redis → Upstash free tier

- https://upstash.com → create Redis DB → Asia-Pacific
- Copy URL → `REDIS_URL=rediss://default:pw@xxx.upstash.io:6379`
- Same for `CELERY_BROKER_URL` (use a different DB index or same)
- Remove `redis` service from prod compose

Free tier = 10k commands/day — plenty for early users.

## 5. Worker + Beat → same VPS as backend

`docker compose up -d worker beat` on the same Hetzner box.

**Critical rule:** Run **only ONE beat instance**. Multiple beat replicas =
duplicate scheduled tasks (trial freeze fires twice, OTP cleanup duplicates).
Beat is not horizontally scalable. Worker can be scaled freely.

To scale worker only:
```bash
docker compose up -d --scale worker=3
```

## 6. Flower → same VPS, behind auth

Already configured above via Caddy basicauth + IP allowlist. Access:
- Public: https://flower.whatly.in → 401 unless whitelisted IP
- Whitelisted: basic auth prompt

Set basicauth password:
```bash
caddy hash-password
# paste output into Caddyfile
```

**Why restrict:** Flower exposes broker URL, task arguments, and worker
internals — full RCE surface if compromised.

## 7. Adminer → **never deploy to prod**

Adminer = web SQL console. If exposed publicly → instant data breach.

**Use instead:** SSH tunnel from your local machine:
```bash
ssh -L 5432:localhost:5432 root@your-server
# now connect to localhost:5432 with TablePlus / DBeaver
```

OR use Neon's built-in web SQL editor (already authenticated).

OR keep adminer in compose but **bind to 127.0.0.1 only**:
```yaml
adminer:
  ports:
    - "127.0.0.1:8080:8080"   # localhost-only on the VPS
```
Then SSH tunnel: `ssh -L 8080:localhost:8080 root@server`.

## Production `.env` checklist

```env
APP_ENV=production
SECRET_KEY=<64-char random>        # python -c "import secrets; print(secrets.token_urlsafe(64))"
ENCRYPTION_KEY=<Fernet key>        # python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

DATABASE_URL=postgresql+asyncpg://...?sslmode=require    # Neon
SYNC_DATABASE_URL=postgresql+psycopg2://...?sslmode=require

REDIS_URL=rediss://...             # Upstash
CELERY_BROKER_URL=rediss://...

META_APP_ID=<from Meta>
META_APP_SECRET=<from Meta>
META_WEBHOOK_VERIFY_TOKEN=<random>

RAZORPAY_KEY_ID=rzp_live_...       # live mode, not test
RAZORPAY_KEY_SECRET=<live secret>
RAZORPAY_WEBHOOK_SECRET=<random>

R2_ACCESS_KEY_ID=<from CF>
R2_SECRET_ACCESS_KEY=<from CF>
R2_ENDPOINT=https://<account>.r2.cloudflarestorage.com
R2_BUCKET=whatly-invoices
R2_PUBLIC_BASE=https://invoices.whatly.in

SENTRY_DSN=https://...             # error tracking, recommended
LOG_LEVEL=INFO

NEXT_PUBLIC_API_URL=https://api.whatly.in
NEXT_PUBLIC_SITE_URL=https://whatly.in
```

The config validator (`core/config.py:_validate_production_secrets`) refuses
boot if any critical secret is missing or default. Test locally:
```bash
APP_ENV=production python -c "from app.main import app"
```

## Cost summary

| Item | Free tier | Paid (first ~1k users) |
|---|---|---|
| Vercel (frontend) | ✅ 100GB/mo | ₹2,500/mo Pro tier when you need it |
| Hetzner CX22 (backend + worker + beat + flower) | — | ₹420 |
| Neon Postgres | ✅ 0.5 GB / 191 hr compute | ₹1,650 scale tier |
| Upstash Redis | ✅ 10k cmds/day | ₹400 paid |
| Cloudflare R2 storage | ✅ 10 GB / 1 M reads | ₹15 / extra 10 GB |
| Cloudflare DNS + CDN | ✅ Free | — |
| Sentry | ✅ 5k events/mo | ₹2,000 paid |
| Domain `whatly.in` | ₹1,500/yr | — |
| **MVP launch total** | **~₹575/mo** | scales to ~₹6,000 at 1k users |

## CI/CD outline

GitHub Actions (`.github/workflows/deploy.yml`):
```yaml
name: Deploy
on:
  push: { branches: [main] }
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SSH deploy
        run: |
          ssh ${{ secrets.SSH_HOST }} "
            cd /opt/whatly &&
            git pull &&
            docker compose build backend worker beat &&
            docker compose up -d backend worker beat &&
            docker compose exec -T backend alembic upgrade head
          "
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
```

## Monitoring / on-call

- Sentry catches every backend exception → email/Slack alerts
- UptimeRobot hits `https://api.whatly.in/health` every 5 min → SMS if down
- Cloudflare Analytics → traffic graphs
- Flower → real-time Celery task state

When `/health` returns 500 for 5 min → SSH in → `docker compose logs backend | tail -50`.

## Day-1 launch playbook

1. Buy domain `whatly.in` (Namecheap / Cloudflare Registrar, ₹1,500/yr)
2. Cloudflare DNS — A records:
   - `whatly.in` → Vercel
   - `api.whatly.in` → VPS IP
   - `flower.whatly.in` → VPS IP
   - `invoices.whatly.in` → R2 custom domain (optional)
3. Provision Hetzner VPS, install Docker
4. Create Neon DB, copy URL
5. Create Upstash Redis, copy URL
6. Configure Meta WhatsApp Cloud API webhook → `https://api.whatly.in/api/v1/webhooks/whatsapp`
7. Configure Razorpay webhook → `https://api.whatly.in/api/v1/webhooks/razorpay`
8. Push to main → GitHub Actions deploys
9. Run `alembic upgrade head` once
10. Create first superuser
11. Test the full signup → onboarding → bot reply flow end-to-end
