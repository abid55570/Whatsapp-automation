# Share for phone testing — let others open it on their device

Your stack runs on your machine. To let someone test it on **their** phone —
even on mobile data, anywhere — you share a temporary public HTTPS link.

## Why a plain port-forward isn't enough

The frontend (`:3000`) and backend (`:8000`) are two servers. Earlier the
browser called the backend at `http://localhost:8000` directly — on someone
else's phone `localhost` means *their* phone, so every API call died.

**Fixed now:** the frontend proxies `/api/*` to the backend itself
(`next.config.mjs` → `rewrites`). The browser only ever talks to ONE origin.
So we only need to expose **one** port (`3000`) and everything works —
no CORS, no second tunnel.

```
phone ──https──> tunnel ──> frontend:3000 ──/api/*──> backend:8000
                              (same origin)   (internal, server-side)
```

---

## Option A — Public link (any network, recommended)

A Cloudflare "quick tunnel". Free, HTTPS, no account, works over mobile data.
It's already wired into `docker-compose.yml` as the `tunnel` service.

### Start sharing
```bash
docker compose --profile tunnel up -d tunnel
```

### Get the link
```bash
docker compose logs tunnel | grep trycloudflare
```
You'll see something like:
```
https://accessing-proven-soil-joel.trycloudflare.com
```
Send that URL to anyone. They open it on their phone — done.

> The URL is **random every time the tunnel starts**. Restarting the tunnel
> gives a new one.

### Stop sharing
```bash
docker compose stop tunnel
```
The link dies instantly. Your app keeps running locally.

### One-off without editing compose
If you ever want a tunnel without the compose service:
```bash
docker run --rm cloudflare/cloudflared:latest tunnel --url http://host.docker.internal:3000
```

---

## Option B — Same WiFi (fastest, same room)

If the tester is on the **same WiFi**, skip the tunnel and use your PC's LAN IP.

### 1. Find your PC's IP
```powershell
ipconfig | findstr IPv4
# e.g. 192.168.1.42
```

### 2. Allow it through Windows Firewall (first time only)
Docker Desktop usually prompts to allow this. If blocked, allow inbound TCP
on port 3000 for "Private" networks.

### 3. Open on the phone
```
http://192.168.1.42:3000
```
The `/api` proxy makes this Just Work — no env change needed.

> LAN is plain HTTP. Fine for this app. (Camera/mic features would need
> HTTPS, but Whatly's flow doesn't use them.)

---

## Letting a tester sign up (no real WhatsApp)

You're in `APP_ENV=development`, so testers can sign up without Meta:

1. They open the link → **Start free** → pick a language → signup.
2. On signup, the yellow **🧪 Dev: signup with random test phone** button
   fills a random number and submits.
3. On the verify screen, the **Dev Mode** panel shows the code +
   a **Simulate** button → tap it → they're in.

Full detail: `docs/dev-mode.md`.

---

## ⚠️ Security — read before you share a public link

A public tunnel exposes your **dev** server to the internet for as long as
it runs. While it's up:

- **Anyone with the URL can use the dev signup bypass** and create accounts.
  That's the point for testing — just know it's open.
- The link is unguessable but **not authenticated**. Treat it as
  semi-public. Don't post it publicly.
- It points at your **local dev** stack (test data, fake Meta/Razorpay).
  Never tunnel a stack that holds real customer data this way.
- **Stop the tunnel when you're done** (`docker compose stop tunnel`).
  Don't leave it running overnight.

For real external/staging access, deploy properly behind Caddy + a real
domain (see `docs/setup.md` §10) instead of a quick tunnel.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Link shows "Bad Gateway" right after start | Frontend still booting. Wait ~15s, retry. |
| Link works but login/data fails | Confirm `/health` works: open `<link>/health` → should say `{"status":"ok"}`. If 502, backend is down (`docker compose logs backend`). |
| No `trycloudflare.com` line in logs | Tunnel still connecting. `docker compose logs -f tunnel` and wait for the boxed URL. |
| Need a fresh URL | `docker compose restart tunnel` then re-read logs. |
| Page loads but assets look broken over tunnel | Hard-refresh on the phone; Next dev HMR can warn over a tunnel but the app still renders. |
| LAN IP won't load | Windows Firewall blocking 3000 — allow it for Private networks. |
