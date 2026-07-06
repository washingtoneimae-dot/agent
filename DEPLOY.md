# Deploying Openfield — Step-by-Step Guide

Three deployment paths, from simplest to most control.

---

## Option 1: Hostinger VPS (Recommended for Production)

Best for: full control, fixed pricing, SSL, custom domain, Docker support.

**Prerequisites:** A Hostinger VPS (any plan with at least 2 GB RAM), Ubuntu 24.04 LTS, a domain pointed to your VPS IP.

### Step 1 — SSH into your VPS

```bash
ssh root@<your-vps-ip>
```

### Step 2 — Install Docker

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker   # or log out and back in
```

### Step 3 — Clone and configure

```bash
git clone https://github.com/washingtoneimae-dot/agent.git /opt/openfield
cd /opt/openfield
cp .env.example .env
nano .env
```

Fill in at minimum:

```ini
DOMAIN=https://yourdomain.com
DB_USER=openfield
DB_PASSWORD=<generate-a-strong-password>
JWT_SECRET=<generate-a-strong-secret>
MINIO_ACCESS_KEY=openfield
MINIO_SECRET_KEY=<generate-a-strong-key>
LETSENCRYPT_EMAIL=you@yourdomain.com
DEBUG=false
```

Optionally add Stripe and AI provider keys for full functionality.

### Step 4 — Start the stack

```bash
docker compose up -d
```

This builds the API and frontend images on first run (~3 minutes), then starts all 6 services (nginx, frontend, API, PostgreSQL, Redis, MinIO).

### Step 5 — SSL with Let's Encrypt

```bash
export DOMAIN=yourdomain.com
export LETSENCRYPT_EMAIL=you@yourdomain.com
bash deploy/init-letsencrypt.sh
```

This obtains free SSL certificates from Let's Encrypt and installs an auto-renewal cron job. After completion, restart nginx:

```bash
docker compose restart nginx
```

### Step 6 — Verify

Visit `https://yourdomain.com`. Register as the first user (auto-admin).

**Maintenance commands:**

```bash
docker compose ps                 # check service status
docker compose logs -f            # tail all logs
docker compose restart api        # restart API only
docker compose down               # stop all services
docker compose up -d --build      # rebuild and restart
git pull && docker compose up -d --build   # update from GitHub
```

### Cost estimate

