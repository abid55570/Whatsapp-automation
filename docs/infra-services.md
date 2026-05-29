# Infra services — what each one does + when you actually use it

When you run `docker compose up -d`, you get 8 containers. Here's why each
one exists, when you actually look at it, and what happens if it dies.

## Quick reference

| Container | Port | What it does | You touch it when… | If it dies |
|---|---|---|---|---|
| **postgres** | 5432 | Persistent data store | Never (use adminer / SQL client) | App crashes, customers can't do anything |
| **redis** | 6379 | Job queue + cache | Never | Celery jobs queue up but don't run |
| **backend** | 8000 | FastAPI API | All API calls land here | Frontend shows network errors |
| **frontend** | 3000 | Next.js PWA | Your customers' browsers | Site is down for users |
| **worker** | — | Runs background jobs | Never (monitor via flower) | Order auto-replies stop, sheet syncs stop |
| **beat** | — | Schedules recurring jobs | Never | Trial-freeze cron stops, OTP cleanup stops |
| **flower** | 5555 | Celery dashboard | Debugging stuck/failed jobs | You lose visibility, but workers keep running |
| **adminer** | 8080 | Web SQL client for postgres | Debugging data, manual queries | Just lose the web UI — DB unaffected |

## In detail

### postgres — the brain
Stores **everything**: users, businesses, conversations, messages, orders,
invoices, OTP codes, webhook events. All `await db.execute(...)` in the
backend talks to this.

When you touch it:
- Never directly. Use adminer (dev) or pgAdmin/TablePlus via SSH tunnel
  (prod).
- Daily backups via `pg_dump` cron (see `docs/setup.md` §11).

### redis — the messenger
Three roles:
1. **Celery broker** (`CELERY_BROKER_URL=redis://redis:6379/1`) — when the
   FastAPI app needs to fire a background job (e.g. process incoming
   webhook), it pushes the job here.
2. **Celery result backend** (`CELERY_RESULT_BACKEND=redis://redis:6379/2`)
   — workers write task results here so the API can poll status.
3. **Rate-limit storage** — slowapi uses Redis to enforce per-IP/per-user
   limits across multiple backend replicas.

When you touch it:
- Never. If you want to inspect it: `docker exec -it wa_redis redis-cli`
  then `KEYS *`.

### backend — the API
FastAPI app serving:
- `POST /api/v1/auth/start-verification` etc. (signup)
- `GET /api/v1/businesses/me/orders` (owner dashboard)
- `POST /api/v1/webhooks/whatsapp` (Meta inbound webhook)
- `POST /api/v1/webhooks/razorpay` (payment webhook)
- ... ~70 endpoints in total

When you touch it:
- Every HTTP request from the frontend.
- Logs: `docker compose logs backend -f`
- Auto-reload on code change (we mount `./backend:/app` in dev).

### frontend — the user-facing app
Next.js 15 PWA. Renders the landing page, dashboard, settings, etc.
SSR + client-side hydration. Talks to backend via axios.

When you touch it:
- Every browser tab visiting `whatly.in` (or `localhost:3000` in dev).
- Logs: `docker compose logs frontend -f`
- Hot-reload on code change.

### worker — the muscle (Celery)
Listens on the Redis queue. Picks up jobs and runs them. **Multiple workers
can run in parallel** to handle high load.

Jobs it runs:
- `whatsapp.process_webhook` — every inbound WhatsApp message from Meta
  comes through here (signature verify, save, route to bot)
- `sheets.sync_one` — when owner edits a Google Sheet, this re-fetches +
  updates Products table
- `sheets.sync_all_due` — every 15 min, sync all sheets with auto_sync=true
- `billing.freeze_expired_trials` — hourly, freezes subs whose trial ran out
- `billing.reset_monthly_usage` — hourly, resets conversation counters when
  billing period rolls over
- `account.purge_soft_deleted` — daily, hard-deletes accounts past 30-day
  retention (DPDP compliance)
