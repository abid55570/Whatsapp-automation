# Setup — zero to running app

## Prereqs
- Docker Desktop (Windows/Mac/Linux) — https://docker.com/desktop
- Git
- A free domain (later) — Namecheap / GoDaddy / Cloudflare

## 1. Clone

```bash
git clone <your-repo-url> whatsapp-auto
cd whatsapp-auto
```

## 2. Env

```bash
cp .env.example .env
# Edit .env — see docs/envsetup.md for every key
```

Minimum for local dev (skip Meta/Razorpay/Sheets for now):
```
APP_ENV=development
SECRET_KEY=<generate-with-secrets.token_urlsafe-64>
ENCRYPTION_KEY=                  # leave empty in dev
PLATFORM_WHATSAPP_PHONE_NUMBER=+919999999999
META_WEBHOOK_VERIFY_TOKEN=local-dev-token
```

## 3. Start all services

```bash
docker compose up -d
```

Brings up: postgres, redis, backend (FastAPI), worker (Celery), beat (cron), frontend (Next.js), mailhog, adminer, flower.

Verify:
```bash
docker compose ps
# all should show "running"
```

URLs (local):
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Adminer (DB GUI): http://localhost:8080  (server=postgres, user=postgres, pass=postgres)
- Flower (Celery monitor): http://localhost:5555
- MailHog (caught emails): http://localhost:8025

## 4. Database migration

```bash
docker compose exec backend alembic upgrade head
```

Creates all 16 tables. Re-run on every code pull that ships a new migration.

To create a new migration after model change:
```bash
docker compose exec backend alembic revision --autogenerate -m "your message"
```

Then inspect the new file in `backend/alembic/versions/` before `upgrade head`.

## 5. Create the first superuser

```bash
docker compose run --rm backend python scripts/create_superuser.py \
    --phone "+919876543210" --name "Owner"
```

Then login: visit http://localhost:3000/signup → use that phone → dev simulate verify (in dev mode, code shown in API response).

After signup, superusers see `/admin` link in Settings.

## 6. Install frontend deps (auto-runs in container)

If running frontend outside Docker:
```bash
cd frontend
npm install
npm run dev
```

## 7. Run tests

```bash
# Inside container (recommended)
docker compose run --rm backend pytest

# Or from host with localhost DB
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/whatsapp_saas_test \
SYNC_DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/whatsapp_saas_test \
REDIS_URL=memory:// RATE_LIMIT_ENABLED=false \
python -m pytest tests/ --cov=app
```

Coverage report → `backend/htmlcov/index.html`.

## 8. Logs

```bash
docker compose logs -f backend
docker compose logs -f worker
docker compose logs -f frontend
```

## 9. Reset / wipe

```bash
docker compose down -v          # removes containers + volumes (DATA LOST)
docker compose up -d            # fresh start
docker compose exec backend alembic upgrade head
```

## 10. Production deploy (DigitalOcean / Hetzner / AWS Lightsail)

### One-time
```bash
# On server (Ubuntu 22.04)
ssh root@your-server
apt update && apt install -y docker.io docker-compose-plugin git ufw
ufw allow 22 && ufw allow 80 && ufw allow 443 && ufw --force enable

git clone <repo> /opt/whatsapp-auto
cd /opt/whatsapp-auto
cp .env.example .env
nano .env   # fill real prod keys
```

### Add Caddy reverse proxy (auto-SSL)
Create `Caddyfile` next to `docker-compose.yml`:
```
yourdomain.com {
    reverse_proxy frontend:3000
}
api.yourdomain.com {
    reverse_proxy backend:8000
}
```

Add to `docker-compose.yml`:
```yaml
  caddy:
    image: caddy:2-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    networks: [wa_network]
```

### Run
```bash
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose run --rm backend python scripts/create_superuser.py --phone "+91YOURNUMBER"
```

DNS: point `yourdomain.com` + `api.yourdomain.com` A-records to server IP. Caddy auto-fetches Let's Encrypt cert.

## 11. Backups

Postgres dump daily:
```bash
# Add to crontab on host
0 3 * * * docker exec wa_postgres pg_dump -U postgres whatsapp_saas | gzip > /backup/wa-$(date +\%F).sql.gz
```

Keep last 30 days. Test restore monthly.

## 12. Upgrade

```bash
cd /opt/whatsapp-auto
git pull
docker compose build
docker compose up -d
docker compose exec backend alembic upgrade head
```

Zero-downtime later: deploy 2 backend replicas behind Caddy, rolling restart.

## 13. Troubleshooting

| Symptom | Fix |
|---|---|
| `port 5432 in use` | Local postgres running. `sudo service postgresql stop` or change port in docker-compose. |
| `alembic.command.CommandError: Can't locate revision` | `docker compose exec backend alembic stamp head` then `revision --autogenerate` |
| Frontend can't reach backend | Check `NEXT_PUBLIC_API_URL` — in docker network it's `http://backend:8000`, from browser `http://localhost:8000` |
| Webhook signature fails | `META_WEBHOOK_VERIFY_TOKEN` mismatch. Re-set both sides. |
| Razorpay webhook 401 | `RAZORPAY_WEBHOOK_SECRET` must EXACTLY match dashboard secret. |