- Hostinger VPS (2 GB): ~$5-8/month
- Domain: ~$10/year
- SSL: free (Let's Encrypt)
- **Total: ~$6-10/month**

---

## Option 2: Railway (Simplest — No Server Management)

Best for: zero-ops, auto-scaling, managed PostgreSQL.

**Prerequisites:** A [Railway](https://railway.com) account + GitHub connected.

**Important:** Railway does NOT run docker compose natively. You deploy each service individually as a Railway service. For a 6-service Docker Compose stack like Openfield, you need to adapt.

### Step 1 — Install Railway CLI

```bash
npm install -g @railway/cli
railway login
```

### Step 2 — Create a project

```bash
railway init
railway link   # link to a new Railway project
```

### Step 3 — Add PostgreSQL

In the Railway dashboard, add a PostgreSQL database service. Copy the `DATABASE_URL` it provides.

### Step 4 — Deploy the API

In your Railway project, create a new service from your GitHub repo. Point it to the `api/` directory. Set the start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Add environment variables from your `.env.example`, plus the Railway-provided `DATABASE_URL`.

### Step 5 — Deploy the frontend

Create a second service pointing to `frontend/`. Railway auto-detects Node.js + Vite and runs:

```bash
npm run build && npm run preview
```

Or use the build output as a static site with nginx.

### Step 6 — MinIO for file storage

Either:
- Use Railway's volume mount (for dev)
- Use an external S3-compatible service (AWS S3, Cloudflare R2, Backblaze B2) and point MinIO env vars there
- Add MinIO as a separate Railway service with a mounted volume

### Step 7 — Wire services together

In Railway, each service gets an internal hostname. Update your API's environment:

```ini
DATABASE_URL=postgresql+asyncpg://<railway-pg-url>
REDIS_URL=redis://<railway-redis-host>:6379/0
MINIO_ENDPOINT=<minio-service-host>:9000
```

### Step 8 — Deploy

```bash
railway up
```

### Cost estimate

- Railway: ~$5-20/month (usage-based, scales with traffic)
- Managed Postgres included in plan
- No SSL/config overhead

---

## Option 3: Why NOT Vercel + What to Use Instead

**Vercel does not support Docker Compose, PostgreSQL, Redis, MinIO, or any persistent services.** It's designed for serverless frontend apps and short-lived functions. Openfield's 6-service Docker stack (FastAPI + React + Postgres + Redis + MinIO + nginx) fundamentally doesn't fit.

If you want a Vercel-like experience but for full-stack Docker apps, use one of these:

### Render (recommended Vercel alternative)

[Render](https://render.com) supports Docker, native backends, managed PostgreSQL, Redis, cron jobs, and private networking.

1. Create a Render account, link GitHub
2. Add a PostgreSQL database (managed)
3. Add a Redis instance (managed)
4. Create a "Web Service" from your repo — choose Docker
5. Set `Dockerfile Path` to `api/Dockerfile`
6. Add environment variables from `.env.example`
7. Create a "Static Site" from `frontend/` — build command `npm run build`, publish directory `dist`
8. Wire the frontend to the API's Render URL

**Cost:**
- Render: free tier available, Pro $19/user/month
- Managed Postgres: starts at ~$7/month
- Managed Redis: starts at ~$7/month

### Fly.io

[Fly.io](https://fly.io) runs Docker containers on a global edge network with managed Postgres.

1. Install `flyctl` CLI
2. `fly launch` from the repo root
3. `fly postgres create` for the database
4. `fly redis create` for Redis
5. Set secrets via `fly secrets set`
6. `fly deploy`

**Cost:** ~$5-15/month for a small app.

### Dokploy (self-hosted, open-source)

[Dokploy](https://dokploy.com) is an open-source Vercel alternative you run on your own VPS.

1. On your VPS: `curl -sSL https://dokploy.com/install.sh | sh`
2. Access the Dokploy dashboard
3. Connect your GitHub repo
4. Dokploy reads your `docker-compose.yml` and deploys everything
5. Automatic SSL, custom domains, one-click deploys

**Cost:** just the VPS (~$5-8/month)

---

## Quick Comparison

| Platform | Docker Compose | Managed DB | SSL | Monthly Cost | Best For |
|---|---|---|---|---|---|
| **Hostinger VPS** | Yes | DIY | Manual | $5-10 | Full control |
| **Dokploy on VPS** | Yes | DIY | Auto | $5-8 | Vercel-like on VPS |
| **Railway** | Partial | Yes | Auto | $5-20 | Zero-ops |
| **Render** | Yes | Yes | Auto | $7-30 | Managed full-stack |
| **Fly.io** | Yes | Yes | Auto | $5-15 | Global edge |
| **Vercel** | No | No | N/A | N/A | Doesn't fit |

---

## Production Checklist

Before going live, ensure:

- [ ] Set `DEBUG=false` in `.env`
- [ ] Generate strong `JWT_SECRET` (minimum 32 random characters)
- [ ] Generate strong `DB_PASSWORD`
- [ ] Generate strong `MINIO_SECRET_KEY`
- [ ] Configure Stripe keys (or users get mock payment mode)
- [ ] Configure an AI provider key (OpenRouter recommended)
- [ ] Set `DOMAIN` to your actual HTTPS URL
- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall allows only ports 80 and 443
- [ ] Regular database backups configured
- [ ] Set up monitoring (e.g., UptimeRobot for a free health check ping to `/api/v1/health`)

---

## The Quickest Path to Live

For most users, the fastest way to production:

1. Buy a $5/month Hostinger VPS (Ubuntu 24.04)
2. Point your domain's A record to the VPS IP
3. Run the 3 commands from Option 1 Steps 1-4
4. Run the SSL script from Step 5
5. You're live in under 30 minutes

Already included in the repo:
- `deploy/setup.sh` — one-click deploy/update script
- `deploy/init-letsencrypt.sh` — SSL certificate setup
- `docker-compose.yml` — full 6-service production stack
- `Makefile` — `make deploy`, `make build`, `make reset`, `make logs`
