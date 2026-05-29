# Local setup — WITHOUT Docker

Run the whole stack natively. You install + run 4 things yourself that Docker
otherwise gave you for free: **PostgreSQL**, **Redis**, the **FastAPI backend**,
and the **Next.js frontend** (plus 2 Celery processes).

> Prefer Docker? See `docs/setup.md` — it's one command. This guide is for when
> you can't / don't want to run Docker.

You'll end up with ~5 terminals open:

| Terminal | Process | Port |
|---|---|---|
| 1 | Postgres (or run as a service) | 5432 |
| 2 | Redis (or run as a service) | 6379 |
| 3 | Backend — `uvicorn` | 8000 |
| 4 | Celery worker | — |
| 5 | Celery beat (scheduler) | — |
| 6 | Frontend — `npm run dev` | 3000 |

Worker + beat are only needed for background jobs (auto-replies, sheet sync,
trial cron). For pure UI/signup testing you can skip 4 & 5.

---

## 0. Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ (3.12 recommended) | https://python.org/downloads |
| Node.js | 18+ (20 LTS recommended) | https://nodejs.org |
| PostgreSQL | 16 | see below |
| Redis | 7 | see below |
| uv (optional, fast) | latest | `pip install uv` |

---

## 1. PostgreSQL

### Install
- **Windows:** https://www.postgresql.org/download/windows/ (EDB installer). Or `winget install PostgreSQL.PostgreSQL.16`.
- **macOS:** `brew install postgresql@16 && brew services start postgresql@16`
- **Ubuntu/Debian:** `sudo apt install postgresql-16 && sudo systemctl enable --now postgresql`

### Create the database + user
Match the credentials the app expects (`postgres` / `postgres` / `whatsapp_saas`).

```bash
# Open a psql shell as the postgres superuser, then:
psql -U postgres
```
```sql
-- inside psql
ALTER USER postgres WITH PASSWORD 'postgres';
CREATE DATABASE whatsapp_saas;
CREATE DATABASE whatsapp_saas_test;   -- used by pytest
\q
```

> On Windows the EDB installer already creates a `postgres` user — just set its
> password to `postgres` during install (or with the `ALTER USER` above).

Verify:
```bash
psql -U postgres -d whatsapp_saas -c "SELECT 1;"
```

---

## 2. Redis

Redis has no official native Windows build. Pick one:

- **macOS:** `brew install redis && brew services start redis`
- **Ubuntu/Debian:** `sudo apt install redis-server && sudo systemctl enable --now redis-server`
- **Windows — option A (recommended):** run Redis under WSL2:
  ```bash
  wsl --install            # if WSL not set up yet, then reboot
  # inside the WSL Ubuntu shell:
  sudo apt update && sudo apt install -y redis-server
  redis-server             # leave running, or: sudo service redis-server start
  ```
  WSL forwards `localhost:6379` to Windows automatically.