- `account.cleanup_expired_otps` — daily, drops OTP rows >7 days old

When you touch it:
- Never directly. Monitor via flower at `:5555`.
- Logs: `docker compose logs worker -f` — useful when an auto-reply isn't
  firing.
- Scale: `docker compose up -d --scale worker=3` for 3 worker processes.

### beat — the clock (Celery beat)
The scheduler. Reads the `beat_schedule` dict in `celery_app.py` and
pushes recurring jobs onto Redis at the right time. **Only one beat
instance should run** — multiple beats = duplicate cron firings = double
auto-replies / double trial freezes.

What it schedules:
- Every 15 min: sheet sync
- Every hour: freeze expired trials, reset usage
- Every day: purge soft-deleted, cleanup OTPs

When you touch it:
- Never. If recurring jobs stop running: `docker compose logs beat -f` to
  see if it's emitting schedule ticks.

**Critical:** in production, ensure `--replicas=1` for beat. Worker can
scale freely, beat **cannot**.

### flower — the X-ray (Celery dashboard)
Web UI at `:5555` showing every Celery worker, every task, success/failure
counts, runtime distribution. Without flower you'd be blind to whether
background jobs are healthy.

When you touch it:
- "Why is the bot not replying?" → flower → check if `whatsapp.process_webhook`
  tasks are stuck or failing.
- "Why are sheets not syncing?" → flower → check `sheets.sync_one` last
  success.
- After a deploy → flower → confirm workers reconnected.

URL (dev): http://localhost:5555
URL (prod): https://flower.whatly.in (behind basicauth + IP allowlist —
see `docs/deployment.md` §6).

### adminer — the DB GUI
Web SQL console for postgres at `:8080`. Useful in dev for:
- Inspecting a specific user's data
- Manually fixing a bad row
- Running ad-hoc queries to debug
- Verifying a migration applied correctly

When you touch it:
- "Why does the admin panel say 0 paying users?" → adminer → `SELECT count(*) FROM subscriptions WHERE status='active';`
- "Did my migration add the column?" → adminer → check the schema.

URL (dev): http://localhost:8080 — login: postgres / postgres / whatsapp_saas

**Never deploy to prod.** Use SSH tunnel + local pgAdmin / DBeaver
instead. See `docs/deployment.md` §7.

## What you really need to know

In normal operation, **you'll only ever look at**:
1. **frontend logs** if a UI feature breaks
2. **backend logs** if an API call returns 500
3. **flower** if background jobs misbehave

The rest hum along invisibly. If `docker compose ps` shows all containers
"healthy" / "Up", everything's working.

## Diagram

```
   Browser
      │
      ▼
   frontend (Next.js)  ← hot-reload via volume mount
      │  HTTP /api/v1/*
      ▼
   backend (FastAPI)   ← hot-reload via volume mount
      │           │
      │           └──► postgres (data)
      │
      │  push job
      ▼
   redis (queue) ◄──── beat (scheduler) — fires recurring jobs
      │  pull job
      ▼
   worker (Celery) × N replicas
      │
      └──► postgres (writes results back)
                │
                ├──► flower (read-only view) → :5555
                └──► adminer (read-only view) → :8080
```

## Failure cheat-sheet

| Symptom | Likely cause | Where to look |
|---|---|---|
| Landing page won't load | frontend container down or compilation error | `docker logs wa_frontend` |
| 500 errors in browser | backend container crashed or DB unreachable | `docker logs wa_backend` |
| WhatsApp auto-reply not firing | worker not picking up jobs | flower → see if `whatsapp.process_webhook` is stuck |
| Trials not freezing | beat not running | `docker logs wa_beat` — should see "Scheduler" lines every minute |
| Login button does nothing | frontend can't reach backend (CORS, wrong URL) | browser devtools → Network tab |
| All data missing | postgres volume corrupted or wiped | restore from backup |
| Can't open localhost:3000 | port conflict on host | `netstat -an \| grep 3000` |