- **Windows — option B:** [Memurai](https://www.memurai.com) (Redis-compatible native Windows service).

Verify:
```bash
redis-cli ping        # → PONG
```

---

## 3. Backend (FastAPI)

```bash
cd backend

# Create + activate a virtualenv
python -m venv .venv
#   Windows (PowerShell):
.venv\Scripts\Activate.ps1
#   Windows (cmd):
.venv\Scripts\activate.bat
#   macOS / Linux:
source .venv/bin/activate

# Install deps (uv is fastest; plain pip also works)
uv pip install -e ".[dev]"
#   or, without uv:
pip install -e ".[dev]"
```

### Environment

The app reads `.env` from the **repo root** (one level up from `backend/`).

```bash
cd ..                 # back to repo root
cp .env.example .env
```

Now edit `.env` and change the Docker hostnames (`@postgres`, `@redis`) to
**`localhost`** — this is the one critical difference from the Docker setup:

```env
APP_ENV=development

# Postgres — note @localhost (NOT @postgres)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_saas
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/whatsapp_saas

# Redis — note @localhost (NOT @redis)
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Required, generate a real one:
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_urlsafe(64))">
ENCRYPTION_KEY=                       # leave empty in dev
META_WEBHOOK_VERIFY_TOKEN=local-dev-token
PLATFORM_WHATSAPP_PHONE_NUMBER=+919999999999
```

You can skip every Meta / Razorpay / R2 key in dev — see `docs/envsetup.md` for
what each one does. `APP_ENV=development` enables the no-WhatsApp signup bypass.

### Migrate the database

```bash
cd backend
alembic upgrade head        # creates all 21 tables
```

> If you skip this you'll get `relation "otp_codes" does not exist` on signup.

### Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Run Celery (separate terminals — only for background jobs)

Activate the same venv in each, from `backend/`:

```bash
# Terminal 4 — worker
celery -A app.workers.celery_app worker --loglevel=info
#   Windows note: add --pool=solo  (prefork doesn't work on Windows)
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```
```bash
# Terminal 5 — beat (scheduler)
celery -A app.workers.celery_app beat --loglevel=info
```

(Want the Flower dashboard too? `celery -A app.workers.celery_app flower --port=5555` → http://localhost:5555)

### Create a superuser (optional)
```bash
cd backend
python scripts/create_superuser.py --phone "+919876543210" --name "Owner"
```

---

## 4. Frontend (Next.js)

```bash
cd frontend
npm install
```

### Environment

Create `frontend/.env.local`:

```env
# Empty = same-origin. Next proxies /api/* to the backend below.
NEXT_PUBLIC_API_URL=
# Where Next forwards /api/* — point at your local backend (NOT backend:8000)
BACKEND_INTERNAL_URL=http://localhost:8000
```

> Why: `next.config.mjs` rewrites `/api/*` → `BACKEND_INTERNAL_URL`. Under
> Docker that defaults to `http://backend:8000`; running natively there is no
> `backend` host, so you must set it to `http://localhost:8000`.

### Run

```bash
npm run dev
```
- Frontend: http://localhost:3000

---

## 5. Verify the whole thing

```bash
# Backend up?
curl http://localhost:8000/health
# → {"status":"ok"}

# Signup works end-to-end (returns dev_code in development)?
curl -X POST http://localhost:3000/api/v1/auth/start-verification \
  -H "Content-Type: application/json" \
  -d '{"phone":"+919876543210","full_name":"Test Owner"}'
# → 201 with "dev_code": "...."
```

Then open http://localhost:3000 → **Start free** → use the dev signup bypass
(`docs/dev-mode.md`).

---

## 6. Run the tests

```bash
cd backend
# Uses the whatsapp_saas_test DB you created in step 1
pytest
```

If `pytest` can't reach the DB, set the test URLs explicitly:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_saas_test \
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/whatsapp_saas_test \
REDIS_URL=memory:// RATE_LIMIT_ENABLED=false \
pytest
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `relation "otp_codes" does not exist` | Run `alembic upgrade head` in `backend/`. |
| `connection refused` to 5432 | Postgres isn't running, or wrong host. Confirm `@localhost` in `.env`. |
| `connection refused` to 6379 | Redis isn't running. `redis-cli ping` should return `PONG`. |
| Frontend loads but login/data 500s | `BACKEND_INTERNAL_URL` not set to `http://localhost:8000` in `frontend/.env.local`. |
| Celery worker crashes on Windows | Add `--pool=solo`. |
| `password cannot be longer than 72 bytes` on signup | Old bcrypt/passlib clash — `pip install -e ".[dev]"` again to get current deps. |
| `ModuleNotFoundError: app` | Run uvicorn/alembic/celery from inside the `backend/` directory with the venv activated. |
| Port already in use | Something else owns 3000/8000/5432/6379. Stop it or change the port. |

---

## How this maps to the Docker setup

| Docker service | Native equivalent |
|---|---|
| `postgres` container | Local PostgreSQL on :5432 |
| `redis` container | Local Redis on :6379 |
| `backend` container | `uvicorn app.main:app` |
| `worker` container | `celery ... worker` |
| `beat` container | `celery ... beat` |
| `frontend` container | `npm run dev` |
| `adminer` | Use `psql`, TablePlus, or DBeaver |
| `flower` | `celery ... flower` (optional) |

The only config difference is hostnames: Docker resolves `postgres` / `redis` /
`backend` over its internal network; running natively you use `localhost`.
